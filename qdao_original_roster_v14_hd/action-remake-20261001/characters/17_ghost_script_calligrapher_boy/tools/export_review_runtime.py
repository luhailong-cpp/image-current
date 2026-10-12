"""Export this character's 196 reviewed selections, without content edits.

Default/--check is read-only. --export publishes only after every check succeeds.
No crop, bbox fitting, translation, alpha cleanup, pose edit, or source deletion.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parents[1]
CHARACTER = "17_ghost_script_calligrapher_boy"
SIZE = 1024
EDGE_ALPHA_THRESHOLD = 128  # Existing review convention: alpha > 128.
ACTIONS = {
    "run": (("N", "NE", "E", "SE", "S", "SW", "W", "NW"), 16, 60),
    "hit": (("E", "W"), 6, 40),
    "attack": (("E", "W"), 12, 30),
    "cast": (("E", "W"), 16, 45),
}
EXPECTED = {
    f"{action}-{direction}-{n:02d}": (action, direction, n, ms)
    for action, (directions, count, ms) in ACTIONS.items()
    for direction in directions for n in range(1, count + 1)
}


class ExportError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise ExportError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_json(path):
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8-sig")), raw


def resolve_from(folder, raw):
    require(isinstance(raw, str) and bool(raw), f"Missing path relative to {folder}")
    p = Path(raw)
    return (p if p.is_absolute() else folder / p).resolve()


def rel_or_absolute(path, base):
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def edge_counts(im):
    alpha = im.getchannel("A")
    w, h = im.size
    boxes = {"left": (0, 0, 1, h), "right": (w - 1, 0, w, h),
             "top": (0, 0, w, 1), "bottom": (0, h - 1, w, h)}
    return {side: sum(band.histogram()[EDGE_ALPHA_THRESHOLD + 1:])
            for side, box in boxes.items() for band in [alpha.crop(box)]}


def inspect_png(raw, label, native=True):
    with Image.open(io.BytesIO(raw)) as im:
        im.load()
        require(im.format == "PNG" and im.mode == "RGBA", f"{label}: needs native PNG RGBA")
        w, h = im.size
        require(w == h and w >= SIZE, f"{label}: native square >= {SIZE} required, got {im.size}")
        if not native:
            require(im.size == (SIZE, SIZE), f"{label}: export size is not 1024 square")
        lo, hi = im.getchannel("A").getextrema()
        require(lo == 0 and hi > EDGE_ALPHA_THRESHOLD, f"{label}: invalid/empty transparency")
        edges = edge_counts(im)
        require(not any(edges.values()), f"{label}: high-alpha pixels touch canvas edge: {edges}")
        return im.copy(), {"size": [w, h], "mode": im.mode, "edgeHighAlphaPixels": edges}


def evidence_bundle(record, source, record_path, base):
    """Keep the original record verbatim; embed available request/prompt text too."""
    roots = [source.parent.parent, source.parent.parent.parent.parent,
             base, record_path.parent]
    key = source.stem
    requested = record.get("evidence", {}).get("request")
    prompt = record.get("prompt")
    items = {}
    for name, raw, fallbacks in [
        ("request", requested, [record_path.parent / f"{key}.request.json",
                               source.parent.parent / "provenance" / f"{key}.request.json"]),
        ("prompt", prompt, [source.parent.parent / "prompts" / f"{key}.txt"]),
    ]:
        candidates = []
        if isinstance(raw, str):
            p = Path(raw)
            candidates.extend([p] if p.is_absolute() else [r / p for r in roots])
        candidates.extend(fallbacks)
        found = next((p.resolve() for p in candidates if p.is_file()), None)
        if found:
            data = found.read_bytes()
            items[name] = {"file": rel_or_absolute(found, base), "sha256": sha(data),
                           "text": data.decode("utf-8-sig")}
        else:
            items[name] = {"availableLocally": False, "recordedReference": raw}
    return items


@dataclass
class Frame:
    slot: str
    action: str
    direction: str
    number: int
    duration: int
    selected: dict
    source: Path
    source_sha: str
    source_info: dict
    record_path: Path
    record_sha: str
    record: dict
    evidence: dict


@dataclass
class Plan:
    base: Path
    preview_sha: str
    preview: dict
    acceptance: dict
    acceptance_sha: str | None
    status: str
    frames: list[Frame]


def preflight(base=BASE):
    base = base.resolve()
    manifest_path = base / "preview" / "manifest-preview.json"
    preview, raw = read_json(manifest_path)
    preview_sha = sha(raw)
    require(preview.get("character") == CHARACTER, "Wrong character in preview manifest")
    rows = preview.get("slots")
    require(isinstance(rows, list) and len(rows) == len(EXPECTED) == 196,
            "Preview must contain exactly 196 slots")
    ids = [s.get("slot") for s in rows]
    require(len(set(ids)) == 196 and set(ids) == set(EXPECTED),
            "Preview slots are missing, duplicated, or unexpected")
    accepted_path = base / "acceptance.json"
    acceptance, acceptance_raw = read_json(accepted_path) if accepted_path.exists() else ({}, None)
    status = acceptance.get("status", "candidate")
    require(status in {"candidate", "needs_review", "passed", "rejected"}, "Unknown acceptance status")
    require(acceptance.get("character", CHARACTER) == CHARACTER, "Wrong character in acceptance.json")
    if status == "passed":
        require(acceptance.get("previewManifestSha256") == preview_sha,
                "Passed acceptance is not bound to this exact preview manifest")
        require(acceptance.get("visualApproval") == "passed" and
                acceptance.get("dynamicApproval") == "passed" and acceptance.get("reviewedAt"),
                "Passed status requires explicit visual/dynamic approval and reviewedAt")
    by_slot = {s["slot"]: s for s in rows}
    frames = []
    for slot, (action, direction, number, duration) in EXPECTED.items():
        row = by_slot[slot]
        require((row.get("action"), row.get("direction"), row.get("frame")) ==
                (action, direction, number), f"{slot}: row identity mismatch")
        require(row.get("duration_ms") == duration, f"{slot}: stale preview timing")
        selected = row.get("selected")
        require(isinstance(selected, dict), f"{slot}: no explicit selected image")
        require((selected.get("slot"), selected.get("action"), selected.get("direction"),
                 selected.get("frame")) == (slot, action, direction, number),
                f"{slot}: selected image identity mismatch")
        source = resolve_from(manifest_path.parent, selected.get("path"))
        record_path = resolve_from(manifest_path.parent, selected.get("record_path"))
        raw_source = source.read_bytes()
        digest = sha(raw_source)
        require(selected.get("sha256") == digest, f"{slot}: selected source SHA mismatch")
        im, info = inspect_png(raw_source, slot)
        im.close()
        record, record_raw = read_json(record_path)
        require(record.get("sha256") == digest, f"{slot}: original generation SHA mismatch")
        require([record.get("width"), record.get("height")] == info["size"],
                f"{slot}: original generation size mismatch")
        for name in ("configSnapshot", "submittedParameters", "actualModel", "actualQuality",
                     "generatedAt", "generatedAtEvidence", "tool", "route", "evidence"):
            require(name in record, f"{slot}: original generation record missing {name}")
        require(isinstance(record["configSnapshot"], dict) and
                all(k in record["configSnapshot"] for k in ("model", "quality")),
                f"{slot}: missing configured model/quality evidence")
        require(isinstance(record["submittedParameters"], dict) and
                all(k in record["submittedParameters"] for k in ("model", "quality")),
                f"{slot}: missing submitted model/quality evidence")
        frames.append(Frame(slot, action, direction, number, duration, selected, source, digest,
                            info, record_path, sha(record_raw), record,
                            evidence_bundle(record, source, record_path, base)))
    return Plan(base, preview_sha, preview, acceptance,
                sha(acceptance_raw) if acceptance_raw is not None else None, status, frames)


def unchanged(plan):
    require(sha((plan.base / "preview" / "manifest-preview.json").read_bytes()) == plan.preview_sha,
            "Preview changed after preflight; rerun")
    p = plan.base / "acceptance.json"
    current = sha(p.read_bytes()) if p.exists() else None
    require(current == plan.acceptance_sha, "Acceptance changed after preflight; rerun")
    for f in plan.frames:
        require(sha(f.source.read_bytes()) == f.source_sha, f"{f.slot}: source changed; rerun")
        require(sha(f.record_path.read_bytes()) == f.record_sha, f"{f.slot}: provenance changed; rerun")


def export(plan):
    """Publish a complete initial package. Never overwrite an existing package."""
    base = plan.base
    runtime, manifest = base / "runtime", base / "manifest.json"
    require(not runtime.exists() and not manifest.exists(),
            "runtime/ or manifest.json already exists; refusing to overwrite it")
    unchanged(plan)
    timestamp = datetime.now(timezone.utc).isoformat()
    groups = {}
    # All preflight checks complete before even creating this private temporary directory.
    # It is removed on failure; existing sources and packages are never removed.
    with tempfile.TemporaryDirectory(prefix=".runtime-export-", dir=base) as tmp:
        tmp = Path(tmp)
        staging_runtime = tmp / "runtime"
        staging_runtime.mkdir()
        for f in plan.frames:
            raw = f.source.read_bytes()
            require(sha(raw) == f.source_sha, f"{f.slot}: source changed while exporting")
            im, _ = inspect_png(raw, f.slot)
            out = im if im.size == (SIZE, SIZE) else im.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
            stream = io.BytesIO()
            out.save(stream, format="PNG")
            out_raw = stream.getvalue()
            verified, output_info = inspect_png(out_raw, f.slot + " output", native=False)
            verified.close()
            if out is not im:
                out.close()
            im.close()
            rel = Path("runtime") / f.action / f.direction / f"{f.number:02d}.png"
            target = tmp / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(out_raw)
            output_sha = sha(out_raw)
            event = "hit_contact" if f.action == "attack" and f.number == 6 else (
                "cast_release" if f.action == "cast" and f.number == 10 else None)
            original = {"file": rel_or_absolute(f.record_path, base),
                        "sha256": f.record_sha, "record": f.record,
                        "availableEvidenceFiles": f.evidence}
            receipt = {"file": rel.as_posix(), "sha256": output_sha, "exportedAt": timestamp,
                       "width": SIZE, "height": SIZE, "mode": "RGBA",
                       "derivedFrom": {"file": rel_or_absolute(f.source, base),
                                       "sha256": f.source_sha, "nativeSize": f.source_info["size"]},
                       "transform": {"type": "uniform_full_canvas_resize", "filter": "LANCZOS",
                                     "crop": None, "translation": [0, 0], "alphaCleanup": False},
                       "configSnapshot": f.record["configSnapshot"],
                       "submittedParameters": f.record["submittedParameters"],
                       "actualModel": f.record["actualModel"], "actualQuality": f.record["actualQuality"],
                       "sourceGenerationRecord": original}
            receipt_raw = json_bytes(receipt)
            target.with_suffix(".png.generation.json").write_bytes(receipt_raw)
            groups.setdefault((f.action, f.direction), []).append({
                "slot": f.slot, "frame": f.number, "file": rel.as_posix(), "sha256": output_sha,
                "sourceFile": rel_or_absolute(f.source, base), "sourceSha256": f.source_sha,
                "sourceNativeSize": f.source_info["size"], "durationMs": f.duration, "event": event,
                "status": plan.status, "technicalChecksPassed": True,
                "sourceEdgeHighAlphaPixels": f.source_info["edgeHighAlphaPixels"],
                "outputEdgeHighAlphaPixels": output_info["edgeHighAlphaPixels"],
                "generationRecord": {"file": rel.as_posix() + ".generation.json",
                                     "sha256": sha(receipt_raw), "record": receipt},
            })
        data = {"schemaVersion": 1, "character": CHARACTER, "exportedAt": timestamp,
                "status": plan.status, "automaticApproval": False, "canvas": [SIZE, SIZE],
                "alignment": {"method": "unchanged_full_canvas", "perFrameTranslation": [0, 0],
                              "perFrameBboxFit": False, "clientPivotCalibrated": False,
                              "previewReferenceTopLeftNormalized": [0.5104, 0.92105],
                              "referenceIsPhysicalGroundMeasurement": False},
                "counts": {"expectedSlots": 196, "exportedRuntimeSlots": 196,
                           "technicalChecksPassed": 196,
                           "visualPassedSlots": 196 if plan.status == "passed" else 0,
                           "dynamicPassedSequences": 14 if plan.status == "passed" else 0},
                "clientNotIntegrated": True, "clientIntegration": "not_integrated",
                "clientRuntimeAcceptance": "not_tested",
                "selectionSource": {"file": "preview/manifest-preview.json",
                                    "sha256": plan.preview_sha, "builtAt": plan.preview.get("built_at")},
                "acceptance": {"file": "acceptance.json" if plan.acceptance_sha else None,
                               "sha256": plan.acceptance_sha, "record": plan.acceptance},
                "limits": "Technical export does not approve anatomy, edges or animation. "
                          "Unknown actual model/quality values remain null; no client integration.",
                "sequences": [
                    {"label": f"{a}/{d}", "action": a, "direction": d, "count": len(fs),
                     "ms": ACTIONS[a][2], "cycleMs": ACTIONS[a][2] * len(fs),
                     "eventFrame": 6 if a == "attack" else 10 if a == "cast" else None,
                     "frames": fs} for (a, d), fs in groups.items()]}
        staged_manifest = tmp / "manifest.json"
        staged_manifest.write_bytes(json_bytes(data))
        unchanged(plan)
        require(not runtime.exists() and not manifest.exists(), "Destination appeared during export")
        # A validation/I/O failure during preparation leaves no partial final package.
        os.rename(staging_runtime, runtime)
        try:
            os.rename(staged_manifest, manifest)
        except BaseException:
            os.rename(runtime, staging_runtime)
            raise
    return {"status": plan.status, "exported": 196, "runtime": str(runtime),
            "manifest": str(manifest), "clientNotIntegrated": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="read-only preflight (default)")
    modes.add_argument("--export", action="store_true", help="publish the complete initial package")
    args = parser.parse_args(argv)
    try:
        plan = preflight()
        result = export(plan) if args.export else {
            "status": plan.status, "checked": len(plan.frames), "exported": 0,
            "previewManifestSha256": plan.preview_sha,
            "edgeRule": "outermost canvas edges: alpha > 128 count must be zero",
            "clientNotIntegrated": True}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ExportError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "failed", "exported": 0, "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
