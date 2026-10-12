#!/usr/bin/env python3
"""Export only recorded, existing single-frame PNGs. No generation or cleanup."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")
SIZE = (1024, 1024)
PIVOT = {"topLeftPixels": [512, 942], "bottomLeftNormalized": [0.5, 0.08]}
IGNORED_STATUSES = {"rejected", "superseded", "cancelled", "failed"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def local_path(value):
    if not isinstance(value, str) or not value:
        raise ValueError("Expected a non-empty file path")
    path = Path(value)
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Frame, prompt, receipt and output files must stay in this pet directory: {value}")
    return path


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def issue(kind, code, message, **extra):
    return {"severity": kind, "code": code, "message": message, **extra}


def key_text(key):
    return f"{key[0]}/{key[1]}/{key[2]:02d}"


def expected_keys():
    return [(action, direction, i) for action, (count, _) in ACTIONS.items()
            for direction in DIRECTIONS for i in range(1, count + 1)]


def read_records():
    records, problems = {}, []
    for path in sorted((ROOT / "records").glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(data, dict):
                raise ValueError("One JSON object is required per record")
            if data.get("selected") is False or data.get("status") in IGNORED_STATUSES:
                continue
            # Static direction studies and receipts are not combat frames.
            if data.get("kind") == "design" or not any(field in data for field in ("action", "frame")):
                continue
            action, direction, number = data.get("action"), data.get("direction"), data.get("frame")
            if action not in ACTIONS or direction not in DIRECTIONS or type(number) is not int:
                raise ValueError("Combat record requires action, E/W direction and integer frame")
            if not 1 <= number <= ACTIONS[action][0]:
                raise ValueError("Frame number is outside this action's contract")
            if data.get("generationUnit", "single-frame") != "single-frame":
                raise ValueError("Only independently generated single-frame inputs are supported")
            key = (action, direction, number)
            if key in records:
                records[key]["ambiguous"] = True
                problems.append(issue("error", "ambiguous-record", "Multiple selected generation records; mark older retries selected:false", frame=key_text(key), records=[rel(records[key]["path"]), rel(path)]))
                continue
            source = local_path(data.get("file"))
            records[key] = {"data": data, "path": path, "source": source}
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            problems.append(issue("error", "invalid-record", str(exc), record=rel(path)))
    return records, problems


def check_record(record, key):
    data, result = record["data"], []
    location = {"frame": key_text(key), "record": rel(record["path"])}
    for field in ("file", "sha256", "generatedAt", "width", "height", "format", "tool", "route", "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "unverifiedReason", "prompt", "references", "evidence"):
        if field not in data:
            result.append(issue("error", "record-field-missing", field, **location))
    params = data.get("submittedParameters")
    if not isinstance(params, dict) or not all(field in params for field in ("model", "quality")):
        result.append(issue("error", "submitted-parameters-missing", "Explicit model/quality keys required; unknown must be null", **location))
    snapshot = data.get("configSnapshot", {})
    if not isinstance(snapshot, dict) or not all(field in snapshot for field in ("model", "quality", "builtin_product", "verified_on", "sources")):
        result.append(issue("error", "config-snapshot-incomplete", "Record the generation-time snapshot, never today's inferred defaults", **location))
    if (data.get("actualModel") is None or data.get("actualQuality") is None) and not data.get("unverifiedReason"):
        result.append(issue("error", "unknown-without-reason", "Unknown model/quality requires an explicit reason", **location))
    if not data.get("evidence"):
        result.append(issue("error", "evidence-missing", "Save the actual tool result/receipt evidence", **location))
    refs = data.get("references")
    if not isinstance(refs, list) or not refs:
        result.append(issue("error", "references-missing", "Actual attached reference paths and purposes are required", **location))
    elif any(not isinstance(ref, dict) or not ref.get("path") or not ref.get("purpose") for ref in refs):
        result.append(issue("error", "references-incomplete", "Every reference needs path and purpose", **location))
    try:
        stamp = datetime.fromisoformat(data.get("generatedAt", "").replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("Timezone missing")
    except (ValueError, TypeError, AttributeError):
        result.append(issue("error", "generation-time-invalid", "generatedAt must contain an explicit timezone", **location))
    try:
        if not local_path(data.get("prompt")).is_file():
            result.append(issue("error", "prompt-missing", "Actual prompt file not found", **location))
    except ValueError as exc:
        result.append(issue("error", "prompt-path-invalid", str(exc), **location))
    return result


def dimensions(records, problems):
    by_direction = defaultdict(set)
    for key, record in records.items():
        if record.get("ambiguous") or not record["source"].is_file():
            continue
        try:
            with Image.open(record["source"]) as image:
                if image.format != "PNG":
                    raise ValueError("Source must be a PNG")
                image.verify()
            with Image.open(record["source"]) as image:
                record["nativeSize"] = image.size
                record["nativeMode"] = image.mode
                by_direction[key[1]].add(image.size)
            record["sourceSha256"] = sha(record["source"])
            data = record["data"]
            if record["sourceSha256"] != data.get("sha256"):
                problems.append(issue("error", "source-sha-mismatch", "Source bytes do not match generation record; export refused", frame=key_text(key)))
                record["unusable"] = True
            if list(record["nativeSize"]) != [data.get("width"), data.get("height")] or data.get("format", "").upper() != "PNG":
                problems.append(issue("error", "native-metadata-mismatch", "Actual native dimensions/format differ from record", frame=key_text(key)))
                record["unusable"] = True
        except (OSError, ValueError) as exc:
            problems.append(issue("error", "source-unreadable", str(exc), frame=key_text(key)))
            record["unusable"] = True
    return by_direction


def transforms(sizes, settings, problems):
    result = {}
    for direction in DIRECTIONS:
        values = sizes.get(direction, set())
        if len(values) > 1:
            problems.append(issue("error", "mixed-native-coordinates", "All actions within one direction must share native canvas coordinates; no frame-specific normalization", direction=direction, dimensions=[list(x) for x in sorted(values)]))
            continue
        if not values:
            continue
        width, height = next(iter(values))
        custom = settings.get(direction)
        if custom:
            if custom.get("sourceSize") != [width, height]:
                problems.append(issue("error", "transform-size-mismatch", "Declared sourceSize differs from actual direction canvases", direction=direction))
                continue
            scale, offset = custom.get("scale"), custom.get("offsetPixels")
            if not isinstance(scale, (float, int)) or not math.isfinite(scale) or scale <= 0 or not isinstance(offset, list) or len(offset) != 2 or any(type(v) is not int for v in offset):
                problems.append(issue("error", "transform-invalid", "scale must be positive finite; offsetPixels must be two integers", direction=direction))
                continue
        else:
            scale = min(1024 / width, 1024 / height)
            scaled = [round(width * scale), round(height * scale)]
            offset = [(1024 - scaled[0]) // 2, (1024 - scaled[1]) // 2]
        scaled = [round(width * scale), round(height * scale)]
        if scaled[0] < 1 or scaled[1] < 1:
            problems.append(issue("error", "transform-empty", "Transform would create an empty canvas", direction=direction))
            continue
        # A native 1024 RGBA image is never resampled or shifted by this exporter.
        if (width, height) == SIZE and (scale != 1 or offset != [0, 0]):
            problems.append(issue("error", "native-1024-transform-refused", "Native 1024 canvas must remain unchanged", direction=direction))
            continue
        result[direction] = {"sourceSize": [width, height], "scale": scale, "offsetPixels": offset, "scaledSize": scaled, "method": "uniform-direction-canvas-transform", "footRealignment": False}
    return result


def render_source(record, transform):
    with Image.open(record["source"]) as image:
        rgba = image.convert("RGBA")
    if transform["scaledSize"] == list(SIZE) and transform["offsetPixels"] == [0, 0] and rgba.size == SIZE:
        return rgba, "byte-copy" if record["nativeMode"] == "RGBA" else "rgba-conversion"
    scaled = rgba.resize(tuple(transform["scaledSize"]), Image.Resampling.LANCZOS)
    offset = transform["offsetPixels"]
    bbox = scaled.getchannel("A").getbbox()
    if bbox and (bbox[0] + offset[0] < 0 or bbox[1] + offset[1] < 0 or bbox[2] + offset[0] > 1024 or bbox[3] + offset[1] > 1024):
        raise ValueError("Uniform transform would crop visible pixels; choose a safer direction-wide transform")
    output = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    output.alpha_composite(scaled, tuple(offset))
    return output, "uniform-scale-and-canvas-placement"


def image_metrics(image):
    alpha = image.getchannel("A")
    hist = alpha.histogram()
    bbox = alpha.getbbox()
    bbox16 = alpha.point(lambda value: 255 if value > 16 else 0).getbbox()
    bbox128 = alpha.point(lambda value: 255 if value > 128 else 0).getbbox()
    visible = Image.new("RGBA", image.size, (0, 0, 0, 0))
    visible.alpha_composite(image)
    cropped = visible.crop(bbox) if bbox else visible
    def digest(value):
        return hashlib.sha256(str(value.size).encode() + value.tobytes()).hexdigest()
    return {"width": image.width, "height": image.height, "mode": image.mode,
            "alphaExtrema": list(alpha.getextrema()), "transparentPixels": hist[0],
            "semitransparentPixels": sum(hist[1:255]), "opaquePixels": hist[255],
            "alphaBBox": list(bbox) if bbox else None,
            "alphaBBoxAbove16": list(bbox16) if bbox16 else None,
            "alphaBBoxAbove128": list(bbox128) if bbox128 else None,
            "edgeContact": bool(bbox and (bbox[0] == 0 or bbox[1] == 0 or bbox[2] == image.width or bbox[3] == image.height)),
            "edgeContactAbove16": bool(bbox16 and (bbox16[0] == 0 or bbox16[1] == 0 or bbox16[2] == image.width or bbox16[3] == image.height)),
            "edgeContactAbove128": bool(bbox128 and (bbox128[0] == 0 or bbox128[1] == 0 or bbox128[2] == image.width or bbox128[3] == image.height)),
            "visiblePixelSha256": digest(visible), "translationInvariantSha256": digest(cropped),
            "mirroredCropSha256": digest(cropped.transpose(Image.Transpose.FLIP_LEFT_RIGHT))}


def export_or_check(args, records, transform_map, problems):
    frames = []
    for key in expected_keys():
        record = records.get(key)
        if record is None or record.get("ambiguous"):
            continue
        problems.extend(check_record(record, key))
        action, direction, number = key
        target = ROOT / "runtime" / action / direction / f"{number:02d}.png"
        source_exists = record["source"].is_file()
        transform = transform_map.get(direction)
        operation = None
        if args.mode in ("plan", "export") and source_exists and not record.get("unusable") and transform:
            try:
                output, operation = render_source(record, transform)
                if args.mode == "export":
                    if target.exists() and not args.overwrite:
                        with Image.open(target) as old:
                            equal = old.mode == "RGBA" and old.size == output.size and old.tobytes() == output.tobytes()
                        if not equal:
                            raise ValueError("Existing runtime differs; review selected record then use --overwrite")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if operation == "byte-copy":
                        if record["source"].resolve() != target.resolve():
                            shutil.copyfile(record["source"], target)
                    else:
                        output.save(target, format="PNG")
                    derived = {"schemaVersion": 1, "file": rel(target), "sha256": sha(target), "exportedAt": now(),
                               "width": 1024, "height": 1024, "format": "PNG", "mode": "RGBA",
                               "derivedFrom": {"file": record["data"]["file"], "sha256": record["sourceSha256"], "generationRecord": rel(record["path"]), "nativeSize": record["data"].get("width") and [record["data"]["width"], record["data"]["height"]]},
                               "operation": {"type": operation, "transform": transform},
                               "configSnapshot": record["data"].get("configSnapshot"),
                               "actualModel": record["data"].get("actualModel"), "actualQuality": record["data"].get("actualQuality"),
                               "unverifiedReason": record["data"].get("unverifiedReason"), "aiGenerationPerformedByExport": False}
                    write_json(target.with_suffix(".png.generation.json"), derived)
            except (OSError, ValueError) as exc:
                problems.append(issue("error", "export-refused", str(exc), frame=key_text(key)))
                continue
        elif args.mode == "export" and source_exists:
            continue
        if args.mode == "plan" and source_exists and operation:
            metrics = image_metrics(output)
            output_sha = None
        elif target.is_file():
            try:
                with Image.open(target) as image:
                    if image.format != "PNG" or image.mode != "RGBA" or image.size != SIZE:
                        raise ValueError("Runtime must be a 1024x1024 RGBA PNG")
                    metrics = image_metrics(image)
                output_sha = sha(target)
            except (OSError, ValueError) as exc:
                problems.append(issue("error", "runtime-invalid", str(exc), frame=key_text(key)))
                continue
        else:
            problems.append(issue("error", "source-and-runtime-unavailable", "No usable recorded native input or runtime output", frame=key_text(key)))
            continue
        derivative_path = target.with_suffix(".png.generation.json")
        derived = None
        if args.mode != "plan":
            try:
                derived = json.loads(derivative_path.read_text(encoding="utf-8"))
                if derived.get("sha256") != output_sha or derived.get("derivedFrom", {}).get("sha256") != record["data"].get("sha256") or derived.get("derivedFrom", {}).get("generationRecord") != rel(record["path"]):
                    raise ValueError("Runtime source chain/hash differs from selected record")
                operation = derived.get("operation", {}).get("type")
                transform = derived.get("operation", {}).get("transform")
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                problems.append(issue("error", "derived-record-invalid", str(exc), frame=key_text(key)))
        if not source_exists and record["data"].get("sourceRetention", {}).get("status") != "deleted-after-export":
            problems.append(issue("error", "source-missing-undocumented", "Native source missing without sourceRetention cleanup record", frame=key_text(key)))
        if metrics["alphaBBox"] is None or metrics["transparentPixels"] == 0:
            problems.append(issue("error", "alpha-invalid", "Runtime is empty or has no fully transparent background pixels", frame=key_text(key)))
        if metrics["edgeContact"]:
            problems.append(issue("warning", "edge-contact", "Some alpha touches the canvas edge; compare alpha>16 and >128 bounds before judging clipping. No pixels were removed.", frame=key_text(key), alphaAbove16=metrics["edgeContactAbove16"], alphaAbove128=metrics["edgeContactAbove128"]))
        frames.append({"id": key_text(key), "action": action, "direction": direction, "frame": number,
                       "file": rel(target), "width": 1024, "height": 1024, "durationMs": ACTIONS[action][1],
                       "pivot": PIVOT, "event": record["data"].get("event"), "sha256": output_sha,
                       "source": {"file": record["data"]["file"], "sha256": record["data"].get("sha256"),
                                  "generationRecord": rel(record["path"]), "nativeSize": [record["data"].get("width"), record["data"].get("height")],
                                  "retained": source_exists, "actualModel": record["data"].get("actualModel"), "actualQuality": record["data"].get("actualQuality")},
                       "derivedRecord": rel(derivative_path), "operation": operation, "exportTransform": transform,
                       "visualStatus": record["data"].get("visualStatus", "pending"), "metrics": metrics})
    return frames


def validate_duplicates(frames, problems):
    exact, translations, mirrors = defaultdict(list), defaultdict(list), defaultdict(list)
    for frame in frames:
        exact[frame["metrics"]["visiblePixelSha256"]].append(frame["id"])
        translations[frame["metrics"]["translationInvariantSha256"]].append(frame["id"])
        mirrors[frame["metrics"]["translationInvariantSha256"]].append(frame)
    for group in exact.values():
        if len(group) > 1:
            problems.append(issue("error", "duplicate-frame-pixels", "Identical visible frame pixels", frames=group))
    for group in translations.values():
        if len(group) > 1 and len({next(f for f in frames if f["id"] == name)["metrics"]["visiblePixelSha256"] for name in group}) > 1:
            problems.append(issue("error", "translation-only-frames", "Same visible pixels at different canvas positions", frames=group))
    checked = set()
    for frame in frames:
        for other in mirrors.get(frame["metrics"]["mirroredCropSha256"], []):
            pair = tuple(sorted([frame["id"], other["id"]]))
            if other["direction"] != frame["direction"] and pair not in checked:
                checked.add(pair)
                problems.append(issue("error", "opposite-direction-mirror", "Exact mirrored pixels across E/W; back view must be independently drawn", frames=list(pair)))


def contact_sheet(group, frames, destination):
    tile, label_height, columns = 224, 30, 4
    rows = math.ceil(group["expectedFrames"] / columns)
    sheet = Image.new("RGB", (columns * tile, rows * (tile + label_height)), "#182c30")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=15)
    by_number = {frame["frame"]: frame for frame in frames}
    for number in range(1, group["expectedFrames"] + 1):
        x, y = ((number - 1) % columns) * tile, ((number - 1) // columns) * (tile + label_height)
        for yy in range(0, tile, 16):
            for xx in range(0, tile, 16):
                draw.rectangle((x + xx, y + yy, x + xx + 15, y + yy + 15), fill="#d4dedb" if (xx // 16 + yy // 16) % 2 else "#edf1e9")
        frame = by_number.get(number)
        if frame:
            with Image.open(ROOT / frame["file"]) as image:
                thumb = image.resize((tile, tile), Image.Resampling.LANCZOS)
                sheet.paste(thumb, (x, y), thumb)
        else:
            draw.text((x + 50, y + tile // 2), "MISSING", font=font, fill="#9a2434")
        draw.text((x + 7, y + tile + 6), f'{group["action"]} {group["direction"]} {number:02d} / {group["durationMs"]}ms', font=font, fill="#ffffff")
    sheet.save(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("plan", "export", "verify"), nargs="?", default="plan", help="plan reads only; export writes runtime+reports+previews; verify reads runtime and writes reports+previews")
    parser.add_argument("--transforms", type=Path, help="Optional fixed E/W transforms JSON inside this pet directory")
    parser.add_argument("--overwrite", action="store_true", help="Replace changed runtime frames from explicitly selected records")
    args = parser.parse_args()
    records, problems = read_records()
    settings = {}
    if args.transforms:
        settings = json.loads(local_path(str(args.transforms)).read_text(encoding="utf-8-sig"))
    sizes = dimensions(records, problems)
    transform_map = transforms(sizes, settings, problems)
    frames = export_or_check(args, records, transform_map, problems)
    validate_duplicates(frames, problems)
    found = {(f["action"], f["direction"], f["frame"]) for f in frames}
    missing = [key_text(key) for key in expected_keys() if key not in found]
    referenced = {f["file"] for f in frames}
    unrecorded = [rel(path) for path in sorted((ROOT / "runtime").glob("*/*/*.png")) if rel(path) not in referenced]
    if unrecorded:
        problems.append(issue("error", "unrecorded-runtime", "Runtime files without a unique selected source record are excluded", files=unrecorded))
    for direction in DIRECTIONS:
        actual_transforms = {json.dumps(f["exportTransform"], sort_keys=True) for f in frames if f["direction"] == direction}
        if len(actual_transforms) > 1:
            problems.append(issue("error", "mixed-export-transforms", "One direction has inconsistent export coordinates", direction=direction))
    groups = [{"action": action, "direction": direction, "expectedFrames": count, "durationMs": duration,
               "expectedTotalMs": count * duration, "availableFrames": sum(f["action"] == action and f["direction"] == direction for f in frames),
               "contactSheet": f"preview/{action}-{direction}-contact.png"}
              for action, (count, duration) in ACTIONS.items() for direction in DIRECTIONS]
    errors = sum(p["severity"] == "error" for p in problems)
    visual_pending = [f["id"] for f in frames if f["visualStatus"] != "passed"]
    validation = {"schemaVersion": 1, "checkedAt": now(), "mode": args.mode, "expectedFrames": 68,
                  "availableFrames": len(frames), "missingFrames": missing, "issues": problems,
                  "technicalStatus": "failed" if errors else ("incomplete" if missing else "passed"),
                  "visualReview": {"status": "pending" if visual_pending or missing else "recorded-passed", "pendingFrames": visual_pending, "note": "Only reads the review status saved by a human/visual reviewer; does not perform visual or motion review."},
                  "motionReview": {"status": "pending", "note": "Play all six groups and record independent review evidence."},
                  "clientIntegration": {"status": "not-performed"}, "unrecordedRuntimeFiles": unrecorded}
    review_path = ROOT / "qa/final-review.json"
    if review_path.exists():
        review = json.loads(review_path.read_text(encoding="utf-8-sig"))
        if review.get("reviewedRuntimeSha256") == {f["id"]: f["sha256"] for f in frames}:
            validation["motionReview"] = {"status": review.get("motionStatus"), "evidence": "qa/final-review.json", "note": review.get("scope")}
    manifest = {"schemaVersion": 1, "pet": "legacy-yun-jiu-jiu", "name": "云啾啾", "builtAt": now(),
                "dimensions": [1024, 1024], "pivot": PIVOT, "expectedFrames": 68, "availableFrames": len(frames),
                "coordinatePolicy": "One native canvas and one uniform export transform per direction across all actions; no per-frame foot alignment.",
                "transforms": transform_map, "groups": groups, "frames": frames, "missingFrames": missing,
                "technicalStatus": validation["technicalStatus"], "artAndMotionApproval": "not-implied", "clientIntegration": "not-performed"}
    if args.mode != "plan":
        write_json(ROOT / "manifest.json", manifest)
        write_json(ROOT / "validation.json", validation)
        preview = ROOT / "preview"
        preview.mkdir(parents=True, exist_ok=True)
        for group in groups:
            group_frames = [f for f in frames if f["action"] == group["action"] and f["direction"] == group["direction"]]
            contact_sheet(group, group_frames, ROOT / group["contactSheet"])
        template = (preview / "template.html").read_text(encoding="utf-8")
        embedded = json.dumps(manifest, ensure_ascii=False).replace("<", "\\u003c")
        (preview / "index.html").write_text(template.replace("__MANIFEST_JSON__", embedded), encoding="utf-8")
        for group in groups:
            group_frames = [f for f in frames if f["action"] == group["action"] and f["direction"] == group["direction"]]
            standalone = dict(manifest, groups=[group], frames=group_frames, expectedFrames=group["expectedFrames"], availableFrames=len(group_frames))
            payload = json.dumps(standalone, ensure_ascii=False).replace("<", "\\u003c")
            (preview / f'{group["action"]}-{group["direction"]}.html').write_text(template.replace("__MANIFEST_JSON__", payload), encoding="utf-8")
    print(json.dumps({"mode": args.mode, "technicalStatus": validation["technicalStatus"], "availableFrames": len(frames), "expectedFrames": 68, "missingFrames": missing, "errors": errors, "warnings": sum(p["severity"] == "warning" for p in problems), "issues": problems, "writesPerformed": args.mode != "plan"}, ensure_ascii=False, indent=2))
    return 2 if errors else (1 if missing else 0)


if __name__ == "__main__":
    sys.exit(main())
