"""Read-only runtime audit; writes QA, optional contact sheets and manifest.

No image generation, frame synthesis, transforms, or runtime edits occur here.
Run from any directory. --manifest is intentionally opt-in.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont
from playback_evidence import load_playback_review, PLAYBACK_RECORD, PLAYBACK_SEQUENCE, PENDING_SEQUENCE

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[3]
ACTIONS = {"hit": (6, 40, 3, "impact"), "attack": (12, 30, 7, "attack"), "cast": (16, 45, 10, "cast")}
DIRECTIONS = {"E": "斜前朝右下", "W": "斜后朝左上"}
PIVOT = [0.5, 0.08]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reference_path(raw, record: Path) -> Path | None:
    if not isinstance(raw, str) or not raw or raw.startswith(("http:", "https:", "data:")):
        return None
    p = Path(raw)
    if p.is_absolute():
        return p.resolve()
    choices = [ROOT / p, record.parent / p, PROJECT / p]
    return next((c.resolve() for c in choices if c.exists()), choices[0].resolve())


def allowed_reference(path: Path) -> bool:
    # Check only this pet and the specifically authorized shared inputs.
    permitted = [ROOT, PROJECT / "designs/pets-xianling-20260924/source",
                 PROJECT / "designs/attribute-panels/v2-painted",
                 PROJECT / "config", PROJECT / "docs"]
    return any(path == base or base in path.parents for base in permitted)


def source_record(path: Path, action: str, direction: str, n: int) -> Path | None:
    candidates = [Path(str(path) + ".generation.json"), path.with_suffix(".generation.json")]
    for folder in ("records", "source-records", "sources", "generation"):
        candidates += [ROOT / folder / f"{action}-{direction}-{n:02d}.json",
                       ROOT / folder / action / direction / f"{n:02d}.json",
                       ROOT / folder / action / direction / f"{n:02d}.png.generation.json"]
    return next((p for p in candidates if p.is_file()), None)


def audit_record(record: Path | None, image_path: Path, image_sha: str, errors: list, warnings: list) -> dict:
    if record is None:
        errors.append("missing_source_record")
        return {"path": None, "status": "missing"}
    out = {"path": relative(record), "sha256": sha(record), "status": "checked", "references": []}
    try:
        data = json.loads(record.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        errors.append("invalid_source_record_json")
        out.update(status="invalid", detail=str(exc))
        return out
    if not isinstance(data, dict):
        errors.append("source_record_not_object")
        out["status"] = "invalid"
        return out
    required = ["file", "sha256", "generatedAt", "tool", "route", "configSnapshot",
                "submittedParameters", "actualModel", "actualQuality", "evidence", "prompt", "references"]
    for key in required:
        if key not in data:
            errors.append(f"source_record_missing:{key}")
    if str(data.get("sha256", "")).lower() != image_sha:
        errors.append("source_record_sha_mismatch")
    file_path = reference_path(data.get("file"), record)
    if file_path is not None and file_path != image_path.resolve():
        errors.append("source_record_file_mismatch")
    snapshot = data.get("configSnapshot", {})
    if not isinstance(snapshot, dict) or not all(k in snapshot for k in ("model", "quality", "builtin_product", "verified_on", "sources")):
        errors.append("source_record_incomplete_config_snapshot")
    submitted = data.get("submittedParameters", {})
    if not isinstance(submitted, dict) or not all(k in submitted for k in ("model", "quality")):
        errors.append("source_record_incomplete_submitted_parameters")
    if data.get("actualModel") is None or data.get("actualQuality") is None:
        out["actualModelQualityStatus"] = "unconfirmed"
        if not data.get("unverifiedReason"):
            errors.append("source_record_unknown_model_quality_without_reason")
    else:
        out["actualModelQualityStatus"] = "reported_in_source_record_not_independently_verified"
    refs = [("prompt", data.get("prompt"))]
    evidence = data.get("evidence", {})
    if isinstance(evidence, dict):
        for key in ("receipt", "toolResult", "metadata"):
            value = evidence.get(key)
            if isinstance(value, str) and value.lower().endswith((".json", ".txt")):
                refs.append((f"evidence:{key}", value))
    edit_target = data.get("editTarget", {})
    if isinstance(edit_target, dict) and edit_target.get("generationRecord"):
        refs.append(("editTarget:generationRecord", edit_target["generationRecord"]))
    references = data.get("references", [])
    if isinstance(references, list):
        for idx, ref in enumerate(references):
            raw = ref.get("path", ref.get("file")) if isinstance(ref, dict) else ref
            refs.append((f"reference:{idx}", raw))
    else:
        errors.append("source_record_references_not_array")
    for label, raw in refs:
        if label == "prompt" and isinstance(raw, str) and ("\n" in raw or len(raw) > 500):
            out["references"].append({"kind": label, "status": "embedded_text"})
            continue
        target = reference_path(raw, record)
        if target is None:
            # Some records embed prompt text instead of a prompt file.
            if label == "prompt" and isinstance(raw, str) and len(raw) > 100:
                out["references"].append({"kind": label, "status": "embedded_text"})
            else:
                errors.append(f"source_record_invalid_reference:{label}")
            continue
        if not allowed_reference(target):
            warnings.append(f"reference_outside_audit_scope:{label}")
            out["references"].append({"kind": label, "path": str(raw), "status": "outside_audit_scope"})
        else:
            exists = target.is_file()
            out["references"].append({"kind": label, "path": relative(target), "exists": exists})
            if not exists:
                errors.append(f"missing_current_reference:{label}")
    out["actualModel"] = data.get("actualModel")
    out["actualQuality"] = data.get("actualQuality")
    out["configTarget"] = snapshot
    return out


def audit_frame(action: str, direction: str, n: int) -> dict:
    count, duration, event_frame, event_name = ACTIONS[action]
    path = ROOT / "runtime" / action / direction / f"{n:02d}.png"
    f = {"action": action, "direction": direction, "frame": n, "file": relative(path),
         "durationMs": duration, "pivot": PIVOT, "event": event_name if n == event_frame else None,
         "present": path.is_file(), "errors": [], "warnings": [],
         "visual": {"stillReview": "pending", "sequenceReview": "pending", "clientReview": "not_tested"}}
    if not f["present"]:
        f["errors"].append("missing_frame")
        return f
    f["sha256"] = sha(path)
    review_path = ROOT / "qa/visual-review.json"
    if review_path.exists():
        review = json.loads(review_path.read_text(encoding="utf-8"))
        matching = next((r for r in review.get("frames", []) if r.get("file") == f["file"] and r.get("sha256") == f["sha256"]), None)
        if matching:
            f["visual"] = {k: matching[k] for k in ("stillReview", "sequenceReview", "clientReview", "evidence")}
            if "sequenceEvidence" in matching:
                f["visual"]["sequenceEvidence"] = matching["sequenceEvidence"]
    try:
        with Image.open(path) as image:
            image.load()
            f.update(width=image.width, height=image.height, mode=image.mode, format=image.format)
            if image.size != (1024, 1024):
                f["errors"].append("wrong_dimensions")
            if image.format != "PNG":
                f["errors"].append("not_png")
            if image.mode != "RGBA":
                f["errors"].append("not_rgba")
            rgba = image.convert("RGBA")
            alpha = rgba.getchannel("A")
            histogram = alpha.histogram()
            amin, amax = alpha.getextrema()
            pixels = image.width * image.height
            f["alpha"] = {"min": amin, "max": amax, "transparentPixels": histogram[0],
                          "opaquePixels": histogram[255], "partialPixels": sum(histogram[1:255]),
                          "transparentFraction": round(histogram[0] / pixels, 6)}
            if amin != 0:
                f["errors"].append("no_fully_transparent_pixels")
            if amax == 0:
                f["errors"].append("blank_image")
            if amax < 255:
                f["warnings"].append("no_fully_opaque_pixels")
            mask = alpha.point(lambda value: 255 if value > 8 else 0)
            bbox = mask.getbbox()
            f["contentBoundsAlphaAbove8"] = list(bbox) if bbox else None
            if bbox:
                margins = [bbox[0], bbox[1], image.width - bbox[2], image.height - bbox[3]]
                f["transparentMarginsLTRB"] = margins
                if min(margins) == 0:
                    f["warnings"].append("content_touches_canvas_edge")
                elif min(margins) < 8:
                    f["warnings"].append("content_within_8px_of_canvas_edge")
            f["rgbaPixelSha256"] = hashlib.sha256(rgba.tobytes()).hexdigest()
            clean = rgba.copy()
            zero_alpha = alpha.point(lambda value: 255 if value == 0 else 0)
            clean.paste((0, 0, 0, 0), mask=zero_alpha)
            f["visiblePixelSha256"] = hashlib.sha256(clean.tobytes()).hexdigest()
    except (OSError, ValueError) as exc:
        f["errors"].append("image_decode_failed")
        f["decodeError"] = str(exc)
    record = source_record(path, action, direction, n)
    f["sourceRecord"] = audit_record(record, path, f["sha256"], f["errors"], f["warnings"])
    return f


def font(size: int):
    for name in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def contact_sheets(frames: list[dict]) -> list[str]:
    output = []
    thumb, columns, label_h, title_h, gap = 448, 4, 66, 76, 12
    for action, (count, duration, _, _) in ACTIONS.items():
        for direction in DIRECTIONS:
            group = [f for f in frames if f["action"] == action and f["direction"] == direction]
            rows = (count + columns - 1) // columns
            width = gap + columns * (thumb + gap)
            height = title_h + gap + rows * (thumb + label_h + gap)
            sheet = Image.new("RGB", (width, height), "#f1ecdf")
            draw = ImageDraw.Draw(sheet)
            draw.rectangle((0, 0, width, title_h), fill="#194f47")
            draw.text((24, 16), f"绛铃 | {action} {direction} · {DIRECTIONS[direction]} | {duration} ms / frame", font=font(28), fill="#fff6df")
            for i, frame in enumerate(group):
                x, y = gap + (i % columns) * (thumb + gap), title_h + gap + (i // columns) * (thumb + label_h + gap)
                cell = Image.new("RGBA", (thumb, thumb), "#e7e4db")
                tile_draw = ImageDraw.Draw(cell)
                for ty in range(0, thumb, 28):
                    for tx in range(0, thumb, 28):
                        if (tx // 28 + ty // 28) % 2:
                            tile_draw.rectangle((tx, ty, tx + 27, ty + 27), fill="#cfcec6")
                if frame["present"] and "image_decode_failed" not in frame["errors"]:
                    with Image.open(ROOT / frame["file"]) as im:
                        im = im.convert("RGBA")
                        im.thumbnail((thumb, thumb), Image.Resampling.LANCZOS)
                        cell.alpha_composite(im, ((thumb - im.width) // 2, (thumb - im.height) // 2))
                else:
                    tile_draw.text((40, 190), "缺帧 / MISSING", font=font(32), fill="#903f35")
                sheet.paste(cell.convert("RGB"), (x, y))
                event = f" · {frame['event']}" if frame["event"] else ""
                draw.text((x + 8, y + thumb + 4), f"{direction} / {action} / {frame['frame']:02d}{event}", font=font(22), fill="#194f47")
                playback_label = "原生连播已抽验" if frame["visual"].get("sequenceEvidence") == PLAYBACK_RECORD else "连播待验"
                status = (f"单帧已实看 · {playback_label}" if frame["visual"]["stillReview"] == "reviewed" else "待美术实看") if not frame["errors"] else f"技术问题 {len(frame['errors'])} 项"
                draw.text((x + 8, y + thumb + 34), status, font=font(19), fill="#725e3f")
            target = ROOT / "qa" / f"technical-contact-{action}-{direction}.jpg"
            target.parent.mkdir(parents=True, exist_ok=True)
            sheet.save(target, quality=94, subsampling=0)
            output.append(relative(target))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contacts", action="store_true", help="Regenerate six labeled contact sheets; missing slots remain explicit.")
    parser.add_argument("--manifest", action="store_true", help="Write manifest.json and SHA256SUMS.txt (opt-in only).")
    parser.add_argument("--require-complete", action="store_true", help="Exit 2 for any technical error, including absent frames/records.")
    args = parser.parse_args()
    playback = load_playback_review(ROOT)
    frames = [audit_frame(a, d, n) for a, (count, *_rest) in ACTIONS.items() for d in DIRECTIONS for n in range(1, count + 1)]
    for frame in frames:
        visual = frame["visual"]
        if playback:
            visual["sequenceReview"] = PLAYBACK_SEQUENCE
            visual["sequenceEvidence"] = PLAYBACK_RECORD
        else:
            visual.pop("sequenceEvidence", None)
            if visual["stillReview"] == "reviewed":
                visual["sequenceReview"] = PENDING_SEQUENCE
    expected = {f["file"] for f in frames}
    actual = {relative(p) for p in (ROOT / "runtime").rglob("*.png")} if (ROOT / "runtime").exists() else set()
    duplicates = {}
    for key in ("sha256", "rgbaPixelSha256", "visiblePixelSha256"):
        hashes = defaultdict(list)
        for frame in frames:
            if frame.get(key):
                hashes[frame[key]].append(frame)
        sets = []
        for digest, group in hashes.items():
            if len(group) > 1:
                sets.append({"sha256": digest, "files": [f["file"] for f in group]})
                for frame in group:
                    frame["errors"].append(f"duplicate:{key}")
        duplicates[key] = sets
    now = datetime.now(timezone.utc).isoformat()
    present = sum(f["present"] for f in frames)
    errors = sum(len(f["errors"]) for f in frames)
    extras = sorted(actual - expected)
    status = "passed" if errors == 0 and not extras else "incomplete" if present < 68 else "failed"
    delivery_status = ("assets_complete_native_playback_reviewed" if playback else "assets_complete_continuous_playback_pending") if status == "passed" else status
    visual_review = (f"qa/visual-review.json; independent_record: {PLAYBACK_RECORD}; native live playback sampled at 1x and 0.25x"
                     if playback else "qa/visual-review.json; continuous playback not observed")
    report = {"schemaVersion": 1, "pet": "02-jiangling", "name": "绛铃", "checkedAt": now,
              "status": status, "deliveryStatus": delivery_status, "scope": "technical_files_only", "expectedFrames": 68, "presentFrames": present,
              "missingFrames": [f["file"] for f in frames if not f["present"]], "unexpectedRuntimePngs": extras,
              "errorCount": errors, "warningCount": sum(len(f["warnings"]) for f in frames),
              "duplicates": duplicates, "frames": frames,
              "visualReview": visual_review, "clientReview": "not_tested",
              "limitations": ["Exact duplicate detection does not prove independent AI generation.",
                              "Bounding boxes do not verify anatomy, direction, pivot stability or animation quality.",
                              "Source metadata is checked for consistency; model assertions are not independently authenticated.",
                              "No runtime frame is modified, synthesized, mirrored, shifted or interpolated."]}
    if args.contacts:
        report["contactSheets"] = contact_sheets(frames)
    save_json(ROOT / "qa/technical-check.json", report)
    if args.manifest:
        manifest = {"schemaVersion": 1, "pet": "02-jiangling", "name": "绛铃", "generatedAt": now,
                    "deliveryStatus": delivery_status, "technicalStatus": status, "frameCount": present, "expectedFrameCount": 68,
                    "canvas": {"width": 1024, "height": 1024, "format": "PNG", "mode": "RGBA"},
                    "coordinates": {"pivot": PIVOT, "pivotOrigin": "bottom-left", "neutralAnchorTopLeftPx": [512, 942],
                                    "alignment": "single_uniform_export_transform_per_direction; no per-frame foot realignment"},
                    "directions": DIRECTIONS,
                    "actions": {a: {"framesPerDirection": c, "durationMs": ms, "totalDurationMs": c * ms,
                                    "eventFrame": event, "event": name} for a, (c, ms, event, name) in ACTIONS.items()},
                    "technicalReport": "qa/technical-check.json", "preview": "preview.html", "nativePreview": "preview-native.cmd", "frames": frames,
                    "visualReview": visual_review, "clientReview": "not_tested", "sourceAudit": "qa/source-audit.json"}
        save_json(ROOT / "manifest.json", manifest)
        checksum_paths = [ROOT / f["file"] for f in frames if f["present"]]
        checksum_paths += [ROOT / f["sourceRecord"]["path"] for f in frames if f.get("sourceRecord", {}).get("path")]
        checksum_paths += [ROOT / "manifest.json", ROOT / "preview.html"]
        checksum_paths = sorted(set(p for p in checksum_paths if p.is_file()))
        (ROOT / "SHA256SUMS.txt").write_text("".join(f"{sha(p)}  {relative(p)}\n" for p in checksum_paths), encoding="utf-8")
    print(json.dumps({"status": status, "frames": f"{present}/68", "errors": errors, "unexpectedPngs": len(extras),
                      "report": str(ROOT / "qa/technical-check.json"), "manifestWritten": args.manifest}, ensure_ascii=False))
    return 2 if args.require_complete and (errors or extras) else 0


if __name__ == "__main__":
    sys.exit(main())
