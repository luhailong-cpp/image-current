"""Read-only checks of expected static exports and their evidence chains."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate_overview(filename, manifest_slugs, require_complete=False):
    """Check one existing review sheet and all sources named by its sidecar."""
    path = ROOT / filename
    meta = read(Path(str(path) + ".derived.json"))
    if meta["file"] != filename or digest(path) != meta["sha256"]:
        raise ValueError("Overview file or hash mismatch")
    with Image.open(path) as image:
        image.load()
        if image.size != (meta["width"], meta["height"]) or image.format != "PNG":
            raise ValueError("Overview dimensions or format differ from its sidecar")
    expected_count = meta.get("expectedPetCount")
    if not isinstance(expected_count, int) or expected_count < 1:
        raise ValueError("Overview expectedPetCount must be a positive integer")
    requested = Path(filename).name.startswith("requested-")
    if requested:
        request_record = meta.get("requestedRoster", {"file": "records/requested-roster.json"})
        request_path = ROOT / request_record["file"]
        selection = read(request_path)
        expected_slugs = selection["slugs"]
        if request_record.get("sha256") and digest(request_path) != request_record["sha256"]:
            raise ValueError("Overview has a stale requested roster")
    else:
        expected_slugs = manifest_slugs
    if not isinstance(expected_slugs, list) or not expected_slugs or not all(isinstance(slug, str) for slug in expected_slugs):
        raise ValueError("Overview roster must be a nonempty list of slug strings")
    if len(set(expected_slugs)) != len(expected_slugs) or any(slug not in manifest_slugs for slug in expected_slugs):
        raise ValueError("Overview roster contains duplicate or unknown slugs")
    if expected_count != len(expected_slugs):
        raise ValueError("Overview expectedPetCount differs from the current roster")
    if meta.get("rosterSlugs", expected_slugs) != expected_slugs:
        raise ValueError("Overview ordered roster differs from its current definition")
    portrait = filename.endswith("portrait-roster.png")
    paired = filename.endswith("EW-roster.png")
    directions = ("E", "W") if paired else (None,) if portrait else ("E",)
    seen = set()
    for source in meta["derivedFrom"]:
        pet = source["pet"]
        direction = source.get("direction") if not portrait else None
        key = (pet, direction)
        if pet not in expected_slugs or direction not in directions or key in seen:
            raise ValueError("Overview contains an unexpected or duplicate source")
        seen.add(key)
        expected_file = f"ui/{pet}/portrait_512.png" if portrait else f"runtime/{pet}/idle_{direction}.png"
        if source["file"] != expected_file or digest(ROOT / source["file"]) != source["sha256"]:
            raise ValueError("Overview has stale or unexpected source artwork")
        if source["derivedRecord"] != expected_file + ".derived.json":
            raise ValueError("Overview source points to an unexpected derived record")
        derived = read(ROOT / source["derivedRecord"])
        if derived["file"] != source["file"] or derived["sha256"] != source["sha256"]:
            raise ValueError("Overview source derived-record hash mismatch")
    available = sum(all((slug, direction) in seen for direction in directions) for slug in expected_slugs)
    if meta.get("availablePetCount") != available:
        raise ValueError("Overview availablePetCount differs from its recorded sources")
    if require_complete and len(seen) != expected_count * len(directions):
        raise ValueError("Overview does not contain the complete expected roster")
    return {"file": filename, "checks": "passed", "expectedPetCount": expected_count,
            "availablePetCount": available, "checkedSourceCount": len(seen)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    manifest = read(ROOT / "manifest.json")
    errors, pending, checked, source_records = [], [], [], {}
    checked_overviews = []
    expected_count = manifest.get("expectedPetCount", len(manifest["pets"]))
    if len(manifest["pets"]) != expected_count:
        pending.append({"slug": None, "missingPetDefinitions": expected_count - len(manifest["pets"])})
    for pet in manifest["pets"]:
        expected = {"idle_E", "idle_W", "fullbody_1024", "portrait_512"}
        missing = sorted(expected - set(pet.get("outputs", {})))
        if missing:
            pending.append({"slug": pet["slug"], "missingOutputs": missing})
        for key, item in pet.get("outputs", {}).items():
            path = ROOT / item["file"]
            try:
                meta = read(ROOT / item["record"])
                actual_sha = digest(path)
                if actual_sha != meta["sha256"] or actual_sha != item["sha256"]:
                    raise ValueError("Export hash mismatch")
                with Image.open(path) as im:
                    im.load()
                    expected_size = (512, 512) if key == "portrait_512" else (1024, 1024)
                    if im.mode != "RGBA" or im.size != expected_size:
                        raise ValueError("Unexpected image mode or dimensions")
                    alpha = im.getchannel("A")
                    if alpha.getextrema()[0] != 0 or alpha.getbbox() is None:
                        raise ValueError("Missing true transparency or empty image")
                    if key.startswith("idle_"):
                        x0, y0, x1, y1 = alpha.getbbox()
                        if min(x0, y0) <= 0 or x1 >= im.width or y1 >= im.height:
                            raise ValueError("Runtime alpha touches the frame edge")
                        if meta["runtimePivotBottomOrigin"] != [0.5, 0.08]:
                            raise ValueError("Unexpected foot pivot")
                        if meta["sharedScale"] != pet["sharedScale"]:
                            raise ValueError("E/W shared-scale contract differs")
                if meta.get("upscaled") is True or meta.get("scale", 1) > 1 or meta.get("sharedScale", 1) > 1:
                    raise ValueError("Upsampling detected")
                for source in meta["derivedFrom"]:
                    source_path = ROOT / source["file"]
                    generation_path = ROOT / source["generationRecord"]
                    generation = read(generation_path)
                    if digest(source_path) != source["sha256"] or source["sha256"] != generation["sha256"]:
                        raise ValueError("Source generation chain hash mismatch")
                    if min(generation["width"], generation["height"]) < 1024:
                        raise ValueError("Native source below minimum resolution")
                    if not isinstance(generation.get("generatedAt"), str):
                        raise ValueError("Generation timestamp is unavailable or malformed")
                    archive = ROOT / generation["immutableNativeArchive"]
                    if digest(archive) != generation["sha256"]:
                        raise ValueError("Preserved native archive differs from its generation record")
                    if not generation.get("prompt") or not generation.get("references"):
                        raise ValueError("Generation prompt or reference evidence missing")
                    for reference in generation.get("references", []):
                        ref = reference.get("path", "") if isinstance(reference, dict) else reference
                        normalized = str(ref).replace("\\", "/").lower()
                        if "pets-20260924/" in normalized or "codex-clipboard" in normalized:
                            raise ValueError("Rejected candidate or external game screenshot used as an original-design generation reference")
                    if not generation.get("toolSource"):
                        raise ValueError("Tool result-file source missing")
                    source_records[source["file"]] = {"file": source["file"], "sha256": source["sha256"], "nativeSize": [generation["width"], generation["height"]], "actualModel": generation["actualModel"], "actualQuality": generation["actualQuality"], "generationRecord": source["generationRecord"]}
                checked.append({"file": item["file"], "sha256": actual_sha, "checks": "passed"})
            except Exception as error:
                errors.append({"file": item["file"], "error": str(error)})
    manifest_slugs = [pet["slug"] for pet in manifest["pets"]]
    for prefix in ("", "requested-"):
        for stem in ("E-roster", "EW-roster", "portrait-roster"):
            filename = f"previews/{prefix}{stem}.png"
            path = ROOT / filename
            if not path.exists() and not Path(str(path) + ".derived.json").exists():
                continue
            try:
                checked_overviews.append(validate_overview(filename, manifest_slugs, args.require_complete))
            except Exception as error:
                errors.append({"file": filename, "error": str(error)})
    if args.require_complete and pending:
        errors.append({"file": "manifest.json", "error": "Incomplete expected static asset set"})
    previous = read(ROOT / "records/technical-validation.json") if (ROOT / "records/technical-validation.json").exists() else {}
    report = {"schemaVersion": 1, "status": "passed" if not errors else "failed", "allExpectedStaticExportsPresent": not pending, "expectedPetCount": expected_count, "checkedOutputCount": len(checked), "checkedSourceCount": len(source_records), "checkedOverviewCount": len(checked_overviews), "overviews": checked_overviews, "outputs": checked, "sources": list(source_records.values()), "pending": pending, "errors": errors, "visualApproval": False, "clientIntegrated": False, "animation": False, "scope": "PNG dimensions, alpha, clipping, no-upscale, paired shared scale, hashes, generation and derived evidence; does not grant visual or engine acceptance", "deterministicRebuild": previous.get("deterministicRebuild"), "originalityReview": manifest.get("originalityReview", "pending"), "referencePolicy": "Rejected candidates and external-game clipboard screenshots are forbidden generation references; visual identity review remains manual"}
    target = ROOT / "records/technical-validation.json"
    raw = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if not target.exists() or target.read_bytes() != raw:
        target.write_bytes(raw)
    print(json.dumps({k: v for k, v in report.items() if k not in ("outputs", "sources")}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
