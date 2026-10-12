"""Validate eight reviewed grounding selections; merge only with --write.

This does not render, edit, fit, align, interpolate, or approve any artwork.
Run export_selected.py and the preview/check refresh chain after a successful merge.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
SELECTION_NAME = "selection-middle4-side2-20261004.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(value):
    path = Path(str(value).replace("\\", "/"))
    path = (path if path.is_absolute() else ROOT / path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Path escapes character directory: {path}")
    return path


def first(row, keys):
    return next((row[key] for key in keys if row.get(key) is not None), None)


def slot_number(row):
    value = first(row, ("frame", "slot", "frameNumber"))
    if isinstance(value, str):
        value = Path(value.replace("\\", "/")).stem
    if isinstance(value, bool):
        raise ValueError("Boolean is not a frame number")
    return int(value)


def write_json(path, value):
    temporary = path.with_name(path.name + ".merge-tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_direction(direction, seen_files, seen_pixels):
    path = ROOT / "generation/run" / direction / SELECTION_NAME
    document = read(path)
    metadata = document if isinstance(document, dict) else {}
    rows = document if isinstance(document, list) else document.get("frames", document.get("selection"))
    if not isinstance(rows, list) or len(rows) != 16:
        raise ValueError(f"Expected exactly 16 rows: {path}")
    if metadata.get("direction", direction) != direction:
        raise ValueError(f"Direction mismatch in {path}")
    numbers = [slot_number(row) for row in rows]
    if sorted(numbers) != list(range(1, 17)):
        raise ValueError(f"Duplicate/missing slots in {path}: {numbers}")
    result = []
    for row in sorted(rows, key=slot_number):
        n = slot_number(row)
        key = f"run/{direction}/{n:02d}"
        if row.get("action", "run") != "run" or row.get("direction", direction) != direction:
            raise ValueError(f"Action/direction mismatch at {key}")
        source_value = first(row, ("source", "sourcePath", "source_path"))
        if not source_value:
            raise ValueError(f"Missing native source at {key}")
        source = local(source_value)
        if not source.is_relative_to((ROOT / "generation/run" / direction).resolve()):
            raise ValueError(f"Native source outside intended direction at {key}: {source}")
        actual_sha = sha(source)
        declared_sha = first(row, ("sourceSha256", "source_sha256", "sha256"))
        if declared_sha != actual_sha:
            raise ValueError(f"Missing/mismatched selected source SHA at {key}")
        record_value = first(row, ("generationRecord", "generationRecordPath", "record"))
        record_path = local(record_value) if record_value else Path(str(source) + ".generation.json")
        record = read(record_path)
        if record.get("sha256") != actual_sha:
            raise ValueError(f"Native generation record SHA mismatch at {key}")
        if record.get("route") == "derived" or record.get("derivedFrom") or record.get("operation"):
            raise ValueError(f"Derived image supplied as native at {key}")
        if record.get("route") != "builtin" or record.get("tool") not in ("image_gen.imagegen", "image_gen"):
            raise ValueError(f"Unexpected native image route at {key}")
        with Image.open(source) as im:
            if im.format != "PNG" or im.mode != "RGBA" or im.size != (1254, 1254):
                raise ValueError(f"Expected native 1254x1254 RGBA PNG at {key}")
            im.load()
            if im.getchannel("A").getextrema()[1] == 0:
                raise ValueError(f"Empty native image at {key}")
            pixels_sha = hashlib.sha256(im.tobytes()).hexdigest()
        for value, seen, kind in ((actual_sha, seen_files, "file"), (pixels_sha, seen_pixels, "pixels")):
            if value in seen:
                raise ValueError(f"Duplicate native {kind} in {seen[value]} and {key}")
            seen[value] = key
        support = "right" if n <= 8 else "left"
        pair_number = ((n - 1) % 8) // 2 + 1
        position = f"position_{pair_number}"
        if row.get("supportFoot", support) != support:
            raise ValueError(f"Unexpected support foot at {key}")
        declared_position = first(row, ("position", "supportPositionAlongRun"))
        # Earlier front/middle/rear labels remain historical observations.
        # Current timing uses successive two-frame positions, not a four-frame hold.
        duration = first(row, ("durationMs", "frameDurationMs"))
        if duration is not None and duration != 60:
            raise ValueError(f"Unexpected duration at {key}")
        observation = row.get("observation")
        if not observation:
            raise ValueError(f"Missing per-slot static observation at {key}")
        result.append({**row, "action": "run", "direction": direction, "frame": n,
                       "source": source.relative_to(ROOT).as_posix(),
                       "sourceSha256": actual_sha, "nativePixelSha256": pixels_sha,
                       "generationRecord": record_path.relative_to(ROOT).as_posix(),
                       "supportFoot": support, "position": position,
                       "legacyPositionObservation": declared_position,
                       "positionPair": pair_number,
                       "durationMs": 60, "nativeSize": [1254, 1254],
                       "status": row.get("status", metadata.get("status", "static_candidate_dynamic_unverified")),
                       "observation": "相邻支撑位置各两张独立姿态，依跑向逐步推进；60ms/帧；静态复核不等于动态接地通过。 " + observation if "flow-" in source.name or "axis-" in source.name else "相邻支撑位置各两张独立姿态，依跑向逐步推进；60ms/帧；静态复核不等于动态接地通过。",
                       "legacyObservation": observation, "dynamicVerified": False,
                       "reviewedSelection": path.relative_to(ROOT).as_posix(),
                       "reviewedSelectionSha256": sha(path)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="After all checks pass, replace selected-new.json and save merge report")
    args = parser.parse_args()
    target = ROOT / "selected-new.json"
    original_sha = sha(target)
    original = read(target)
    if not isinstance(original, list):
        raise ValueError("selected-new.json must be a list")
    old_keys = [(r["action"], r["direction"], r["frame"]) for r in original]
    if len(set(old_keys)) != len(old_keys):
        raise ValueError("Existing selection has duplicate slots")
    seen_files, seen_pixels = {}, {}
    replacements = [row for direction in DIRECTIONS for row in load_direction(direction, seen_files, seen_pixels)]
    replacement_by_key = {(r["action"], r["direction"], r["frame"]): r for r in replacements}
    if not set(replacement_by_key).issubset(set(old_keys)):
        raise ValueError("Existing selection is missing one or more run slots")
    merged = [replacement_by_key.get((r["action"], r["direction"], r["frame"]), r) for r in original]
    timing = read(ROOT / "run-timing.json")
    if timing["cycleDurationMs"] != 960 or set(timing["durationsByDirection"]) != set(DIRECTIONS) or any(v != [60] * 16 for v in timing["durationsByDirection"].values()):
        raise ValueError("Expected all eight directions at 16x60ms = 960ms")
    changes = [{"action": before["action"], "direction": before["direction"], "frame": before["frame"],
                "before": before["source"], "after": after["source"], "sourceSha256": after["sourceSha256"]}
               for before, after in zip(original, merged)
               if before["source"] != after["source"]]
    report = {"createdAt": datetime.now(timezone.utc).isoformat(), "status": "merged" if args.write else "validated_only",
              "selectedBeforeSha256": original_sha, "directions": list(DIRECTIONS), "nativeFrames": 128,
              "preservedOtherActionSlots": len(original) - 128, "changedSources": len(changes),
              "changes": changes, "frames": replacements,
              "dynamicVisualVerified": False, "clientIntegrated": False,
              "note": "Native files and evidence validated. Static observations are carried from direction reviews; pair labels do not independently prove grounding."}
    if args.write:
        if sha(target) != original_sha:
            raise ValueError("Global selection changed during validation; rerun before writing")
        write_json(target, merged)
        report["selectedAfterSha256"] = sha(target)
        write_json(ROOT / "review/grounding-fourframes/selection-merge-middle4-side2.json", report)
    print(json.dumps({k: report[k] for k in ("status", "nativeFrames", "preservedOtherActionSlots", "changedSources")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
