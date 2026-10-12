#!/usr/bin/env python3
"""Inspect existing AI frames and build a truthful, offline delivery inventory.

Run: python tools/build_delivery.py
No images are created or modified. This script only writes manifest.json,
validation.json, SHA256SUMS.txt and the data block in preview/index.html.
Python 3.9+ standard library only. An incomplete delivery returns 0 by default;
--strict returns 1 unless all 68 frames pass technical checks.
"""

import argparse
import hashlib
import json
import re
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path


ACTIONS = (("hit", "受击", 6, 40), ("attack", "普攻", 12, 30), ("cast", "施法", 16, 45))
ROOT = Path(__file__).resolve().parent.parent
DATA_START = "<!-- DELIVERY_DATA_START -->"
DATA_END = "<!-- DELIVERY_DATA_END -->"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path):
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def png_info(path):
    """Read dimensions, PNG integrity and alpha without installing Pillow.

    PNG filtering is independent per channel. Reconstructing only each RGBA
    pixel's alpha byte is sufficient for transparency and alpha bounds checks.
    """
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG file")
    offset, compressed, header, end = 8, bytearray(), None, False
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        if offset + length + 12 > len(data):
            raise ValueError("Truncated PNG chunk")
        expected_crc = struct.unpack(">I", data[offset + length + 8:offset + length + 12])[0]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != expected_crc:
            raise ValueError("PNG chunk CRC mismatch: " + kind.decode("ascii", "replace"))
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            end = True
            break
        offset += length + 12
    if not header or not end:
        raise ValueError("Missing PNG IHDR or IEND")
    width, height, depth, color, compression, filtering, interlace = header
    result = {"width": width, "height": height, "bitDepth": depth,
              "colorType": color, "mode": "RGBA" if color == 6 else "non-RGBA",
              "hasAlphaChannel": color == 6, "interlace": interlace}
    if (depth, color, compression, filtering, interlace) != (8, 6, 0, 0, 0):
        result["alphaInspectionError"] = "Expected non-interlaced 8-bit RGBA PNG"
        return result
    # Avoid decompressing an accidentally selected oversized source image.
    if (width, height) != (1024, 1024):
        result["alphaInspectionError"] = "Alpha inspection skipped: delivery size must be 1024 x 1024"
        return result
    raw = zlib.decompress(bytes(compressed))
    stride = width * 4 + 1
    if len(raw) != stride * height:
        raise ValueError("Unexpected decompressed PNG length")
    previous = bytearray(width)
    minimum, maximum, transparent, visible = 255, 0, 0, 0
    left, top, right, bottom = width, height, -1, -1
    for y in range(height):
        row_start = y * stride
        filter_type = raw[row_start]
        alpha = bytearray(raw[row_start + 4:row_start + stride:4])
        if filter_type == 1:
            for x in range(1, width):
                alpha[x] = (alpha[x] + alpha[x - 1]) & 255
        elif filter_type == 2:
            alpha = bytearray((value + previous[x]) & 255 for x, value in enumerate(alpha))
        elif filter_type == 3:
            for x in range(width):
                alpha[x] = (alpha[x] + ((alpha[x - 1] if x else 0) + previous[x]) // 2) & 255
        elif filter_type == 4:
            for x in range(width):
                a, b, c = (alpha[x - 1] if x else 0), previous[x], (previous[x - 1] if x else 0)
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                predictor = a if pa <= pb and pa <= pc else b if pb <= pc else c
                alpha[x] = (alpha[x] + predictor) & 255
        elif filter_type != 0:
            raise ValueError("Invalid PNG row filter")
        minimum, maximum = min(minimum, min(alpha)), max(maximum, max(alpha))
        row_transparent = alpha.count(0)
        transparent += row_transparent
        visible += width - row_transparent
        if row_transparent != width:
            xs = [x for x, value in enumerate(alpha) if value]
            left, right, top, bottom = min(left, xs[0]), max(right, xs[-1]), min(top, y), y
        previous = alpha
    result.update(alphaMin=minimum, alphaMax=maximum, transparentPixels=transparent,
                  visiblePixels=visible, hasTransparency=transparent > 0,
                  alphaBounds=[left, top, right + 1, bottom + 1] if visible else None)
    return result


def find_record(action, direction, number, image_path):
    stem = f"{number:02d}"
    candidates = [image_path.with_name(image_path.name + ".generation.json"),
                  image_path.with_suffix(".generation.json")]
    for directory in (ROOT / "records" / action / direction, image_path.parent):
        candidates.extend((directory / (stem + ".png.generation.json"),
                           directory / (stem + ".generation.json"),
                           directory / stem / "generation.json"))
    return next((path for path in candidates if path.is_file()), None)


def resolve_reference(value, record_path):
    path = Path(value)
    if path.is_absolute():
        return path
    candidates = (ROOT / path, record_path.parent / path)
    return next((candidate for candidate in candidates if candidate.is_file()), candidates[0])


def record_references(record, record_path):
    """Inspect explicit local path fields; do not interpret free prose as a path.

    Deleted native/intermediate sources are permitted only when their object
    says deleted/removed/retained:false AND retains a SHA-256 text record.
    URLs, data URLs and tool IDs are provenance, not local file references.
    """
    found = []
    path_keys = {"path", "file", "filepath", "sourcepath", "sourcefile", "recordpath",
                 "generationrecord", "receiptpath", "promptpath", "referencepath"}
    suffixes = (".png", ".webp", ".jpg", ".jpeg", ".json", ".txt", ".md", ".log")

    def walk(value, location="", parent=None):
        if isinstance(value, dict):
            for key, child in value.items():
                child_location = location + "." + key if location else key
                normalized = re.sub(r"[_-]", "", key).lower()
                if isinstance(child, str) and (normalized in path_keys or normalized in {"prompt", "receipt", "record"}):
                    if child.lower().startswith(("http://", "https://", "data:", "file://")):
                        continue
                    if "\n" in child or len(child) > 1000:
                        continue
                    if normalized in path_keys or child.lower().endswith(suffixes):
                        target = resolve_reference(child, record_path)
                        deleted = value.get("deleted") is True or value.get("removed") is True or value.get("retained") is False
                        source_hash = value.get("sha256") or value.get("sourceSha256")
                        retired = deleted and isinstance(source_hash, str) and bool(re.fullmatch(r"[0-9a-fA-F]{64}", source_hash))
                        found.append({"field": child_location, "path": child, "resolved": target.as_posix(),
                                      "exists": target.is_file(), "retiredWithSha256": retired})
                if isinstance(child, (dict, list)):
                    walk(child, child_location, value)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{location}[{index}]", parent)
    walk(record)
    return found


def hashes_in(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if "sha256" in key.lower() and isinstance(child, str):
                yield child.lower()
            elif isinstance(child, (dict, list)):
                yield from hashes_in(child)
    elif isinstance(value, list):
        for child in value:
            yield from hashes_in(child)


def events_from_poses():
    poses = ROOT / "POSES.md"
    events, action = {}, None
    if not poses.is_file():
        return events, "POSES.md missing"
    for line in poses.read_text(encoding="utf-8-sig").splitlines():
        heading = re.match(r"^##\s+(hit|attack|cast)\b", line)
        if heading:
            action = heading.group(1)
        row = re.match(r"^\|\s*(\d+)\s*\|.*?event:\s*([A-Za-z0-9_-]+)", line)
        if row and action:
            events[(action, int(row.group(1)))] = row.group(2)
    return events, None


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Exit 1 when technical delivery is incomplete or invalid")
    args = parser.parse_args()
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    events, poses_error = events_from_poses()
    visual_path = ROOT / "qa" / "final-visual-review.json"
    visual_report = json.loads(visual_path.read_text(encoding="utf-8")) if visual_path.is_file() else {}
    visual_frames = {item["path"]: item for item in visual_report.get("frames", [])}
    groups, all_frames, sums, hashes, problems = [], [], {}, {}, []
    if poses_error:
        problems.append({"code": "poses-missing", "detail": poses_error})
    if events.get(("attack", 8)) != "attack-contact" or events.get(("cast", 11)) != "cast-release":
        problems.append({"code": "poses-events", "detail": "Expected POSES attack frame 08 attack-contact and cast frame 11 cast-release"})
    for action, label, count, duration in ACTIONS:
        for direction in ("E", "W"):
            frames = []
            for number in range(1, count + 1):
                path = ROOT / "runtime" / action / direction / f"{number:02d}.png"
                frame = {"action": action, "direction": direction, "frame": number,
                         "path": rel(path), "exists": path.is_file(), "width": None, "height": None,
                         "durationMs": duration, "pivot": [0.5, 0.08], "anchor": [512, 942],
                         "event": events.get((action, number)), "sha256": None,
                         "sourceRecord": None, "visualStatus": "unverified",
                         "technicalStatus": "missing", "errors": [], "warnings": []}
                if not path.is_file():
                    frame["errors"].append("missing-frame")
                    frames.append(frame)
                    continue
                digest = sha256(path)
                frame["sha256"] = digest
                review = visual_frames.get(rel(path), {})
                evidence = review.get("evidence", [])
                if (review.get("sha256") == digest and review.get("staticStatus") == "reviewed"
                        and evidence and all((ROOT / item).is_file() for item in evidence)):
                    frame["visualStatus"] = "static-reviewed"
                    frame["visualEvidence"] = review.get("evidence", [])
                elif review:
                    frame["warnings"].append("visual-review-sha-mismatch-or-not-accepted")
                sums[rel(path)] = digest
                hashes.setdefault(digest, []).append(rel(path))
                try:
                    info = png_info(path)
                    frame.update(width=info["width"], height=info["height"], image=info)
                    if (info["width"], info["height"]) != (1024, 1024):
                        frame["errors"].append("size-not-1024")
                    if info["mode"] != "RGBA" or info["bitDepth"] != 8:
                        frame["errors"].append("not-8-bit-RGBA")
                    if "alphaInspectionError" in info:
                        frame["errors"].append("alpha-not-verified")
                    elif not info["hasTransparency"]:
                        frame["errors"].append("no-transparent-pixels")
                    elif info["visiblePixels"] == 0:
                        frame["errors"].append("empty-image")
                    if info.get("alphaBounds") and (info["alphaBounds"][0] == 0 or info["alphaBounds"][1] == 0 or
                                                    info["alphaBounds"][2] == 1024 or info["alphaBounds"][3] == 1024):
                        frame["warnings"].append("visible-alpha-touches-canvas-edge-review-crop")
                except (OSError, ValueError, struct.error, zlib.error) as exc:
                    frame["errors"].append("invalid-png: " + str(exc))
                record_path = find_record(action, direction, number, path)
                if not record_path:
                    frame["errors"].append("missing-generation-record")
                else:
                    frame["sourceRecord"] = rel(record_path)
                    sums[rel(record_path)] = sha256(record_path)
                    try:
                        record = json.loads(record_path.read_text(encoding="utf-8-sig"))
                        if not isinstance(record, dict):
                            raise ValueError("Generation record must be a JSON object")
                        references = record_references(record, record_path)
                        frame["sourceReferences"] = references
                        if any(not item["exists"] and not item["retiredWithSha256"] for item in references):
                            frame["errors"].append("broken-source-reference")
                        if digest not in set(hashes_in(record)):
                            frame["errors"].append("final-sha256-not-linked-in-record")
                        required = ("generatedAt", "tool", "route", "configSnapshot", "submittedParameters",
                                    "actualModel", "actualQuality", "evidence", "prompt", "references")
                        missing = [key for key in required if key not in record]
                        if missing:
                            frame["errors"].append("record-fields-missing: " + ", ".join(missing))
                        submitted = record.get("submittedParameters")
                        if not isinstance(submitted, dict) or not all(key in submitted for key in ("model", "quality")):
                            frame["errors"].append("record-submitted-model-quality-fields-missing")
                        if (record.get("actualModel") is None or record.get("actualQuality") is None) and not record.get("unverifiedReason"):
                            frame["errors"].append("unknown-model-quality-reason-missing")
                        frame["provenance"] = {key: record.get(key) for key in
                                               ("generatedAt", "tool", "route", "configSnapshot", "submittedParameters",
                                                "actualModel", "actualQuality", "unverifiedReason")}
                    except (OSError, ValueError, TypeError) as exc:
                        frame["errors"].append("invalid-generation-record: " + str(exc))
                frame["technicalStatus"] = "invalid" if frame["errors"] else "pass"
                frames.append(frame)
            groups.append({"id": f"{action}-{direction}", "action": action, "label": label,
                           "direction": direction, "expected": count, "present": sum(f["exists"] for f in frames),
                           "durationMs": duration, "totalDurationMs": count * duration, "frames": frames})
            all_frames.extend(frames)
    duplicates = [{"sha256": digest, "paths": paths} for digest, paths in hashes.items() if len(paths) > 1]
    for duplicate in duplicates:
        for frame in all_frames:
            if frame["path"] in duplicate["paths"]:
                frame["errors"].append("duplicate-frame-sha256")
                frame["technicalStatus"] = "invalid"
    expected_paths = {frame["path"] for frame in all_frames}
    extra = sorted(rel(path) for path in (ROOT / "runtime").rglob("*.png") if rel(path) not in expected_paths)
    present = sum(frame["exists"] for frame in all_frames)
    passed = sum(frame["technicalStatus"] == "pass" for frame in all_frames)
    status = "complete" if present == 68 and passed == 68 and not problems and not extra else "partial" if present < 68 else "invalid"
    counts = {"expected": 68, "present": present, "missing": 68 - present, "technicalPass": passed,
              "invalid": present - passed, "duplicateSets": len(duplicates), "extraPng": len(extra)}
    manifest = {"schemaVersion": 1, "id": "03-shuangtuan", "name": "霜团貂", "builtAt": timestamp,
                "status": status, "counts": counts, "coordinateOrigin": "top-left",
                "pivotOrigin": "bottom-left", "pivot": [0.5, 0.08], "anchor": [512, 942],
                "eventSource": "POSES.md", "framePathsRelativeTo": "pet-root",
                "visualReview": {"report": "qa/final-visual-review.json" if visual_report else None,
                                 "shaMatchedStaticFrames": sum(f["visualStatus"] == "static-reviewed" for f in all_frames),
                                 "scope": "Actual static visual-inspection evidence bound to the current image SHA; builder does not perform visual review.",
                                 "playbackReport": "qa/playback-status.json"}, "clientIntegration": "not-tested",
                "groups": groups}
    validation = {"schemaVersion": 1, "builtAt": timestamp, "status": status, "counts": counts,
                  "scope": "Technical file/provenance checks only; no anatomy, animation or client approval inferred.",
                  "missingFrames": [f["path"] for f in all_frames if not f["exists"]],
                  "invalidFrames": [{"path": f["path"], "errors": f["errors"]} for f in all_frames if f["exists"] and f["errors"]],
                  "warnings": [{"path": f["path"], "warnings": f["warnings"]} for f in all_frames if f["warnings"]],
                  "duplicateHashes": duplicates, "extraPng": extra, "problems": problems,
                  "visualInspection": "not-performed-by-builder", "continuousPlayback": "not-performed-by-builder",
                  "clientIntegration": "not-tested"}
    preview = ROOT / "preview" / "index.html"
    html = preview.read_text(encoding="utf-8")
    if html.count(DATA_START) != 1 or html.count(DATA_END) != 1:
        raise ValueError("preview/index.html must contain exactly one delivery data marker pair")
    snapshot = json.dumps(manifest, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    data_block = DATA_START + '\n<script type="application/json" id="delivery-data">' + snapshot + "</script>\n" + DATA_END
    html = html[:html.index(DATA_START)] + data_block + html[html.index(DATA_END) + len(DATA_END):]
    write_json(ROOT / "manifest.json", manifest)
    write_json(ROOT / "validation.json", validation)
    preview.write_text(html, encoding="utf-8")
    for file in (ROOT / "manifest.json", ROOT / "validation.json", ROOT / "POSES.md", ROOT / "tools" / "build_delivery.py",
                 preview, ROOT / "preview" / "preview.js", ROOT / "preview" / "preview.css",
                 visual_path, ROOT / "qa" / "playback-status.json", ROOT / "qa" / "animation-encoding.json",
                 ROOT / "qa" / "pixel-alpha-audit.json", ROOT / "preview" / "media-manifest.json",
                 ROOT / "preview" / "video" / "manifest.json", ROOT / "README.md", ROOT / "STATUS.md",
                 ROOT / "MERGE_HANDOFF.md", ROOT / "generation-index.md"):
        if file.is_file():
            sums[rel(file)] = sha256(file)
    for reviewed in visual_frames.values():
        for name in reviewed.get("evidence", []):
            evidence_file = ROOT / name
            if evidence_file.is_file():
                sums[rel(evidence_file)] = sha256(evidence_file)
    for directory in (ROOT / "preview" / "media", ROOT / "preview" / "video", ROOT / "qa" / "contact"):
        for file in directory.iterdir():
            if file.is_file():
                sums[rel(file)] = sha256(file)
    for file in (ROOT / "qa").rglob("*cleanup*.json"):
        sums[rel(file)] = sha256(file)
    (ROOT / "SHA256SUMS.txt").write_text("".join(f"{sums[name]}  {name}\n" for name in sorted(sums)), encoding="utf-8")
    print(json.dumps({"status": status, **counts, "preview": str(preview)}, ensure_ascii=False))
    return 1 if args.strict and status != "complete" else 0


if __name__ == "__main__":
    raise SystemExit(main())
