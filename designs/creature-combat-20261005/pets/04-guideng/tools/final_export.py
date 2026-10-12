"""Deterministically export all 68 sprites from their native images.

No native image, identity reference, cache, manifest, or visual review is changed.
The entire package must pass preflight before any output is written.
Run with --check-only for a read-only preflight, or with no arguments to export.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, __version__ as PILLOW_VERSION

ROOT = Path(__file__).resolve().parents[1]
SPECS = (("hit", 6, 40), ("attack", 12, 30), ("cast", 16, 45))
NATIVE_SIZE = (1254, 1254)
SCALED_SIZE = (922, 922)
FINAL_SIZE = (1024, 1024)
OFFSET = (51, 51)
TRANSFORM = {
    "id": "native-1254-full-canvas-lanczos-922-pad51-v1",
    "type": "uniform-full-canvas-resize-and-pad",
    "nativeSize": list(NATIVE_SIZE),
    "scaledSize": list(SCALED_SIZE),
    "finalCanvasSize": list(FINAL_SIZE),
    "offsetPx": list(OFFSET),
    "scaleFromNative": 922 / 1254,
    "resampling": "Lanczos",
    "sameForAllDirectionsAndActions": True,
    "crop": None,
    "perFrameBBoxAlignment": False,
    "perFrameFootAlignment": False,
    "clearLowAlpha": False,
    "alphaCompositing": "RGBA copy into transparent canvas; no extra alpha mask",
}
ANCHOR_NOTE = (
    "All E/W hit/attack/cast frames use the same full-canvas transform. "
    "The runtime pivot [0.5,0.08] and virtual anchor [512,942] are final "
    "1024x1024 canvas coordinates. The preset anchor is not the lowest shoe "
    "pixel of each frame; no per-frame foot/bbox alignment is performed. "
    "The character's relative pose motion is retained."
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def require_output_path(path: Path) -> Path:
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Output escapes this pet directory: {path}")
    return path


def resolve_source(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def path_strings(value):
    if isinstance(value, str) and value.strip():
        yield value
    elif isinstance(value, dict):
        for key in ("path", "file", "source", "nativeFile", "sourceNativePath"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                yield candidate


def native_candidates(record: dict) -> list[Path]:
    values = []
    for key in ("nativeFile", "sourceNativePath", "sourceNative", "source"):
        values.extend(path_strings(record.get(key)))
    values.extend(path_strings(record.get("derivedFrom")))
    values.extend(path_strings(record.get("native")))
    result = []
    for value in values:
        candidate = resolve_source(value)
        if candidate not in result:
            result.append(candidate)
    return result


def native_hash_evidence(record: dict) -> str:
    candidates = [
        record.get("nativeSha256"),
        record.get("sourceSha256"),
    ]
    for key in ("native", "sourceNative", "derivedFrom"):
        value = record.get(key)
        if isinstance(value, dict):
            candidates.append(value.get("sha256"))
            candidates.append(value.get("sourceSha256"))
    known = {str(value).lower() for value in candidates if value}
    if len(known) != 1:
        raise ValueError(
            "Native SHA evidence is missing or contradictory: "
            + json.dumps(sorted(known))
        )
    return next(iter(known))


def find_native(record: dict, destination: Path) -> tuple[Path, bytes, str]:
    expected = native_hash_evidence(record)
    candidates = native_candidates(record)
    problems = []
    for path in candidates:
        if path == destination.resolve():
            problems.append(f"{path}: points to runtime output")
            continue
        if not path.is_file():
            problems.append(f"{path}: missing")
            continue
        data = path.read_bytes()
        actual = digest(data)
        if actual == expected:
            return path, data, actual
        problems.append(f"{path}: SHA does not match native record")
    raise ValueError("No verified native source. " + " | ".join(problems))


def record_size_evidence(record: dict) -> list[tuple]:
    result = []
    direct = (record.get("nativeWidth"), record.get("nativeHeight"))
    if all(value is not None for value in direct):
        result.append(direct)
    for value in (
        record.get("nativeSize"),
        (record.get("derivedFrom") or {}).get("nativeSize")
        if isinstance(record.get("derivedFrom"), dict) else None,
    ):
        if isinstance(value, (list, tuple)) and len(value) == 2:
            result.append(tuple(value))
    for owner in (record.get("native"), record.get("sourceNative"),
                  (record.get("derivedFrom") or {}).get("native")
                  if isinstance(record.get("derivedFrom"), dict) else None):
        if isinstance(owner, dict):
            size = (owner.get("width"), owner.get("height"))
            if all(value is not None for value in size):
                result.append(size)
    return result


def enumerate_inputs() -> list[dict]:
    items = []
    missing = []
    for action, count, duration in SPECS:
        for direction in ("E", "W"):
            group = f"{direction}-{action}"
            for number in range(1, count + 1):
                destination = require_output_path(
                    ROOT / "runtime" / action / direction / f"{number:02d}.png"
                )
                options = [
                    ROOT / "records" / group / f"{number:02d}.generation.json",
                    ROOT / "records" / group / f"{number:02d}.json",
                ]
                existing = [path for path in options if path.is_file()]
                if not destination.is_file():
                    missing.append(relative(destination))
                if not existing:
                    missing.append(relative(options[0]) + " (or nn.json)")
                elif len(existing) > 1:
                    raise ValueError(f"Ambiguous generation records for {group}-{number:02d}")
                if destination.is_file() and len(existing) == 1:
                    items.append({
                        "id": f"{group}-{number:02d}",
                        "action": action, "direction": direction,
                        "frame": number, "durationMs": duration,
                        "destination": destination,
                        "recordPath": require_output_path(existing[0]),
                        "record": load_json(existing[0]),
                    })
    if missing or len(items) != 68:
        raise ValueError(
            f"Refusing export: all 68 runtime PNGs and generation records are required; "
            f"found {len(items)} complete pairs. Missing: " + "; ".join(missing)
        )
    return items


def encode_final(native_data: bytes, frame_id: str) -> tuple[bytes, dict, dict]:
    with Image.open(io.BytesIO(native_data)) as native:
        native.load()
        if native.size != NATIVE_SIZE:
            raise ValueError(f"{frame_id}: native size {native.size} is not {NATIVE_SIZE}")
        if native.mode != "RGBA" or native.format != "PNG":
            raise ValueError(f"{frame_id}: native must be RGBA PNG, got {native.mode}/{native.format}")
        native_info = {
            "width": native.width, "height": native.height,
            "mode": native.mode, "format": native.format,
        }
        scaled = native.resize(SCALED_SIZE, Image.Resampling.LANCZOS)
    final = Image.new("RGBA", FINAL_SIZE, (0, 0, 0, 0))
    # Intentionally no mask: using scaled as a mask would multiply its alpha.
    final.paste(scaled, OFFSET)
    alpha = final.getchannel("A")
    bbox = alpha.getbbox()
    extrema = list(alpha.getextrema())
    if bbox is None or extrema != [0, 255]:
        raise ValueError(f"{frame_id}: unexpected exported alpha: {extrema}/{bbox}")
    margins = [bbox[0], bbox[1], FINAL_SIZE[0] - bbox[2], FINAL_SIZE[1] - bbox[3]]
    if min(margins) < 51:
        raise ValueError(f"{frame_id}: transparent margin check failed: {margins}")
    core_bbox = alpha.point(lambda value: 255 if value >= 8 else 0).getbbox()
    buf = io.BytesIO()
    final.save(buf, format="PNG", optimize=False, compress_level=6)
    return buf.getvalue(), native_info, {
        "extrema": extrema, "bbox": list(bbox), "alpha8BBox": list(core_bbox) if core_bbox else None,
        "marginsPx": margins,
    }


def make_plan(item: dict, journal_by_id: dict, exported_at: str) -> dict:
    record = item["record"]
    destination = item["destination"]
    original_bytes = destination.read_bytes()
    current_sha = digest(original_bytes)
    native_path, native_data, native_sha = find_native(record, destination)
    for size in record_size_evidence(record):
        if size != NATIVE_SIZE:
            raise ValueError(f'{item["id"]}: recorded native size {size} contradicts {NATIVE_SIZE}')
    final_bytes, native_info, alpha = encode_final(native_data, item["id"])
    final_sha = digest(final_bytes)
    recorded_sha = record.get("sha256")
    if current_sha not in (recorded_sha, final_sha):
        raise ValueError(f'{item["id"]}: current runtime SHA differs from record and deterministic final export')
    previous_final = record.get("finalExport")
    matching_export = (
        isinstance(previous_final, dict)
        and previous_final.get("transform") == TRANSFORM
        and previous_final.get("finalSHA") == final_sha
        and previous_final.get("nativeSource", {}).get("sha256") == native_sha
    )
    if matching_export and current_sha == final_sha and recorded_sha == final_sha:
        return {
            **item, "nativePath": native_path, "nativeSha256": native_sha,
            "nativeInfo": native_info, "currentSha256": current_sha,
            "finalSha256": final_sha, "finalBytes": final_bytes,
            "updatedRecord": record, "alpha": alpha, "skip": True,
            "preExportSha256": previous_final["preExportSha256"],
        }
    updated = copy.deepcopy(record)
    pre_export_sha = current_sha
    if matching_export:
        pre_export_sha = previous_final["preExportSha256"]
    elif current_sha == final_sha:
        # Resume after PNG replacement but before record replacement, using the export journal.
        prior = journal_by_id.get(item["id"], {})
        pre_export_sha = prior.get("preExportSha256") or recorded_sha
    if not pre_export_sha:
        raise ValueError(f'{item["id"]}: cannot establish original pre-export SHA')
    history = updated.setdefault("operationHistory", [])
    if not isinstance(history, list):
        raise ValueError(f'{item["id"]}: operationHistory must be a list')
    old_operation = copy.deepcopy(updated.get("operation"))
    if old_operation is not None and (not history or history[-1] != old_operation):
        history.append(old_operation)
    if isinstance(previous_final, dict) and not matching_export:
        updated.setdefault("finalExportHistory", []).append(copy.deepcopy(previous_final))
    updated["operation"] = copy.deepcopy(TRANSFORM)
    updated["finalExport"] = {
        "exportedAt": exported_at,
        "preExportSha256": pre_export_sha,
        "transform": copy.deepcopy(TRANSFORM),
        "finalSHA": final_sha,
        "finalDimensions": list(FINAL_SIZE),
        "nativeSource": {"path": str(native_path), "sha256": native_sha, **native_info},
        "pillowVersion": PILLOW_VERSION,
        "note": ANCHOR_NOTE,
    }
    updated.update(
        sha256=final_sha, width=1024, height=1024, format="PNG", mode="RGBA",
        exportSize=list(FINAL_SIZE), pivot=[0.5, 0.08],
        virtualAnchor=[512, 942], anchorTopLeftPx=[512, 942],
        alphaExtrema=alpha["extrema"], alphaBBox=alpha["bbox"],
        alphaBounds=alpha["bbox"], alpha8BBox=alpha["alpha8BBox"],
    )
    old_alpha = updated.get("alpha")
    if old_alpha is None or isinstance(old_alpha, dict):
        updated["alpha"] = {
            **(old_alpha or {}), "min": alpha["extrema"][0], "max": alpha["extrema"][1],
            "bbox": alpha["bbox"], "marginsPx": alpha["marginsPx"],
        }
    # All original native/prompt/reference/receipt/model fields remain untouched.
    return {
        **item, "nativePath": native_path, "nativeSha256": native_sha,
        "nativeInfo": native_info, "currentSha256": current_sha,
        "finalSha256": final_sha, "finalBytes": final_bytes,
        "updatedRecord": updated, "alpha": alpha, "skip": False,
        "preExportSha256": pre_export_sha,
    }


def atomic_write(path: Path, data: bytes) -> None:
    path = require_output_path(path)
    temporary = require_output_path(path.with_name(path.name + ".final-export.tmp"))
    temporary.write_bytes(data)
    os.replace(temporary, path)


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Validate all 68 inputs without writing files")
    args = parser.parse_args()
    items = enumerate_inputs()
    journal_path = require_output_path(ROOT / "EXPORT.json")
    old_journal = load_json(journal_path) if journal_path.is_file() else {}
    journal_by_id = (
        {frame["id"]: frame for frame in old_journal.get("frames", [])}
        if old_journal.get("transform") == TRANSFORM else {}
    )
    exported_at = datetime.now(timezone.utc).isoformat()
    # Prepare and verify EVERY output in memory before replacing any file.
    plans = [make_plan(item, journal_by_id, exported_at) for item in items]
    pending = [plan for plan in plans if not plan["skip"]]
    summary = {
        "framesValidated": len(plans), "toExport": len(pending),
        "alreadyExported": len(plans) - len(pending),
        "transform": TRANSFORM["id"], "checkOnly": args.check_only,
    }
    if args.check_only:
        print(json.dumps(summary, ensure_ascii=False))
        return
    if not pending and old_journal.get("status") == "complete":
        print(json.dumps({**summary, "status": "already-complete-no-files-changed"}, ensure_ascii=False))
        return
    report = {
        "schemaVersion": 1, "status": "in-progress", "startedAt": exported_at,
        "expectedFrames": 68, "transform": copy.deepcopy(TRANSFORM),
        "finalCanvas": list(FINAL_SIZE), "pivot": [0.5, 0.08],
        "virtualAnchor": [512, 942], "anchorCoordinateSpace": "final-1024x1024-canvas",
        "minimumTransparentMarginPx": 51, "note": ANCHOR_NOTE,
        "nativeSourcesModified": False, "cacheDeleted": False,
        "alphaCleared": False, "runtimeIdentityRedesigned": False,
        "pillowVersion": PILLOW_VERSION,
        "visualReview": "separate; this export does not grant visual approval",
        "frames": [{
            "id": plan["id"], "file": relative(plan["destination"]),
            "generationRecord": relative(plan["recordPath"]),
            "nativeFile": str(plan["nativePath"]), "nativeSha256": plan["nativeSha256"],
            "native": plan["nativeInfo"],
            "preExportSha256": plan["preExportSha256"],
            "finalSHA": plan["finalSha256"], "finalDimensions": list(FINAL_SIZE),
            "alpha": plan["alpha"], "alreadyExported": plan["skip"],
        } for plan in plans],
    }
    atomic_write(journal_path, json_bytes(report))
    for plan in pending:
        if plan["currentSha256"] != plan["finalSha256"]:
            atomic_write(plan["destination"], plan["finalBytes"])
        atomic_write(plan["recordPath"], json_bytes(plan["updatedRecord"]))
    # Verify all persisted bytes and record hashes before declaring completion.
    for plan in plans:
        if digest(plan["destination"].read_bytes()) != plan["finalSha256"]:
            raise RuntimeError(f'Post-export PNG SHA mismatch: {plan["id"]}')
        written_record = load_json(plan["recordPath"])
        if written_record.get("sha256") != plan["finalSha256"]:
            raise RuntimeError(f'Post-export generation SHA mismatch: {plan["id"]}')
    report["status"] = "complete"
    report["completedAt"] = datetime.now(timezone.utc).isoformat()
    atomic_write(journal_path, json_bytes(report))
    print(json.dumps({**summary, "status": "complete", "report": str(journal_path)}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Final export failed: {exc}", file=sys.stderr)
        sys.exit(1)

