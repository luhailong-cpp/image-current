"""Native-pixel core-cut baseline; no generation, resize, blending or acceptance.

Run --check for a read-only audit. Normal execution writes only under the chosen
northeast tile's qa/core-baseline/<input-signature>/ directory. It never changes
production.py, coordinates.json, progress.json or native sources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ZONE = Path(__file__).resolve().parent
CORE, HALO, NATIVE, FINAL = 1024, 115, 1254, 4096
CORE_CROP = [115, 115, 1139, 1139]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def resolved_file(value, base):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def file_evidence(path):
    path = Path(path)
    require(path.is_file(), f"Missing evidence: {path}")
    return {"file": str(path), "sha256": sha(path)}


def reference_evidence(ref, tile, contract):
    """Keep a missing, explicitly retired style reference honest and visible.

    This exception never substitutes the new style image or verifies old bytes.
    All present references, including a restored historical image, must hash-match.
    """
    path = resolved_file(ref["file"], tile)
    recorded_hash = ref["sha256"]
    require(isinstance(recorded_hash, str) and
            re.fullmatch(r"[0-9a-fA-F]{64}", recorded_hash),
            f"Invalid recorded reference SHA-256: {path}")
    previous = contract.get("previousPrimaryStyleReference")
    if not path.exists() and previous and path == resolved_file(previous, ZONE.parent):
        return {"file": str(path), "sha256": recorded_hash, "role": ref["role"],
                "referencePresent": False, "unverifiedHistoricalSource": True,
                "sha256Basis": "historical generation record; source bytes unavailable",
                "verification": "not reverified; exact retired style path named by contract"}
    evidence = file_evidence(path)
    require(evidence["sha256"] == recorded_hash, f"Reference hash changed: {path}")
    return {**evidence, "role": ref["role"], "referencePresent": True,
            "unverifiedHistoricalSource": False, "sha256Basis": "current source bytes"}


def load_plan(tile_id):
    require(re.fullmatch(r"r\d{2}_c\d{2}", tile_id), "Use a tile ID such as r05_c13")
    row, col = int(tile_id[1:3]), int(tile_id[5:7])
    require(1 <= row <= 8 and 9 <= col <= 16, "Tile is outside northeast ownership")
    tile = (ZONE / tile_id).resolve()
    require(tile.parent == ZONE, "Tile directory must be directly inside northeast")
    plan = read_json(tile / "coordinates.json")
    contract = read_json(ZONE.parent / "production-contract.json")
    require(contract["artCanvasPixels"] == [65536, 65536], "Unexpected canvas contract")
    require(contract["formalTilePixels"] == [FINAL, FINAL], "Unexpected tile contract")
    patch_plan = contract["nativePatchPlan"]
    require((patch_plan["corePixels"], patch_plan["haloPixels"],
             patch_plan["expectedNativePixels"]) == (CORE, HALO, NATIVE),
            "Contract patch dimensions changed; explicitly revise this baseline")
    ox, oy = (col - 1) * FINAL, (row - 1) * FINAL
    require(plan["tile"] == tile_id and plan["canvasPixels"] == [65536, 65536],
            "Coordinate identity/canvas mismatch")
    require(plan["coreWorldBox"] == [ox, oy, ox + FINAL, oy + FINAL],
            "Tile origin/extent mismatch")
    ids = [f"p{r}{c}" for r in range(1, 5) for c in range(1, 5)]
    require(len(plan["patches"]) == 16, "Coordinate plan must contain 16 patches")
    require(sorted(p["id"] for p in plan["patches"]) == ids, "Duplicate/missing patch IDs")
    for item in plan["patches"]:
        r, c = int(item["id"][1]), int(item["id"][2])
        x, y = ox + (c - 1) * CORE, oy + (r - 1) * CORE
        require(item["coreWorldBox"] == [x, y, x + CORE, y + CORE],
                f"Core coordinate mismatch: {item['id']}")
        require(item["contextWorldBox"] == [x - HALO, y - HALO,
                                            x + CORE + HALO, y + CORE + HALO],
                f"Context coordinate mismatch: {item['id']}")
        require(item["coreCrop"] == CORE_CROP, f"Core crop mismatch: {item['id']}")
    return tile, plan


def inspect_source(tile, item):
    patch_id = item["id"]
    selection_file = tile / "selected-native.json"
    selection = read_json(selection_file) if selection_file.exists() else {}
    native = tile / "native" / selection.get(patch_id, f"{patch_id}.png")
    sidecar = Path(str(native) + ".generation.json")
    record = read_json(sidecar)
    native_hash = sha(native)
    require(record["sha256"] == native_hash, "Native SHA-256 differs from generation record")
    require(resolved_file(record["file"], tile) == native.resolve(), "Record points at another native")
    require(record["nativeSize"] == [NATIVE, NATIVE], "Recorded native dimensions differ from plan")
    require(record["width"] == NATIVE and record["height"] == NATIVE, "Recorded width/height mismatch")
    require(record["format"] == "PNG", "Native record must identify PNG")
    require(record.get("resized") is False, "Native source must explicitly record resized=false")
    require(record.get("dimensionsMatch1254Plan") is True, "Native size plan is not confirmed")
    require(record["route"] == "builtin", "Source was not recorded as built-in generation")
    require(record["coordinates"] == item, "Source coordinates differ from current coordinate plan")
    for key in ("generatedAt", "tool", "configSnapshot", "submittedParameters",
                "actualModel", "actualQuality", "unverifiedReason"):
        require(key in record, f"Missing model/quality evidence field: {key}")
    with Image.open(native) as decoded:
        decoded.load()
        require(decoded.format == "PNG" and decoded.size == (NATIVE, NATIVE),
                "Measured native dimensions/format differ from plan; no resize is allowed")
        require(decoded.mode in ("RGB", "RGBA"), "Native must be RGB or RGBA")
        if decoded.mode == "RGBA":
            require(decoded.getextrema()[3] == (255, 255), "Ground native has transparent pixels")
        pixels = decoded.convert("RGB")
    prompt = resolved_file(record["prompt"], tile)
    request = resolved_file(record["request"], tile)
    receipt = resolved_file(record["evidence"], tile)
    saved_prompt = prompt.read_text(encoding="utf-8-sig")
    require(saved_prompt.strip(), "Prompt is empty")
    request_data = read_json(request)
    submitted_prompt = request_data["prompt"]
    require(saved_prompt in (submitted_prompt, submitted_prompt + "\n"),
            "Saved prompt and actual request prompt differ")
    read_json(receipt)  # A truncated/non-JSON receipt is incomplete evidence.
    contract = read_json(ZONE.parent / "production-contract.json")
    references = [reference_evidence(ref, tile, contract) for ref in record["references"]]
    require(bool(references), "No input references recorded")
    require([resolved_file(p, tile) for p in request_data["referenced_image_paths"]] ==
            [Path(ref["file"]) for ref in references], "Request/reference list differs")
    guide = file_evidence(resolved_file(item["guide"], tile))
    require(guide["sha256"] == item["guideSha256"], "Layout-only guide hash changed")
    source_path = resolved_file(record["sourceOutputPath"], tile)
    source_exists = source_path.is_file()
    if source_exists:
        require(sha(source_path) == native_hash, "Native differs from retained tool output bytes")
    evidence = {
        "id": patch_id, "file": str(native), "sha256": native_hash,
        "nativeSize": [NATIVE, NATIVE], "format": "PNG", "opaque": True,
        "generationRecord": file_evidence(sidecar), "prompt": file_evidence(prompt),
        "request": file_evidence(request), "receipt": file_evidence(receipt),
        "promptRequestComparison": "exact" if saved_prompt == submitted_prompt else
                                   "saved text has one terminal newline; request preserves actual prompt",
        "references": references, "layoutGuide": guide,
        "allReferenceBytesReverified": all(ref["referencePresent"] for ref in references),
        "coordinates": item, "coreCrop": CORE_CROP,
        "sourceOutputPath": str(source_path), "sourceOutputStillPresent": source_exists,
        "originalOutputByteIdentityChecked": source_exists,
        "configSnapshot": record["configSnapshot"],
        "submittedParameters": record["submittedParameters"],
        "actualModel": record["actualModel"], "actualQuality": record["actualQuality"],
        "unverifiedReason": record["unverifiedReason"], "generatedAt": record["generatedAt"],
    }
    return pixels, evidence


def inspect_sources(tile, plan):
    sources, evidence, missing, invalid = {}, [], [], []
    selection_file = tile / "selected-native.json"
    selection = read_json(selection_file) if selection_file.exists() else {}
    for item in plan["patches"]:
        patch_id = item["id"]
        native = tile / "native" / selection.get(patch_id, f"{patch_id}.png")
        if not native.is_file():
            missing.append(patch_id)
            continue
        try:
            pixels, entry = inspect_source(tile, item)
            sources[patch_id] = pixels
            evidence.append(entry)
        except (KeyError, TypeError, ValueError, OSError) as error:
            invalid.append({"id": patch_id, "file": str(native), "reason": str(error)})
    return sources, evidence, missing, invalid


def compose(plan, sources):
    canvas = Image.new("RGBA", (FINAL, FINAL), (0, 0, 0, 0))
    ox, oy = plan["coreWorldBox"][:2]
    for item in plan["patches"]:
        if item["id"] not in sources:
            continue
        image = sources[item["id"]]
        require(image.size == (NATIVE, NATIVE), "Refusing an unexpected measured native size")
        core = image.crop(tuple(item["coreCrop"])).convert("RGBA")
        x, y = item["coreWorldBox"][:2]
        canvas.paste(core, (x - ox, y - oy))
    hist = canvas.getchannel("A").histogram()
    require(sum(hist[1:255]) == 0, "Baseline contains interpolated alpha")
    require(hist[255] == len(sources) * CORE * CORE, "Opaque coverage differs from source count")
    return canvas


def difference_metrics(first, second):
    diff = ImageChops.difference(first, second)
    histogram = diff.histogram()
    samples = [sum(histogram[channel * 256 + value] for channel in range(3))
               for value in range(256)]
    target, total, p95 = sum(samples) * 0.95, 0, 0
    for value, count in enumerate(samples):
        total += count
        if total >= target:
            p95 = value
            break
    return {"meanAbsoluteRGBDifference": sum(ImageStat.Stat(diff).mean) / 3,
            "p95AbsoluteChannelDifference": p95,
            "interpretation": "diagnostic only; no geometry or visual acceptance inferred"}


def seam_pairs():
    for row in range(1, 5):
        for col in range(1, 4):
            yield "vertical", f"p{row}{col}", f"p{row}{col + 1}", col * CORE, (row - 1) * CORE
    for row in range(1, 4):
        for col in range(1, 5):
            yield "horizontal", f"p{row}{col}", f"p{row + 1}{col}", (col - 1) * CORE, row * CORE


def save_image(image, path, *, kind, source_ids, crop=None):
    image.save(path, format="PNG")
    with Image.open(path) as saved:
        saved.load()
        require(saved.mode == image.mode and saved.size == image.size and
                saved.tobytes() == image.tobytes(), "Exported PNG pixels differ")
    return {**file_evidence(path), "kind": kind, "pixels": list(image.size),
            "mode": image.mode, "sourceIds": source_ids, "crop": crop,
            "resized": False, "blurred": False, "visualStatus": "unreviewed"}


def write_outputs(tile, plan, sources, canvas, manifest):
    # Input signatures isolate incomplete runs from later complete candidates.
    output = tile / "qa" / "core-baseline" / manifest["inputSignature"][:20]
    output.mkdir(parents=True, exist_ok=True)
    artifacts = [save_image(canvas, output / "partial-core-baseline.rgba.png",
                           kind="partial-native-core-baseline", source_ids=sorted(sources))]
    if len(sources) == 16:
        artifacts.append(save_image(canvas.convert("RGB"), output / f"{plan['tile']}-core-baseline.candidate.png",
                                    kind="complete-4k-candidate-unreviewed", source_ids=sorted(sources)))
    seams = []
    for axis, first_id, second_id, x, y in seam_pairs():
        pair = [first_id, second_id]
        ready = all(p in sources for p in pair)
        entry = {"axis": axis, "sourceIds": pair, "ready": ready, "visualStatus": "unreviewed"}
        if ready:
            first, second = sources[first_id], sources[second_id]
            if axis == "vertical":
                a, b = first.crop((1024, 0, 1254, 1254)), second.crop((0, 0, 230, 1254))
                comparison = Image.new("RGB", (460, 1254))
                comparison.paste(a, (0, 0)); comparison.paste(b, (230, 0))
                box = [x - 192, y, x + 192, y + CORE]
            else:
                a, b = first.crop((0, 1024, 1254, 1254)), second.crop((0, 0, 1254, 230))
                comparison = Image.new("RGB", (1254, 460))
                comparison.paste(a, (0, 0)); comparison.paste(b, (0, 230))
                box = [x, y - 192, x + CORE, y + 192]
            stem = f"{axis}-{first_id}-{second_id}"
            artifacts.append(save_image(canvas.crop(tuple(box)), output / f"{stem}-join-100pct.png",
                                        kind="native-pixel-seam-crop", source_ids=pair, crop=box))
            artifacts.append(save_image(comparison, output / f"{stem}-overlap-comparison-100pct.png",
                                        kind="native-overlap-side-by-side" if axis == "vertical" else
                                             "native-overlap-top-bottom", source_ids=pair))
            entry["overlapPixels"] = 230
            entry["metrics"] = difference_metrics(a, b)
        seams.append(entry)
    for row in range(1, 4):
        for col in range(1, 4):
            ids = [f"p{r}{c}" for r in (row, row + 1) for c in (col, col + 1)]
            if any(p in sources for p in ids):
                x, y = col * CORE, row * CORE
                box = [x - 450, y - 450, x + 450, y + 450]
                artifacts.append(save_image(canvas.crop(tuple(box)), output / f"intersection-r{row}-c{col}-100pct.png",
                                            kind="native-pixel-intersection-crop", source_ids=[p for p in ids if p in sources], crop=box))
    for axis in ("vertical", "horizontal"):
        for index in range(1, 4):
            center = index * CORE
            box = ([center - 192, 0, center + 192, FINAL] if axis == "vertical" else
                   [0, center - 192, FINAL, center + 192])
            artifacts.append(save_image(canvas.crop(tuple(box)), output / f"full-{axis}-{index}-100pct.png",
                                        kind="full-native-seam-strip-partial-allowed", source_ids=sorted(sources), crop=box))
    manifest["artifacts"] = artifacts
    manifest["seams"] = seams
    manifest["readyInternalPairCount"] = sum(s["ready"] for s in seams)
    manifest["outputDirectory"] = str(output)
    path = output / "assembly.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def run(tile_id, check_only=False):
    tile, plan = load_plan(tile_id)
    sources, evidence, missing, invalid = inspect_sources(tile, plan)
    canvas = compose(plan, sources)
    inputs = {"coordinates": file_evidence(tile / "coordinates.json"),
              "contract": file_evidence(ZONE.parent / "production-contract.json"),
              "script": file_evidence(Path(__file__)), "nativeSources": evidence}
    if (tile / "selected-native.json").exists():
        inputs["selection"] = file_evidence(tile / "selected-native.json")
    signature = hashlib.sha256(json.dumps(inputs, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    complete = len(sources) == 16
    native_files = sorted((tile / "native").glob("*.png"))
    historical_missing = [{"id": item["id"], "reference": ref}
                          for item in evidence for ref in item["references"]
                          if ref["unverifiedHistoricalSource"]]
    manifest = {
        "schemaVersion": 1, "createdAt": datetime.now(timezone.utc).isoformat(),
        "zone": "northeast", "tile": tile_id, "inputSignature": signature,
        "status": "complete-4k-candidate-awaiting-seam-review" if complete else "partial-native-core-baseline",
        "generatedNativeFileCount": len(native_files), "validSelectedNativeCount": len(sources),
        "complete4kCandidateCount": int(complete), "formalAcceptedCount": 0,
        "opaquePixelCount": len(sources) * CORE * CORE,
        "coverageFraction": len(sources) / 16, "missingSelectedIds": missing,
        "invalidSelectedSources": invalid,
        "unverifiedHistoricalReferences": historical_missing,
        "allReferenceBytesReverified": not historical_missing and not invalid,
        "unselectedNativeFiles": [str(p) for p in native_files if p.resolve() not in
                                  {Path(item['file']).resolve() for item in evidence}],
        "inputs": inputs, "coreWorldBox": plan["coreWorldBox"],
        "operation": {"method": "direct 1024 core crop from each measured 1254 native; integer paste",
                      "coreCrop": CORE_CROP, "outputPixels": [FINAL, FINAL],
                      "sourceResampling": False, "finalArtUpscaled": False, "feathering": False,
                      "colorMatching": False, "layoutPixelsInFinal": False,
                      "missingPixels": "RGBA alpha=0; never filled using layout-only guides"},
        "visualQa": {"status": "unreviewed", "expectedInternalPairs": 24,
                     "expectedIntersections": 9, "externalTileSeams": "unreviewed",
                     "note": "Mechanical completeness is not visual acceptance."},
        "clientMappingValidated": False, "capacity5000Validated": False,
        "progressJsonModified": False,
    }
    output_manifest = None if check_only else str(write_outputs(tile, plan, sources, canvas, manifest))
    return {"tile": tile_id, "mode": "read-only-check" if check_only else "baseline-export",
            "generatedNativeFileCount": len(native_files), "validSelectedNativeCount": len(sources),
            "coverageFraction": len(sources) / 16,
            "complete4kCandidateEligible": complete,
            "complete4kCandidateCount": int(complete and not check_only),
            "formalAcceptedCount": 0, "missingSelectedIds": missing,
            "invalidSelectedSources": invalid, "assemblyManifest": output_manifest,
            "unverifiedHistoricalReferenceCount": len(historical_missing),
            "allReferenceBytesReverified": not historical_missing and not invalid,
            "note": "All seams remain unreviewed; progress.json was not changed."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tile", default="r05_c13")
    parser.add_argument("--check", action="store_true", help="Validate and compose in memory; write no files")
    args = parser.parse_args()
    try:
        result = run(args.tile, args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(1 if result["invalidSelectedSources"] else 0)
    except (KeyError, TypeError, ValueError, OSError) as error:
        parser.exit(2, f"Assembly refused: {error}\n")
