"""Plan image cleanup after a verified export; NEVER delete or modify images.

Run this file after export + delivery preview generation. It writes only
<character>/cleanup-plan.json, prints a summary, and exits 0 when guards pass
or 2 when blocked. No approval status is written. No directories outside BASE
are enumerated. External candidates are exact receipt paths in explicitly allowlisted
host generation directory, read only when their recorded source SHA matches.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image

BASE = Path(__file__).resolve().parents[1]
APPROVED_BASE = Path(
    "D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/"
    "characters/17_ghost_script_calligrapher_boy"
).resolve()
# Exact thread roots observed in this character's full-body revision receipts
# (including actual edit ancestors). This is not a generated_images-wide grant.
EXTERNAL_ROOTS = tuple(Path("C:/Users/luyua/.codex/generated_images") / thread for thread in (
    "01a0f77a-fb47-7bd0-8402-cf6df9512a1c",  # root / cast W
    "01a10114-831b-7c12-8a91-0c9cb2d89709",  # run E 04-07
    "01a10115-2b8e-7a52-8634-77f1edef65cb",  # run E 08-11 / combat
    "01a10114-f91d-77b2-8a6b-4a2081aed2a5",  # run W / hit W
))
KEEP_PREVIEW = BASE / "preview" / "run-current-960ms.webp"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".bmp"}
ACTIONS = {
    "run": (("N", "NE", "E", "SE", "S", "SW", "W", "NW"), 16, 60),
    "hit": (("E", "W"), 6, 40),
    "attack": (("E", "W"), 12, 30),
    "cast": (("E", "W"), 16, 45),
}
EXPECTED = {
    f"{a}-{d}-{n:02d}": (a, d, n, ms)
    for a, (ds, count, ms) in ACTIONS.items()
    for d in ds for n in range(1, count + 1)
}


class GuardError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise GuardError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def inside(path, root=BASE):
    return path.resolve().is_relative_to(root.resolve())


def local(raw, folder=BASE):
    require(isinstance(raw, str) and raw, "Missing local path")
    p = Path(raw)
    p = (p if p.is_absolute() else folder / p).resolve()
    require(inside(p), f"Path escapes character directory: {raw}")
    return p


def runtime_path(raw, folder=BASE):
    p = local(raw, folder)
    require(inside(p, BASE / "runtime") and p.suffix.lower() == ".png",
            f"Not an in-character runtime PNG: {raw}")
    return p


def frame_reference(raw):
    require(isinstance(raw, str), "Non-string delivery image reference")
    u = urlsplit(raw)
    require(not u.scheme and not u.netloc and not u.query and not u.fragment,
            f"Delivery frame reference must be a plain local path: {raw}")
    return runtime_path(unquote(u.path), BASE / "preview")


def png_info(path, size=None):
    with Image.open(path) as im:
        im.load()
        require(im.format == "PNG" and im.mode == "RGBA", f"Not PNG RGBA: {path}")
        require(im.width == im.height and im.width >= 1024,
                f"Invalid native square size: {path} {im.size}")
        if size:
            require(im.size == size, f"Wrong runtime canvas: {path} {im.size}")
        lo, hi = im.getchannel("A").getextrema()
        require(lo == 0 and hi > 128, f"No valid transparent character pixels: {path}")
        return list(im.size)


class DeliveryHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.data_blocks = []
        self.capture_data = False
        self.resources = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("id") == "data":
            require(attrs.get("type") == "application/json", "HTML #data is not JSON")
            self.data_blocks.append("")
            self.capture_data = True
        for key in ("src", "href", "poster"):
            if attrs.get(key):
                self.resources.append((tag, key, attrs[key]))
        require(not attrs.get("srcset"), "Unexpected srcset in delivery HTML; inspect manually")
        if tag == "base":
            raise GuardError("Unexpected <base> in delivery HTML")

    def handle_endtag(self, tag):
        if tag == "script":
            self.capture_data = False

    def handle_data(self, data):
        if self.capture_data:
            self.data_blocks[-1] += data


def validate_export():
    manifest_file = BASE / "manifest.json"
    require(manifest_file.is_file(), "manifest.json absent: export is not ready")
    manifest = read_json(manifest_file)
    require(manifest.get("character") == BASE.name, "Manifest character mismatch")
    require(manifest.get("canvas") == [1024, 1024], "Manifest canvas must be 1024 square")
    groups = manifest.get("sequences")
    require(isinstance(groups, list) and len(groups) == 14, "Expected 14 sequences")
    by_slot, runtime_files, source_checks = {}, set(), []
    for group in groups:
        action, direction = group.get("action"), group.get("direction")
        require(action in ACTIONS, f"Unexpected action: {action}")
        ds, count, ms = ACTIONS[action]
        require(direction in ds and group.get("count") == count,
                f"Invalid sequence: {action}/{direction}")
        require(group.get("ms") == ms and group.get("cycleMs") == count * ms,
                f"Stale timing in {action}/{direction}")
        frames = group.get("frames")
        require(isinstance(frames, list) and len(frames) == count, "Sequence frame count mismatch")
        for frame in frames:
            slot = frame.get("slot")
            require(slot in EXPECTED and slot not in by_slot, f"Unexpected or duplicate slot: {slot}")
            a, d, n, expected_ms = EXPECTED[slot]
            require((action, direction, frame.get("frame"), frame.get("durationMs")) ==
                    (a, d, n, expected_ms), f"Frame identity/timing mismatch: {slot}")
            expected_rel = f"runtime/{a}/{d}/{n:02d}.png"
            p = runtime_path(frame.get("file"))
            require(p == local(expected_rel), f"Unexpected runtime location: {slot}")
            require(p.is_file() and digest(p) == frame.get("sha256"),
                    f"Runtime SHA mismatch or missing: {slot}")
            png_info(p, (1024, 1024))
            generation = frame.get("generationRecord", {})
            receipt_path = local(generation.get("file"))
            require(receipt_path == p.with_suffix(".png.generation.json"),
                    f"Wrong runtime generation-record path: {slot}")
            require(receipt_path.is_file() and digest(receipt_path) == generation.get("sha256"),
                    f"Runtime generation-record SHA mismatch: {slot}")
            receipt = read_json(receipt_path)
            require(receipt == generation.get("record"), f"Manifest/receipt content mismatch: {slot}")
            require(receipt.get("file") == expected_rel and
                    receipt.get("sha256") == frame["sha256"] and
                    (receipt.get("width"), receipt.get("height"), receipt.get("mode")) ==
                    (1024, 1024, "RGBA"), f"Runtime receipt identity mismatch: {slot}")
            require(receipt.get("transform") == {
                "type": "uniform_full_canvas_resize", "filter": "LANCZOS",
                "crop": None, "translation": [0, 0], "alphaCleanup": False,
            }, f"Export is not the documented whole-canvas transform: {slot}")
            source_sha = frame.get("sourceSha256")
            require(isinstance(source_sha, str) and re.fullmatch(r"[0-9a-f]{64}", source_sha),
                    f"Invalid source SHA: {slot}")
            derived = receipt.get("derivedFrom", {})
            require(derived == {"file": frame.get("sourceFile"), "sha256": source_sha,
                                "nativeSize": frame.get("sourceNativeSize")},
                    f"Derived source mismatch: {slot}")
            original = receipt.get("sourceGenerationRecord", {})
            record = original.get("record", {})
            require(record.get("sha256") == source_sha and
                    [record.get("width"), record.get("height")] == derived["nativeSize"],
                    f"Embedded original source evidence mismatch: {slot}")
            require(isinstance(derived["nativeSize"], list) and len(derived["nativeSize"]) == 2 and
                    derived["nativeSize"][0] == derived["nativeSize"][1] and
                    derived["nativeSize"][0] >= 1024, f"Source was not native square >=1024: {slot}")
            for field in ("configSnapshot", "submittedParameters", "actualModel", "actualQuality",
                          "generatedAt", "generatedAtEvidence", "tool", "route", "evidence"):
                require(field in record, f"Embedded generation record missing {field}: {slot}")
            require(all(receipt.get(field) == record.get(field) for field in
                        ("configSnapshot", "submittedParameters", "actualModel", "actualQuality")),
                    f"Export rewrote model/quality evidence: {slot}")
            # Read actual source pixels/record only when they reside inside this character.
            # Old reused external sources are preserved as embedded immutable text evidence;
            # this tool does not scan or read their unrelated directories.
            source = Path(frame["sourceFile"])
            source = (source if source.is_absolute() else BASE / source).resolve()
            check = {"slot": slot, "sourceFile": frame["sourceFile"], "sourceSha256": source_sha,
                     "embeddedEvidenceMatches": True, "actualLocalSourceChecked": False}
            if inside(source):
                if source.is_file():
                    require(digest(source) == source_sha, f"Current in-character source SHA mismatch: {slot}")
                    require(png_info(source) == derived["nativeSize"], f"Source size mismatch: {slot}")
                    check["actualLocalSourceChecked"] = True
                else:
                    histories=[BASE/'cleanup-report.json']+list((BASE/'provenance').glob('**/cleanup-*.json'))
                    removed=False
                    for history in histories:
                        if not history.is_file():continue
                        cleanup=read_json(history)
                        if cleanup.get('status')!='completed':continue
                        if any(Path(x.get('file','')).resolve()==source and x.get('sha256')==source_sha
                               for x in cleanup.get('deleted',[])):
                            removed=True;check['previousCleanupEvidence']=history.relative_to(BASE).as_posix();break
                    require(removed,f"Source absent without matching previous cleanup evidence: {slot}")
                    check['scopeNote']='Source pixels already removed by verified prior cleanup; embedded provenance and exact deleted SHA retained.'
            else:
                check["scopeNote"] = "External reused source not read; embedded provenance chain matched."
            original_path = Path(original.get("file", ""))
            require(bool(original.get("file")) and
                    re.fullmatch(r"[0-9a-f]{64}", str(original.get("sha256", ""))),
                    f"Missing original record path/hash: {slot}")
            original_path = (original_path if original_path.is_absolute() else BASE / original_path).resolve()
            if inside(original_path):
                require(original_path.is_file() and digest(original_path) == original["sha256"] and
                        read_json(original_path) == record, f"Original source record changed: {slot}")
            source_checks.append(check)
            by_slot[slot] = frame
            runtime_files.add(p)
    require(set(by_slot) == set(EXPECTED) and len(by_slot) == 196, "Runtime slot set is incomplete")
    actual_runtime = {p.resolve() for p in (BASE / "runtime").rglob("*")
                      if p.is_file() and p.suffix.lower() == ".png"}
    require(actual_runtime == runtime_files, "Runtime PNG tree has missing or extra images")
    return manifest, by_slot, runtime_files, source_checks


def validate_delivery(by_slot, runtime_files):
    data_path, html_path = BASE / "preview/delivery-data.json", BASE / "preview/delivery.html"
    require(data_path.is_file() and html_path.is_file(), "Formal delivery HTML/data absent")
    data, html = read_json(data_path), html_path.read_text(encoding="utf-8-sig")
    require(data.get("character") == BASE.name, "Delivery data character mismatch")
    parser = DeliveryHTML()
    parser.feed(html)
    require(len(parser.data_blocks) == 1, "Delivery HTML needs one embedded #data JSON block")
    require(json.loads(parser.data_blocks[0]) == data, "HTML embedded data differs from delivery-data.json")
    require("staging/" not in html.replace("\\", "/") and
            "staging/" not in json.dumps(data).replace("\\\\", "/"),
            "Delivery still references staging")
    delivered, protected = {}, set(runtime_files)
    groups = data.get("sequences")
    require(isinstance(groups, list) and len(groups) == 14, "Delivery sequence count mismatch")
    for group in groups:
        a, d = group.get("action"), group.get("direction")
        require(a in ACTIONS and d in ACTIONS[a][0], "Unexpected delivery direction")
        count, ms = ACTIONS[a][1:]
        require(group.get("ms") == ms and group.get("cycle") == count * ms, "Delivery timing mismatch")
        frames = group.get("frames")
        require(isinstance(frames, list) and len(frames) == count, "Delivery frame count mismatch")
        for frame in frames:
            slot = f"{a}-{d}-{frame.get('frame', 0):02d}"
            require(slot in by_slot and slot not in delivered, "Duplicate/unknown delivery frame")
            p = frame_reference(frame.get("src"))
            source = by_slot[slot]
            require(p == local(source["file"]) and frame.get("sha256") == source["sha256"] and
                    frame.get("duration") == source["durationMs"], f"Delivery/runtime mismatch: {slot}")
            require(p.is_file() and digest(p) == frame["sha256"], f"Stale delivery SHA: {slot}")
            delivered[slot] = p
    require(set(delivered) == set(EXPECTED) and set(delivered.values()) == runtime_files,
            "Delivery does not reference exactly the exported 196 runtime PNGs")
    # Audit literal resource paths too, including CSS/JS image strings.
    literals = [v for _, _, v in parser.resources]
    literals += re.findall(r"['\"]([^'\"\n]+\.(?:png|jpe?g|webp|gif|avif|bmp)(?:[?#][^'\"\n]*)?)['\"]",
                           html, flags=re.IGNORECASE)
    literals += re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", html, flags=re.IGNORECASE)
    for raw in literals:
        if raw.startswith("#"):
            continue
        url = urlsplit(raw)
        require(not url.scheme and not url.netloc, f"Unexpected external delivery resource: {raw}")
        target = local(unquote(url.path), BASE / "preview")
        require(target.is_file(), f"Broken delivery resource: {raw}")
        if target.suffix.lower() in IMAGE_SUFFIXES:
            require(target in runtime_files or target == KEEP_PREVIEW.resolve(),
                    f"Delivery references intermediate/non-runtime image: {raw}")
            protected.add(target)
    return {"htmlSha256": digest(html_path), "dataSha256": digest(data_path),
            "runtimeFrameReferences": len(delivered)}, protected


def image_candidate(path, reason):
    require(inside(path) and path.is_file() and not path.is_symlink(),
            f"Unscoped image or symlink: {path}")
    return {"file": path.relative_to(BASE).as_posix(), "sha256": digest(path),
            "bytes": path.stat().st_size, "reason": reason}


def candidate_images(protected):
    result = []
    for folder, suffixes, reason in [
        ("staging", {".png"}, "Native work/retry/source PNG, superseded by verified exported runtime."),
        ("review", {".png", ".jpg", ".jpeg"}, "Diagnostic contact sheet/crop; text records retained."),
        ("preview", IMAGE_SUFFIXES, "Intermediate preview image; formal run WebP retained."),
    ]:
        root = BASE / folder
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in suffixes:
                require(inside(path), f"Image symlink escapes character: {path}")
                if path.resolve() == KEEP_PREVIEW.resolve():
                    continue
                require(path.resolve() not in protected, f"Current delivery references candidate: {path}")
                result.append(image_candidate(path, reason))
    return result


def external_candidates():
    """Read only exact recorded paths; never enumerate the host image directory."""
    found, excluded = {}, []
    for receipt_path in sorted((BASE / "staging").glob("*.png.generation.json")):
        require(inside(receipt_path), "Staging provenance escapes character directory")
        require(receipt_path.is_file() and not receipt_path.is_symlink(),
                "Staging provenance must be a regular non-symlink file")
        record = read_json(receipt_path)
        raw = record.get("evidence", {}).get("toolReturnedPath")
        if not raw:
            continue
        p = Path(raw)
        allowed_root = next((root for root in EXTERNAL_ROOTS
                             if p.is_absolute() and p.resolve().is_relative_to(root.resolve())), None)
        if allowed_root is None or p.suffix.lower() != ".png":
            excluded.append({"record": receipt_path.relative_to(BASE).as_posix(),
                             "reason": "Returned path is outside the explicit allowed thread directories."})
            continue
        if not p.is_file() or p.is_symlink():
            excluded.append({"record": receipt_path.relative_to(BASE).as_posix(),
                             "reason": "Exact returned file is absent or is a symlink."})
            continue
        expected = record.get("sha256")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected) or digest(p) != expected:
            excluded.append({"record": receipt_path.relative_to(BASE).as_posix(),
                             "reason": "Returned source SHA does not match its staging generation record."})
            continue
        key = str(p.resolve())
        if key not in found:
            found[key] = {"file": key, "sha256": expected, "bytes": p.stat().st_size,
                          "allowedRoot": str(allowed_root.resolve()), "records": [],
                          "reason": "Exact same-thread host original; recorded SHA matches."}
        found[key]["records"].append(receipt_path.relative_to(BASE).as_posix())
    return list(found.values()), excluded


def plan():
    require(BASE == APPROVED_BASE, "Tool must remain in its approved character directory")
    result = {"schemaVersion": 1, "generatedAt": datetime.now(timezone.utc).isoformat(),
              "character": BASE.name, "scope": str(BASE), "mode": "plan_only",
              "executesDeletion": False, "writesVisualApproval": False,
              "status": "blocked", "blockingReasons": [], "localCandidates": [],
              "externalCandidates": [], "preserve": [
                  "runtime/**", "manifest.json", "preview/delivery.html", "preview/delivery-data.json",
                  "preview/run-current-960ms.webp", "all JSON/JSONL/TXT/MD/PY/JS/HTML and other text records",
                  "all provenance, requests, receipts, prompts, failed-call evidence and original source hashes",
              ],
              "limits": [
                  "Read-only plan, not an executable delete script or a visual/dynamic pass.",
                  "Stale exploratory HTML may become historical after later cleanup; only current delivery is gated.",
                  "Old reused external originals are outside this cleanup scope; embedded source evidence is matched.",
                  "External host candidates come only from exact toolReturnedPath records in four explicitly allowlisted thread roots.",
                  "Before any later deletion rerun this plan and recheck candidate SHA/current references.",
              ]}
    try:
        manifest, frames, runtime_files, checks = validate_export()
        delivery, protected = validate_delivery(frames, runtime_files)
        local_images = candidate_images(protected)
        external, excluded = external_candidates()
        result.update(status="ready_for_cleanup_review", manifestSha256=digest(BASE / "manifest.json"),
                      manifestStatus=manifest.get("status"), validatedRuntimeFrames=196,
                      sourceChecks=checks, deliveryChecks=delivery, localCandidates=local_images,
                      externalCandidates=external, externalExclusions=excluded)
    except (GuardError, OSError, ValueError, TypeError, KeyError) as exc:
        result["blockingReasons"].append(str(exc))
        # Fail closed: never emit any eligible list after even one unmet prerequisite.
        result["localCandidates"] = []
        result["externalCandidates"] = []
    result["summary"] = {
        "localImages": len(result["localCandidates"]),
        "localBytes": sum(x["bytes"] for x in result["localCandidates"]),
        "externalSameThreadOriginals": len(result["externalCandidates"]),
        "externalBytes": sum(x["bytes"] for x in result["externalCandidates"]),
        "deletionsExecuted": 0,
    }
    return result


def main():
    try:
        result = plan()
        # The only write performed by this program.
        target = BASE / "cleanup-plan.json"
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": result["status"], "plan": str(target),
                          "summary": result["summary"], "blockingReasons": result["blockingReasons"],
                          "visualApproval": "unchanged"}, ensure_ascii=False))
        return 0 if result["status"] == "ready_for_cleanup_review" else 2
    except (GuardError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc),
                          "deletionsExecuted": 0, "planWritten": False}, ensure_ascii=False),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
