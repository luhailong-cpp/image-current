"""Inspect real runtime frames and derive inspection artifacts, never animation frames.

Run with bundled Python; Pillow is the only dependency. All output is confined to
this pet directory. --check-only writes nothing; the default writes preview/
artifacts. --manifest-out manifest.json is an explicit root-manifest opt-in.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT.parents[3]  # D:/work/image, only allowed source tree
SPECS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
PIVOT_TOP = [512, 942]
PIVOT_BOTTOM = [0.5, 0.08]
CONFIG_KEYS = ("model", "quality", "builtin_product", "verified_on", "sources")


def inside(path: Path, parent: Path) -> bool:
    return path.resolve().is_relative_to(parent.resolve())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_name(path: Path) -> str:
    return path.relative_to(ROOT).as_posix() if inside(path, ROOT) else path.as_posix()


def resolve_source(value: str, record: Path) -> Path | None:
    if not value or re.match(r"^(https?|data|blob):", value):
        return None
    candidate = Path(value)
    candidates = [candidate] if candidate.is_absolute() else [ROOT / candidate, record.parent / candidate, PROJECT / candidate]
    # Do not read another repository or computer, even if a record points there.
    safe = [p.resolve() for p in candidates if inside(p, PROJECT)]
    if not safe:
        return None
    return next((p for p in safe if p.exists()), safe[0])


def reference_strings(value):
    """Only known path-bearing keys, never arbitrary text or alleged instructions."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for entry in value:
            yield from reference_strings(entry)
    elif isinstance(value, dict):
        for key in ("path", "file", "image", "record", "generationRecord", "generation", "receipt", "prompt"):
            if isinstance(value.get(key), str):
                yield value[key]


def has_retained_deletion_evidence(source: Path | None) -> bool:
    """A historical generation reference may be removed by the retention policy.

    Require the cleanup inventory and its original generation record to agree;
    a missing reference alone is never accepted.
    """
    if source is None or not inside(source, ROOT):
        return False
    try:
        cleanup = json.loads((ROOT / "records/cleanup.json").read_text(encoding="utf-8"))
        relative = source.relative_to(ROOT).as_posix()
        deleted = next((e for e in cleanup["entries"] if e["file"] == relative), None)
        record = json.loads(source.with_name(source.name + ".generation.json").read_text(encoding="utf-8-sig"))
        return bool(deleted and deleted["sha256"] == record["sha256"]
                    and record.get("imageRetention", "").startswith("deleted after final export"))
    except (OSError, ValueError, KeyError, TypeError):
        return False


def read_record(path: Path, errors: list, warnings: list, seen=None) -> dict:
    seen = set() if seen is None else seen
    if path in seen:
        errors.append(f"Circular source record: {local_name(path)}")
        return {}
    seen.add(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError("record must be a JSON object")
    except (OSError, ValueError) as exc:
        errors.append(f"Unreadable generation record {local_name(path)}: {exc}")
        return {}
    if data.get("derivedFrom"):
        if not data.get("operation"):
            errors.append(f"Missing derivation operation: {local_name(path)}")
        entries = data["derivedFrom"]
        entries = entries if isinstance(entries, list) else [entries]
        for source in entries:
            if not isinstance(source, dict) or not source.get("sha256"):
                errors.append(f"derivedFrom must preserve source sha256: {local_name(path)}")
            if isinstance(source, dict):
                record_value = source.get("generationRecord") or source.get("record") or source.get("generation")
                if record_value:
                    src_record = resolve_source(record_value, path)
                    if src_record and src_record.is_file():
                        read_record(src_record, errors, warnings, seen.copy())
                    else:
                        errors.append(f"Missing/out-of-scope source generation record: {record_value}")
                else:
                    errors.append(f"Missing source generationRecord: {local_name(path)}")
                source_value = source.get("file") or source.get("path")
                if source_value:
                    src = resolve_source(source_value, path)
                    deleted = source.get("deleted") is True or source.get("removed") is True or source.get("status") == "deleted"
                    if src and src.is_file():
                        if source.get("sha256") != sha(src):
                            errors.append(f"Source sha256 mismatch: {source_value}")
                    elif deleted:
                        warnings.append(f"Source image removed with retained evidence: {source_value}")
                    else:
                        errors.append(f"Missing/out-of-scope source image without deletion record: {source_value}")
        return data
    required = ("file", "sha256", "generatedAt", "width", "height", "format", "tool", "route", "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt", "references")
    for key in required:
        if key not in data:
            errors.append(f"Missing {key}: {local_name(path)}")
    config = data.get("configSnapshot", {})
    for key in CONFIG_KEYS:
        if key not in config:
            errors.append(f"Missing configSnapshot.{key}: {local_name(path)}")
    params = data.get("submittedParameters", {})
    for key in ("model", "quality"):
        if key not in params:
            errors.append(f"Missing submittedParameters.{key}: {local_name(path)}")
    if data.get("actualModel") is None or data.get("actualQuality") is None:
        if not data.get("unverifiedReason"):
            errors.append(f"Unknown actual model/quality needs unverifiedReason: {local_name(path)}")
        else:
            warnings.append(f"Actual model/quality not fully disclosed: {local_name(path)}")
    try:
        stamp = datetime.fromisoformat(str(data.get("generatedAt", "")).replace("Z", "+00:00"))
        if stamp.utcoffset() is None:
            raise ValueError("timezone missing")
    except ValueError:
        errors.append(f"generatedAt must be ISO-8601 with timezone: {local_name(path)}")
    if not data.get("evidence"):
        errors.append(f"Missing tool evidence: {local_name(path)}")
    if not data.get("references"):
        errors.append(f"Missing identity/style references: {local_name(path)}")
    for field in ("prompt", "references", "evidence"):
        for value in reference_strings(data.get(field)):
            if re.match(r"^https?://", value):
                warnings.append(f"External evidence URL not fetched: {value}")
                continue
            # Inline evidence snippets are allowed; path checks only for recognizable paths.
            if field == "evidence" and not re.search(r"[\\/]|\.(json|txt|md|png|webp|jpe?g)$", value, re.I):
                continue
            source = resolve_source(value, path)
            if source is None or not source.is_file():
                if field == "references" and has_retained_deletion_evidence(source):
                    warnings.append(f"Historical reference image removed with verified retained evidence: {value}")
                else:
                    errors.append(f"Missing/out-of-scope {field} reference: {value}")
    return data


def scan() -> dict:
    errors, warnings, frames = [], [], []
    byte_hashes, pixel_hashes = {}, {}
    expected = set()
    for action, (count, duration) in SPECS.items():
        for direction in ("E", "W"):
            for index in range(1, count + 1):
                path = ROOT / "runtime" / action / direction / f"{index:02}.png"
                expected.add(path.resolve())
                entry = {"file": local_name(path), "action": action, "direction": direction, "frame": index,
                         "durationMs": duration, "pivotTopLeftPx": PIVOT_TOP, "pivotBottomLeftNormalized": PIVOT_BOTTOM,
                         "event": {("hit", 2): "contact", ("attack", 7): "impact", ("cast", 11): "release"}.get((action, index)),
                         "visualStatus": "pending-human-review", "exists": path.is_file()}
                if not path.is_file():
                    errors.append(f"Missing frame: {local_name(path)}")
                    frames.append(entry)
                    continue
                entry["sha256"] = sha(path)
                byte_hashes.setdefault(entry["sha256"], []).append(entry["file"])
                try:
                    with Image.open(path) as im:
                        im.load()
                        entry.update(width=im.width, height=im.height, mode=im.mode, format=im.format)
                        if im.format != "PNG" or im.mode != "RGBA" or im.size != (1024, 1024):
                            errors.append(f"Expected 1024x1024 RGBA PNG: {entry['file']} got {im.size}/{im.mode}/{im.format}")
                        rgba = im.convert("RGBA")
                        alpha = rgba.getchannel("A")
                        histogram = alpha.histogram()
                        entry["alpha"] = {"min": alpha.getextrema()[0], "max": alpha.getextrema()[1], "transparentPixels": histogram[0], "partialPixels": sum(histogram[1:255]), "opaquePixels": histogram[255], "bbox": alpha.getbbox()}
                        if not histogram[0] or not sum(histogram[1:]):
                            errors.append(f"Expected nonempty subject and real transparency: {entry['file']}")
                        bbox = alpha.getbbox()
                        if bbox and (bbox[0] == 0 or bbox[1] == 0 or bbox[2] == im.width or bbox[3] == im.height):
                            warnings.append(f"Nontransparent pixel reaches canvas edge; inspect crop: {entry['file']}")
                        entry["pixelSha256"] = hashlib.sha256(rgba.tobytes()).hexdigest()
                        pixel_hashes.setdefault(entry["pixelSha256"], []).append(entry["file"])
                except (OSError, ValueError) as exc:
                    errors.append(f"Cannot decode {entry['file']}: {exc}")
                records = [path.with_name(path.name + ".generation.json"), path.with_suffix(".generation.json")]
                existing = [p for p in records if p.is_file()]
                if len(existing) > 1:
                    errors.append(f"Ambiguous two generation records: {entry['file']}")
                if not existing:
                    errors.append(f"Missing generation record: {entry['file']}")
                else:
                    record = existing[0]
                    entry["generationRecord"] = local_name(record)
                    evidence = read_record(record, errors, warnings)
                    entry["actualModel"] = evidence.get("actualModel")
                    entry["actualQuality"] = evidence.get("actualQuality")
                    entry["source"] = evidence.get("derivedFrom") or evidence.get("references")
                    if evidence.get("sha256") != entry["sha256"]:
                        errors.append(f"Image/record sha256 mismatch: {entry['file']}")
                    if evidence.get("file"):
                        declared = resolve_source(evidence["file"], record)
                        if declared != path.resolve():
                            errors.append(f"Record file points to another image: {entry['file']}")
                    # Derived export native dimensions can differ; generation record refers to original.
                    if not evidence.get("derivedFrom") and (evidence.get("width"), evidence.get("height")) != (entry.get("width"), entry.get("height")):
                        errors.append(f"Native dimensions disagree with image: {entry['file']}")
                frames.append(entry)
    unexpected = sorted(local_name(p) for p in (ROOT / "runtime").rglob("*.png") if p.resolve() not in expected) if (ROOT / "runtime").exists() else []
    errors.extend(f"Unexpected runtime PNG: {p}" for p in unexpected)
    duplicates = [v for v in pixel_hashes.values() if len(v) > 1]
    errors.extend("Duplicate decoded RGBA frames: " + ", ".join(v) for v in duplicates)
    return {"schemaVersion": 1, "pet": "legacy-hu-tuan-tuan", "generatedAt": datetime.now(timezone.utc).isoformat(),
            "contract": {"frameCount": 68, "width": 1024, "height": 1024, "mode": "RGBA", "groups": {a: {"framesPerDirection": c, "durationMs": d} for a, (c, d) in SPECS.items()}, "directions": {"E": "front-three-quarter-facing-lower-right", "W": "true-back-three-quarter-facing-upper-left"}, "pivotTopLeftPx": PIVOT_TOP, "pivotBottomLeftNormalized": PIVOT_BOTTOM},
            "verification": {"technicalPassed": not errors, "presentFrames": sum(f["exists"] for f in frames), "expectedFrames": 68, "errors": errors, "warnings": sorted(set(warnings)), "pixelDuplicateGroups": duplicates,
                             "visualFrameReview": "pending-human-review", "animationPlaybackReview": "pending-human-review", "clientIntegration": "not-performed", "note": "Technical success never means visual or playback acceptance. No per-frame bbox alignment is applied."}, "frames": frames}


def contact_sheets(report: dict) -> None:
    destination = ROOT / "preview"
    thumb, label, columns = 224, 30, 4
    font = ImageFont.load_default()
    for action, (count, duration) in SPECS.items():
        for direction in ("E", "W"):
            selected = [f for f in report["frames"] if f["action"] == action and f["direction"] == direction]
            rows = (count + columns - 1) // columns
            sheet = Image.new("RGB", (columns * thumb, rows * (thumb + label)), "#ecebdc")
            draw = ImageDraw.Draw(sheet)
            for i, entry in enumerate(selected):
                x, y = (i % columns) * thumb, (i // columns) * (thumb + label)
                for cy in range(0, thumb, 16):
                    for cx in range(0, thumb, 16):
                        color = "#dddccb" if (cx // 16 + cy // 16) % 2 else "#f3f2e5"
                        draw.rectangle((x + cx, y + cy, x + min(cx + 15, thumb - 1), y + min(cy + 15, thumb - 1)), fill=color)
                if entry["exists"]:
                    try:
                        with Image.open(ROOT / entry["file"]) as im:
                            # Fixed full-canvas resize only. No bbox cropping, alignment, or altered pose.
                            tile = im.convert("RGBA").resize((thumb, thumb), Image.Resampling.LANCZOS)
                        sheet.paste(tile, (x, y), tile)
                    except OSError:
                        draw.text((x + 15, y + 95), "DECODE ERROR", fill="red", font=font)
                else:
                    draw.text((x + 15, y + 95), "MISSING", fill="red", font=font)
                px, py = x + thumb * .5, y + thumb * 942 / 1024
                draw.line((px - 5, py, px + 5, py), fill="#a64b70", width=1)
                draw.line((px, py - 5, px, py + 5), fill="#a64b70", width=1)
                draw.text((x + 5, y + thumb + 8), f"{action} {direction} {entry['frame']:02} / {count:02} | {duration}ms", fill="#222222", font=font)
            target = destination / f"contact-{action}-{direction}.png"
            sheet.save(target)
            (destination / f"contact-{action}-{direction}.png.derivation.json").write_text(json.dumps({"file": target.name, "sha256": sha(target), "operation": "Fixed full 1024x1024 canvas resized to 224x224 in labeled checkerboard contact sheet. No bbox re-alignment.", "derivedFrom": [{"file": f["file"], "sha256": f.get("sha256"), "generationRecord": f.get("generationRecord")} for f in selected if f["exists"]]}, ensure_ascii=False, indent=2), encoding="utf-8")


def preview_html(report: dict) -> None:
    template = (ROOT / "preview" / "template.html").read_text(encoding="utf-8")
    data = json.dumps(report, ensure_ascii=False).replace("<", "\\u003c")
    (ROOT / "preview" / "index.html").write_text(template.replace("__MANIFEST_JSON__", data), encoding="utf-8")


def main() -> int:
    # Windows的默认代码页可能无法输出中文验收结论；文件和终端统一UTF-8。
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Print report summary without writing any files")
    parser.add_argument("--manifest-out", default="preview/manifest-candidate.json", help="Manifest output relative to pet root (default: preview/manifest-candidate.json)")
    args = parser.parse_args()
    manifest = (ROOT / args.manifest_out).resolve()
    if not inside(manifest, ROOT):
        parser.error("--manifest-out must stay inside this pet directory")
    report = scan()
    visual_file = ROOT / 'records' / 'final-visual-review.json'
    if visual_file.is_file():
        visual = json.loads(visual_file.read_text(encoding='utf-8-sig'))
        reviewed = {f['file']: f['sha256'] for f in visual.get('frames', [])}
        if len(reviewed) == 68 and all(reviewed.get(f['file']) == f.get('sha256') for f in report['frames']):
            report['verification']['visualFrameReview'] = visual.get('individualFrameReview', 'pending-visual-review')
            report['verification']['animationPlaybackReview'] = visual.get('playbackReview', 'pending-visual-review')
            report['verification']['visualReviewRecord'] = 'records/final-visual-review.json'
            report['verification']['animationAcceptance'] = visual.get('animationAcceptance', 'not-recorded')
            report['verification']['unresolvedVisualIssues'] = visual.get('unresolvedVisualIssues', [])
            for frame in report['frames']:
                frame['visualStatus'] = visual.get('individualFrameReview', 'pending-visual-review')
    if not args.check_only:
        (ROOT / "preview").mkdir(exist_ok=True)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        contact_sheets(report)
        preview_html(report)
        (ROOT / "preview" / "checksums.sha256").write_text("".join(f"{f['sha256']}  {f['file']}\n" for f in report["frames"] if f.get("sha256")), encoding="utf-8")
    status = report["verification"]
    print(json.dumps({"presentFrames": status["presentFrames"], "expectedFrames": 68, "technicalPassed": status["technicalPassed"], "errorCount": len(status["errors"]), "warningCount": len(status["warnings"]), "errors": status["errors"], "warnings": status["warnings"], "visualReview": status["visualFrameReview"], "playbackReview": status["animationPlaybackReview"], "animationAcceptance": status.get("animationAcceptance", "not-recorded"), "unresolvedVisualIssues": status.get("unresolvedVisualIssues", []), "wroteArtifacts": not args.check_only}, ensure_ascii=False, indent=2))
    return 0 if status["technicalPassed"] else 1


if __name__ == "__main__":
    sys.exit(main())
