#!/usr/bin/env python3
"""Read-only inventory of this character; --write-reports writes local reports/preview data.

This tool does not generate, export, move, resize, replace, or approve any image.
Pillow is required. Every output path is fixed beneath this character directory.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageOps

CHARACTER = "09_bamboo_archer_girl"
ROOT = Path(__file__).resolve().parents[1]
ACTIONS = {"hit": (6, 40, ("E", "W")), "attack": (12, 30, ("E", "W")),
           "cast": (16, 45, ("E", "W")),
           "run": (16, 75, ("N", "NE", "E", "SE", "S", "SW", "W", "NW"))}


def local(path: Path) -> Path:
    value = path.resolve()
    if ROOT.name != CHARACTER or not value.is_relative_to(ROOT):
        raise ValueError(f"Path outside this character: {path}")
    return value


def rel(path: Path) -> str:
    return local(path).relative_to(ROOT).as_posix()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    data = json.loads(local(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def canonical_hash(image: Image.Image) -> str:
    pixels = bytearray(image.convert("RGBA").tobytes())
    for index in range(0, len(pixels), 4):
        if pixels[index + 3] == 0:
            pixels[index:index + 3] = b"\0\0\0"
    return hashlib.sha256(pixels).hexdigest()


def inspect_png(path: Path) -> dict:
    result = {"file": rel(path), "sha256": digest(path), "errors": []}
    try:
        with Image.open(path) as image:
            image.load()
            result.update({"size": list(image.size), "mode": image.mode, "format": image.format})
            if image.format != "PNG":
                result["errors"].append("not_png")
            if image.mode != "RGBA":
                result["errors"].append("not_rgba")
            if image.size != (1024, 1024):
                result["errors"].append("not_1024_square")
            rgba = image.convert("RGBA")
            alpha = rgba.getchannel("A")
            histogram = alpha.histogram()
            bbox = alpha.point(lambda value: 255 if value > 8 else 0).getbbox()
            result.update({"visibleBBox": list(bbox) if bbox else None,
                           "fullyTransparentPixels": histogram[0],
                           "semiTransparentPixels": sum(histogram[1:255]),
                           "visiblePixelSha256": canonical_hash(rgba),
                           "mirroredVisiblePixelSha256": canonical_hash(ImageOps.mirror(rgba))})
            if not bbox:
                result["errors"].append("empty_image")
            if not histogram[0]:
                result["errors"].append("no_true_transparency")
            if bbox and (bbox[0] == 0 or bbox[1] == 0 or bbox[2] == image.width or bbox[3] == image.height):
                result["errors"].append("visible_pixels_touch_edge")
    except (OSError, ValueError) as error:
        result["errors"].append(f"decode_failed: {error}")
    return result


def get_selections() -> tuple[dict, list]:
    result, issues = {}, []
    paths = set(ROOT.glob("*selection.json")) | set((ROOT / "selection").glob("*.json"))
    for path in sorted(paths):
        try:
            data = load(path)
            for entry in data.get("frames", []):
                action, direction = entry.get("action", data.get("action")), entry.get("direction", data.get("direction"))
                frame = entry.get("frame")
                if action not in ACTIONS or direction not in ACTIONS[action][2] or type(frame) is not int or not 1 <= frame <= ACTIONS[action][0]:
                    raise ValueError(f"Invalid slot in {rel(path)}: {action}/{direction}/{frame}")
                key = f"{action}/{direction}/{frame:02d}"
                if key in result:
                    raise ValueError(f"Repeated selection for {key}")
                result[key] = {**entry, "selectionFile": rel(path)}
        except (ValueError, OSError, TypeError, KeyError) as error:
            issues.append(str(error))
    return result, issues


def scan() -> tuple[dict, dict, dict]:
    checked = datetime.now(timezone.utc).isoformat()
    selected, issues = get_selections()
    pngs = {rel(path): inspect_png(path) for path in sorted(ROOT.rglob("*.png")) if path.is_file()}
    review = load(ROOT / "review.json") if (ROOT / "review.json").is_file() else {}
    frame_reviews = {entry.get("slot"): entry for entry in review.get("frames", [])}
    sequence_reviews = {entry.get("sequence"): entry for entry in review.get("sequences", [])}
    anchor = load(ROOT / "anchor.json") if (ROOT / "anchor.json").is_file() else {}
    sequences, slots = [], []
    visible, mirror = defaultdict(list), defaultdict(list)
    for action, (count, frame_ms, directions) in ACTIONS.items():
        for direction in directions:
            sequence = {"label": f"{action}/{direction}", "action": action, "direction": direction,
                        "count": count, "ms": frame_ms, "frames": [], "dynamicApproval": "pending"}
            if action == "run":
                sequence.update(timingStatus="offline_default_1200ms_client_unconfirmed", oldBaselineMs=480,
                                comparisonCycleMs=[1200], clientTimingConfirmed=False)
            for frame in range(1, count + 1):
                key = f"{action}/{direction}/{frame:02d}"
                runtime = f"runtime/{key}.png"
                selection = selected.get(key, {})
                source = selection.get("file")
                if source:
                    source = rel(ROOT / source)
                runtime_info = pngs.get(runtime)
                source_info = pngs.get(source)
                info = runtime_info or source_info
                errors = list(info.get("errors", [])) if info else []
                if source and source_info and selection.get("sha256") != source_info["sha256"]:
                    errors.append("selection_source_hash_mismatch_or_missing")
                generation_record = selection.get("generationRecord")
                provenance = None
                provenance_errors = []
                if generation_record:
                    try:
                        record_path = local(ROOT / generation_record)
                        provenance = {"file": rel(record_path), "sha256": digest(record_path), "record": load(record_path)}
                        expected = selection.get("generationRecordSha256")
                        if expected and expected != provenance["sha256"]:
                            provenance_errors.append("generation_record_hash_mismatch")
                        record = provenance["record"]
                        required = ("file", "sha256", "generatedAt", "tool", "route", "configSnapshot",
                                    "submittedParameters", "actualModel", "actualQuality", "evidence",
                                    "prompt", "references", "width", "height")
                        absent = [field for field in required if field not in record]
                        if absent:
                            provenance_errors.append("generation_record_missing_fields:" + ",".join(absent))
                        if not record.get("evidence") or not record.get("prompt") or not record.get("references"):
                            provenance_errors.append("generation_record_missing_evidence_prompt_or_references")
                        if (record.get("actualModel") is None or record.get("actualQuality") is None) and not record.get("unverifiedReason"):
                            provenance_errors.append("unknown_model_or_quality_needs_explicit_reason")
                        bound_hash = source_info["sha256"] if source_info else selection.get("sha256") or (info["sha256"] if info else None)
                        if not bound_hash or record.get("sha256") != bound_hash:
                            provenance_errors.append("generation_record_source_hash_mismatch")
                        if record.get("file"):
                            expected_file = source or (info["file"] if info else None)
                            if rel(ROOT / record["file"]) != expected_file:
                                provenance_errors.append("generation_record_source_path_mismatch")
                    except (ValueError, OSError) as error:
                        provenance_errors.append(f"generation_record_unreadable: {error}")
                elif info:
                    provenance_errors.append("generation_record_not_linked")
                errors.extend(provenance_errors)
                native = selection.get("sourceNativeSize")
                if provenance:
                    record = provenance["record"]
                    native = record.get("nativeCellSize", record.get("nativeSize", native))
                    if native is None and "width" in record and "height" in record:
                        native = [record["width"], record["height"]]
                provenance_passed = bool(info and provenance and not provenance_errors)
                native_eligible = provenance_passed and isinstance(native, list) and len(native) == 2 and all(isinstance(value, int) and value >= 1024 for value in native)
                if info and not native_eligible:
                    errors.append("source_native_resolution_missing_or_below_1024")
                if runtime_info and source_info and source != runtime and runtime_info["sha256"] != source_info["sha256"]:
                    errors.append("runtime_differs_from_selected_source_requires_derived_receipt_review")
                check = frame_reviews.get(key, {})
                visual = bool(info and check.get("status") == "passed" and check.get("sha256") == info["sha256"])
                previewable = bool(info and info.get("size") == [1024, 1024] and "decode_failed" not in " ".join(errors))
                row = {"slot": key, "frame": frame, "file": info["file"] if info else None,
                       "sha256": info["sha256"] if info else None, "pngExists": bool(info),
                       "runtimeExportExists": bool(runtime_info), "previewable": previewable,
                       "sourceNativeSize": native, "nativeResolutionEvidencePassed": native_eligible,
                       "sourceEvidencePassed": provenance_passed,
                       "technicalChecksPassed": bool(info and not errors), "technicalErrors": errors,
                       "visualApproval": "passed" if visual else "pending",
                       "dynamicApproval": "pending", "generationRecord": provenance,
                       "selection": selection or None,
                       "previewUrl": "../" + info["file"] + "?v=" + info["sha256"][:16] if previewable else None}
                if info:
                    visible[info.get("visiblePixelSha256")].append(key)
                    mirror[info.get("mirroredVisiblePixelSha256")].append(key)
                slots.append(row)
                sequence["frames"].append(row)
            hashes = [entry["sha256"] for entry in sequence["frames"]]
            check = sequence_reviews.get(sequence["label"], {})
            dynamic = all(hashes) and check.get("status") == "passed" and check.get("frameSha256") == hashes
            if dynamic:
                sequence["dynamicApproval"] = "passed"
                for entry in sequence["frames"]:
                    entry["dynamicApproval"] = "passed"
            sequence["present"] = sum(entry["pngExists"] for entry in sequence["frames"])
            sequence["exports"] = sum(entry["runtimeExportExists"] for entry in sequence["frames"])
            sequences.append(sequence)
    duplicates = [keys for value, keys in visible.items() if value and len(keys) > 1]
    mirrors = []
    for value, keys in visible.items():
        if value and value in mirror:
            for key in keys:
                for other in mirror[value]:
                    pair = sorted([key, other])
                    if key != other and pair not in mirrors:
                        mirrors.append(pair)
    missing = [row["slot"] for row in slots if not row["pngExists"]]
    counts = {"expectedSlots": len(slots), "actualPngFilesInCharacter": len(pngs),
              "slotsWithActualPng": len(slots) - len(missing),
              "exportedRuntimeSlots": sum(row["runtimeExportExists"] for row in slots),
              "technicalChecksPassed": sum(row["technicalChecksPassed"] for row in slots),
              "nativeResolutionEvidencePassed": sum(row["nativeResolutionEvidencePassed"] for row in slots),
              "sourceEvidencePassed": sum(row["sourceEvidencePassed"] for row in slots),
              "visualPassedSlots": sum(row["visualApproval"] == "passed" for row in slots),
              "dynamicPassedSequences": sum(seq["dynamicApproval"] == "passed" for seq in sequences),
              "expectedSequences": len(sequences), "missingSlots": len(missing)}
    status = {"character": CHARACTER, "checkedAtUtc": checked, "counts": counts,
              "status": "incomplete" if missing else "all_slots_present_review_separately",
              "clientIntegration": "not_integrated", "clientRuntimeAcceptance": "not_tested",
              "missingSlots": missing, "inventoryIssues": issues,
              "exactVisibleDuplicates": duplicates, "exactMirroredPairs": mirrors,
              "automaticApproval": False,
              "limits": "PNG existence, unique SHA, native resolution and technical export do not prove anatomy, continuity or visual approval. Review passes require exact current hashes. This inventory does not export or alter images."}
    accepted_path = ROOT / "accepted-version.json"
    if accepted_path.exists():
        accepted = load(accepted_path)
        current_hashes = {row["file"]: row["sha256"] for row in slots if row["file"]}
        accepted_hashes = {row["file"]: row["sha256"] for row in accepted.get("frames", [])}
        matches = len(current_hashes) == 196 and current_hashes == accepted_hashes
        status["userFeedback"] = {"record": "accepted-version.json", "verbatimFeedback": accepted.get("verbatimFeedback"),
                                  "imageSetSha256": accepted.get("imageSetSha256"), "currentImagesMatch": matches,
                                  "scope": accepted.get("scope")}
        status["deliveryState"] = "current_user_accepted_version_preserved" if matches else "changed_after_user_feedback"
    manifest = {**status, "canvas": [1024, 1024], "anchor": anchor,
                "sequences": sequences, "pngInventory": list(pngs.values())}
    preview = {"character": CHARACTER, "checkedAtUtc": checked, "counts": counts,
               "canvas": [1024, 1024], "anchor": anchor,
               "sequences": [{**seq, "frames": [{key: value for key, value in row.items() if key not in ("generationRecord", "selection")} for row in seq["frames"]]} for seq in sequences]}
    if "userFeedback" in status:
        preview["userFeedback"] = status["userFeedback"]
        preview["deliveryState"] = status["deliveryState"]
    return status, manifest, preview


def write_json(path: Path, value: dict) -> None:
    local(path).parent.mkdir(parents=True, exist_ok=True)
    local(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-reports", action="store_true", help="Write status.json, manifest.json, preview/data.js within this character only")
    args = parser.parse_args()
    status, manifest, preview = scan()
    if args.write_reports:
        write_json(ROOT / "status.json", status)
        write_json(ROOT / "manifest.json", manifest)
        path = local(ROOT / "preview" / "data.js")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("window.BAMBOO_PREVIEW = " + json.dumps(preview, ensure_ascii=False).replace("<", "\\u003c") + ";\n", encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"verify_inventory: {error}", file=sys.stderr)
        raise SystemExit(2)
