#!/usr/bin/env python3
"""Audit existing combat sprites and create inspection aids; never edits runtime art."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ACTIONS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}
DIRECTIONS = ("E", "W")
PIVOT = [0.5, 0.08]
ANCHOR = [512, 942]
TOOL_NOTE = "Technical checks only; art, animation, and client integration require separate review."


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_output(value: str) -> Path:
    path = Path(value)
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Outputs must remain inside the assigned character directory")
    return path


def resolve_link(value: str, record: Path) -> Path:
    p = Path(value)
    if p.is_absolute():
        return p
    candidates = (ROOT / p, record.parent / p)
    return next((c.resolve() for c in candidates if c.exists()), candidates[0].resolve())


def issue(items: list, level: str, code: str, file: str, detail: Any) -> None:
    items.append({"level": level, "code": code, "file": file, "detail": detail})


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def match_record(data: Any, frame: Path, record: Path) -> dict | None:
    if isinstance(data, dict):
        field = data.get("file") or data.get("outputFile") or data.get("output")
        if isinstance(field, str) and resolve_link(field, record) == frame.resolve():
            return data
        for key, value in data.items():
            if isinstance(value, dict) and key.replace("\\", "/") == rel(frame):
                return value
            if isinstance(value, (list, dict)):
                found = match_record(value, frame, record)
                if found is not None:
                    return found
    elif isinstance(data, list):
        for value in data:
            found = match_record(value, frame, record)
            if found is not None:
                return found
    return None


def find_record(frame: Path, central: list[Path]) -> tuple[Path | None, dict | None, str | None]:
    for path in (Path(str(frame) + ".generation.json"), frame.with_suffix(".generation.json")):
        if path.exists():
            try:
                data = read_json(path)
                return path, data if isinstance(data, dict) else None, None
            except (OSError, ValueError) as exc:
                return path, None, str(exc)
    for path in central:
        try:
            found = match_record(read_json(path), frame, path)
            if found is not None:
                return path, found, None
        except (OSError, ValueError):
            continue
    return None, None, None


def check_generation(data: dict, record: Path, items: list, visited: set[str] | None = None) -> dict:
    """Return evidence summary, following derivation records without inventing metadata."""
    visited = set() if visited is None else visited
    key = str(record.resolve())
    if key in visited:
        issue(items, "error", "source_cycle", rel(record), key)
        return {}
    visited.add(key)
    source = data.get("derivedFrom")
    if source:
        if not data.get("operation"):
            issue(items, "error", "missing_derivation_operation", rel(record), None)
        sources = source if isinstance(source, list) else [source]
        summaries = []
        for entry in sources:
            if not isinstance(entry, dict):
                issue(items, "error", "invalid_derived_source", rel(record), entry)
                continue
            src_hash = entry.get("sha256") or entry.get("sourceSha256")
            src_file = entry.get("file") or entry.get("path") or entry.get("source")
            src_record = entry.get("generationRecord") or entry.get("generation") or entry.get("record")
            if not src_hash or len(str(src_hash)) != 64:
                issue(items, "error", "missing_source_sha256", rel(record), src_file)
            if isinstance(src_file, str):
                p = resolve_link(src_file, record)
                if p.exists() and src_hash and digest(p) != src_hash:
                    issue(items, "error", "source_sha256_mismatch", rel(record), src_file)
                if not p.exists() and not (entry.get("deleted") or entry.get("removedAfterExport") or data.get("sourceCleanup")):
                    issue(items, "warning", "source_file_absent_cleanup_unrecorded", rel(record), src_file)
            else:
                issue(items, "error", "missing_source_path", rel(record), None)
            if isinstance(src_record, str):
                p = resolve_link(src_record, record)
                if p.exists():
                    try:
                        native = read_json(p)
                        if not isinstance(native, dict):
                            raise ValueError("source record must be an object")
                        summaries.append(check_generation(native, p, items, visited.copy()))
                    except (OSError, ValueError) as exc:
                        issue(items, "error", "invalid_source_record", rel(record), str(exc))
                else:
                    issue(items, "error", "missing_source_record", rel(record), src_record)
            elif isinstance(src_record, dict):
                summaries.append(check_generation(src_record, record.with_name(record.name + ".embedded"), items, visited.copy()))
            else:
                issue(items, "error", "missing_source_record_link", rel(record), src_file)
        return {"kind": "derived", "record": rel(record), "sources": summaries, "operation": data.get("operation")}

    required = ("file", "sha256", "generatedAt", "width", "height", "format", "tool", "route", "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt", "references")
    for field in required:
        if field not in data:
            issue(items, "error", "generation_field_missing", rel(record), field)
    parameters = data.get("submittedParameters")
    if not isinstance(parameters, dict) or not all(k in parameters for k in ("model", "quality")):
        issue(items, "error", "submitted_model_quality_not_explicit", rel(record), None)
    snapshot = data.get("configSnapshot")
    if not isinstance(snapshot, dict) or not all(k in snapshot for k in ("model", "quality", "builtin_product", "verified_on", "sources")):
        issue(items, "error", "config_snapshot_incomplete", rel(record), None)
    if (data.get("actualModel") is None or data.get("actualQuality") is None) and not data.get("unverifiedReason"):
        issue(items, "error", "unknown_model_quality_reason_missing", rel(record), None)
    if not data.get("evidence"):
        issue(items, "error", "generation_evidence_empty", rel(record), None)
    prompt = data.get("prompt")
    if isinstance(prompt, str):
        prompt_file = resolve_link(prompt, record)
        if not prompt_file.is_file():
            issue(items, "error", "missing_prompt_file", rel(record), prompt)
    else:
        issue(items, "error", "prompt_path_missing", rel(record), prompt)
    references = data.get("references")
    if not isinstance(references, list) or not references:
        issue(items, "error", "references_missing", rel(record), None)
    else:
        for reference in references:
            name = reference if isinstance(reference, str) else reference.get("file") or reference.get("path")
            if not isinstance(name, str) or not resolve_link(name, record).is_file():
                issue(items, "error", "missing_reference_file", rel(record), name)
            if isinstance(reference, dict) and not (reference.get("purpose") or reference.get("role")):
                issue(items, "warning", "reference_purpose_missing", rel(record), name)
    return {"kind": "generated", "record": rel(record), "target": data.get("configSnapshot"), "submittedParameters": parameters, "actualModel": data.get("actualModel"), "actualQuality": data.get("actualQuality"), "unverifiedReason": data.get("unverifiedReason"), "prompt": prompt, "references": references, "evidence": data.get("evidence")}


def audit() -> tuple[dict, dict]:
    items, frames = [], []
    central = sorted(p for p in ROOT.rglob("generation.json") if "preview" not in p.parts)
    file_hashes, pixel_hashes = {}, {}
    expected = set()
    for action, (count, duration) in ACTIONS.items():
        for direction in DIRECTIONS:
            for number in range(1, count + 1):
                name = f"runtime/{action}/{direction}/{number:02}.png"
                expected.add(name)
                frame = ROOT / name
                event = "impact" if action == "attack" and number == 7 else "release" if action == "cast" and number == 10 else None
                entry = {"file": name, "action": action, "direction": direction, "frame": number, "durationMs": duration, "pivot": PIVOT, "anchorTopLeftPx": ANCHOR, "event": event, "visualStatus": "pending_manual_review", "exists": frame.is_file()}
                if not frame.is_file():
                    issue(items, "error", "missing_frame", name, None)
                    frames.append(entry)
                    continue
                sha = digest(frame)
                entry["sha256"] = sha
                file_hashes.setdefault(sha, []).append(name)
                try:
                    with Image.open(frame) as im:
                        im.load()
                        entry.update(width=im.width, height=im.height, mode=im.mode, format=im.format)
                        if im.format != "PNG" or im.mode != "RGBA" or im.size != (1024, 1024):
                            issue(items, "error", "invalid_image_contract", name, {"format": im.format, "mode": im.mode, "size": list(im.size)})
                        rgba = im.convert("RGBA")
                        pixels_sha = hashlib.sha256(rgba.tobytes()).hexdigest()
                        entry["pixelSha256"] = pixels_sha
                        pixel_hashes.setdefault(pixels_sha, []).append(name)
                        alpha = rgba.getchannel("A")
                        hist = alpha.histogram()
                        bbox = alpha.getbbox()
                        total = im.width * im.height
                        edge_boxes = [(0, 0, im.width, 1), (0, im.height - 1, im.width, im.height)]
                        if im.height > 2:
                            edge_boxes += [(0, 1, 1, im.height - 1), (im.width - 1, 1, im.width, im.height - 1)]
                        edge_hist = [sum(values) for values in zip(*(alpha.crop(box).histogram() for box in edge_boxes))]
                        edge_nonzero = sum(edge_hist[1:])
                        edge_visible = sum(edge_hist[16:])
                        solid_bbox = alpha.point(lambda a: 255 if a >= 16 else 0).getbbox()
                        entry["alpha"] = {"min": alpha.getextrema()[0], "max": alpha.getextrema()[1], "transparentPixels": hist[0], "opaquePixels": hist[255], "partialPixels": total - hist[0] - hist[255], "nonzeroBoundingBox": list(bbox) if bbox else None, "visibleBoundingBoxAlpha16": list(solid_bbox) if solid_bbox else None, "edgeNontransparentPixels": edge_nonzero, "edgeVisiblePixelsAlpha16": edge_visible, "edgeMaxAlpha": max(i for i, value in enumerate(edge_hist) if value)}
                        if bbox is None:
                            issue(items, "error", "empty_alpha", name, None)
                        if hist[0] == 0:
                            issue(items, "error", "no_fully_transparent_background", name, None)
                        if hist[255] == 0:
                            issue(items, "warning", "no_fully_opaque_pixels", name, None)
                        if edge_nonzero:
                            issue(items, "warning", "alpha_touches_canvas_edge_check_clipping", name, edge_nonzero)
                except (OSError, ValueError) as exc:
                    issue(items, "error", "unreadable_image", name, str(exc))
                record, data, error = find_record(frame, central)
                entry["generationRecord"] = rel(record) if record else None
                if error or (record and data is None):
                    issue(items, "error", "invalid_generation_record", name, error)
                elif data is None:
                    issue(items, "error", "missing_generation_record", name, None)
                else:
                    if not isinstance(data.get("file"), str) or resolve_link(data["file"], record) != frame.resolve():
                        issue(items, "error", "generation_file_link_mismatch", name, data.get("file"))
                    if data.get("sha256") != sha:
                        issue(items, "error", "generation_sha256_mismatch", name, data.get("sha256"))
                    entry["source"] = check_generation(data, record, items)
                frames.append(entry)
    extras = sorted(rel(p) for p in (ROOT / "runtime").rglob("*.png") if rel(p) not in expected) if (ROOT / "runtime").exists() else []
    for name in extras:
        issue(items, "warning", "unexpected_runtime_png", name, None)
    duplicate_files = [v for v in file_hashes.values() if len(v) > 1]
    duplicate_pixels = [v for v in pixel_hashes.values() if len(v) > 1]
    for group in duplicate_pixels:
        issue(items, "error", "duplicate_pixel_content", group[0], group)
    now = stamp()
    manifest = {"schemaVersion": 1, "character": "玄潮龟", "slug": "10-xuanchaogui", "generatedAt": now, "expectedFrames": 68, "availableFrames": sum(f["exists"] for f in frames), "directions": {"E": "斜前朝右下", "W": "独立斜后朝左上"}, "canvas": {"width": 1024, "height": 1024, "mode": "RGBA", "anchorTopLeftPx": ANCHOR, "pivotBottomLeft": PIVOT}, "actions": {a: {"framesPerDirection": n, "durationMs": d, "groupDurationMs": n * d} for a, (n, d) in ACTIONS.items()}, "review": {"technical": "see validation.json", "visual": "pending_manual_review", "animation": "pending_manual_review", "clientIntegration": "not_performed", "note": TOOL_NOTE}, "frames": frames}
    errors = sum(i["level"] == "error" for i in items)
    warnings = sum(i["level"] == "warning" for i in items)
    validation = {"schemaVersion": 1, "checkedAt": now, "scope": "existing runtime files and their provenance; no generated or modified poses", "expectedFrames": 68, "availableFrames": manifest["availableFrames"], "technicalStatus": "fail" if errors else "pass_with_warnings" if warnings else "pass", "errors": errors, "warnings": warnings, "duplicateFileSha256Groups": duplicate_files, "duplicatePixelSha256Groups": duplicate_pixels, "extraRuntimeFiles": extras, "issues": items, "manualReview": {"allFrames": "pending", "normalPlayback": "pending", "quarterSpeedPlayback": "pending", "anatomyAndProps": "pending", "directionAndReturnPose": "pending"}, "clientIntegration": "not_performed", "limitations": [TOOL_NOTE, "Pixel hashes detect exact duplicates, not mirrored, shifted or interpolated copies.", "Transparent borders and bounding boxes cannot prove anatomical correctness or motion continuity."]}
    return manifest, validation


def contact_sheets() -> list[str]:
    """Inspection aid only: thumbnails may resize the existing pixels; runtime is untouched."""
    destination = ROOT / "preview" / "contact-sheets"
    destination.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16) if Path("C:/Windows/Fonts/arial.ttf").exists() else ImageFont.load_default()
    created = []
    for action, (count, duration) in ACTIONS.items():
        for direction in DIRECTIONS:
            sheet = Image.new("RGB", (4 * 256, 62 + math.ceil(count / 4) * 288), "#171d29")
            draw = ImageDraw.Draw(sheet)
            draw.text((14, 9), f"INSPECTION AID ONLY | {action} {direction} | {count} frames x {duration} ms", fill="white", font=font)
            draw.text((14, 33), "Thumbnails only. Missing frames are labeled. No artistic approval implied.", fill="#b4c2d8", font=font)
            for i in range(count):
                x, y = (i % 4) * 256, 62 + (i // 4) * 288
                for cy in range(0, 256, 16):
                    for cx in range(0, 256, 16):
                        draw.rectangle((x + cx, y + cy, x + cx + 15, y + cy + 15), fill="#e5e9ee" if (cx + cy) % 32 else "#b7c3cf")
                p = ROOT / "runtime" / action / direction / f"{i+1:02}.png"
                status = "MISSING"
                if p.exists():
                    try:
                        with Image.open(p) as im:
                            thumb = im.convert("RGBA")
                            thumb.thumbnail((256, 256), Image.Resampling.LANCZOS)
                            sheet.paste(thumb, (x + (256 - thumb.width) // 2, y + (256 - thumb.height) // 2), thumb)
                        status = ""
                    except OSError:
                        status = "UNREADABLE"
                draw.text((x + 10, y + 263), f"{action}/{direction}/{i+1:02}  {status}", fill="#ffadad" if status else "white", font=font)
            p = destination / f"{action}-{direction}.jpg"
            sheet.save(p, quality=92, subsampling=0)
            created.append(rel(p))
    return created


def html_preview() -> None:
    groups = [{"action": a, "direction": d, "count": n, "duration": ms} for a, (n, ms) in ACTIONS.items() for d in DIRECTIONS]
    path = ROOT / "preview" / "index.html"
    template = (ROOT / "tools" / "preview.template.html").read_text(encoding="utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(template.replace("__GROUPS_JSON__", json.dumps(groups)), encoding="utf-8")


def apply_visual_review(manifest: dict, validation: dict) -> None:
    """Reuse a separately recorded human review only for exactly the reviewed art."""
    path = ROOT / "visual-review.json"
    if not path.exists():
        return
    review = read_json(path)
    current = {f["file"]: f.get("sha256") for f in manifest["frames"]}
    valid = review.get("frameSha256") == current and not validation["errors"]
    validation["visualReviewRecord"] = "visual-review.json"
    validation["visualReviewHashesMatch"] = valid
    if not valid:
        validation["limitations"].append("Stored visual review is stale; current PNG hashes require fresh review.")
        return
    validation["manualReview"] = review["checks"]
    manifest["review"].update(visual=review["visualStatus"], animation=review["animationStatus"], record="visual-review.json")
    for frame in manifest["frames"]:
        frame["visualStatus"] = review["visualStatus"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="preview/audit", help="Audit JSON directory relative to character root; use '.' for delivery manifest.json and validation.json")
    parser.add_argument("--preview-only", action="store_true", help="Only write the HTML viewer; no audit JSON or contact sheets")
    parser.add_argument("--no-contact-sheets", action="store_true", help="Skip derived inspection thumbnails")
    args = parser.parse_args()
    html_preview()
    if args.preview_only:
        print(f"Preview ready: {ROOT / 'preview' / 'index.html'}")
        return 0
    output = safe_output(args.output_dir)
    manifest, validation = audit()
    apply_visual_review(manifest, validation)
    if not args.no_contact_sheets:
        validation["inspectionContactSheets"] = contact_sheets()
    write_json(output / "manifest.json", manifest)
    write_json(output / "validation.json", validation)
    print(json.dumps({"output": str(output), "availableFrames": manifest["availableFrames"], "expectedFrames": 68, "technicalStatus": validation["technicalStatus"], "errors": validation["errors"], "warnings": validation["warnings"]}, ensure_ascii=False))
    return 1 if validation["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
