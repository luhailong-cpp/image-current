#!/usr/bin/env python3
"""Candidate-only 4K native composition. Every RGB value is copied from one source."""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
PLAN = ROOT / "assembly-plan.json"
GRID, STRIDE, HALO, OVERLAP, NATIVE, FULL, FINAL = 4, 1024, 115, 230, 1254, 4326, 4096
OUT = ROOT / "tiles"
ART = OUT / "r03_c03.candidate.png"
IDS = OUT / "r03_c03.source-id.png"
SEAMS = OUT / "r03_c03.seams.json"
RECORD = OUT / "r03_c03.assembly.json"

def require(condition, message):
    if not condition:
        raise ValueError(message)

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()

def path_of(value):
    p = Path(value)
    return p.resolve() if p.is_absolute() else (ROOT / p).resolve()

def local(value):
    return path_of(value).relative_to(ROOT).as_posix()

def write_json(path, value):
    tmp = path.with_name(path.name + ".writing")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)

def contract(plan):
    require(plan.get("tile") == "r03_c03", "Wrong tile")
    require(plan.get("nativeSize") == [NATIVE, NATIVE], "Native contract changed")
    require(plan.get("stride") == STRIDE and plan.get("overlap") == OVERLAP, "Stride/overlap changed")
    require(plan.get("outerCrop") == [115, 115, 4211, 4211], "Crop changed")
    entries = plan.get("sources", [])
    require(len(entries) == 16, "Exactly sixteen explicit sources required")
    expected = [(r, c) for r in range(1, 5) for c in range(1, 5)]
    require([(e["row"], e["column"]) for e in entries] == expected, "Sources must be row-major 4x4")
    require([e["sourceId"] for e in entries] == list(range(1, 17)), "sourceId must be 1..16")
    return entries

def inspect_source(entry, allow_unpinned=False):
    row, col = entry["row"], entry["column"]
    p, rp = path_of(entry["file"]), path_of(entry["generationRecord"])
    require(p.parent == ROOT / "native" and rp == Path(str(p) + ".generation.json"), "Source escaped native directory")
    prefix = f"r03_c03_s{row:02d}_s{col:02d}_v"
    require(p.name.startswith(prefix) and p.suffix == ".png", f"Wrong source position: {p}")
    require(p.is_file() and rp.is_file(), f"Missing native or generation record: {p.name}")
    r = read(rp)
    native_hash, record_hash = sha(p), sha(rp)
    require(r.get("sha256") == native_hash and path_of(r["file"]) == p, f"Generation identity/hash mismatch: {p.name}")
    for key, actual in (("sha256", native_hash), ("generationRecordSha256", record_hash)):
        pinned = entry.get(key)
        require(pinned == actual or (allow_unpinned and pinned is None), f"Unpinned/changed {key}: {p.name}")
    require(r.get("route") == "builtin", f"Non-builtin source: {p.name}")
    require(r.get("tool") == "image_gen.imagegen", f"Wrong generation tool: {p.name}")
    require(r.get("nativeScaleResampled") is False, f"Native scale not verified: {p.name}")
    require([r.get("width"), r.get("height")] == [NATIVE, NATIVE], f"Recorded dimensions wrong: {p.name}")
    state = str(r.get("status", "")).lower()
    require(not any(s in state for s in ("rejected", "superseded", "layout-mismatch")), f"Rejected/superseded source: {p.name}")
    x, y = 8192 + (col - 1) * STRIDE, 8192 + (row - 1) * STRIDE
    require(r.get("globalCoreBox") == [x, y, x + STRIDE, y + STRIDE], f"Core coordinates wrong: {p.name}")
    require(r.get("globalNativeBox") == [x - HALO, y - HALO, x + STRIDE + HALO, y + STRIDE + HALO], f"Native coordinates wrong: {p.name}")
    require(r.get("nativeCoreCropBox") == [115, 115, 1139, 1139], f"Core crop wrong: {p.name}")
    require("configSnapshot" in r and "submittedParameters" in r, f"Missing model evidence: {p.name}")
    require("actualModel" in r and "actualQuality" in r, f"Missing actual selectors: {p.name}")
    if r["actualModel"] is None or r["actualQuality"] is None:
        require(bool(r.get("unverifiedReason")), f"Missing unverified reason: {p.name}")
    prompt = path_of(r["prompt"])
    receipt_path = path_of(r["evidence"]["receipt"])
    request_path = path_of(r["evidence"].get("request", ROOT / "receipts" / f"{p.stem}.request.json"))
    for evidence in (prompt, receipt_path, request_path):
        require(evidence.is_file(), f"Missing evidence: {evidence}")
    prompt_text = prompt.read_text(encoding="utf-8-sig").strip()
    require(bool(prompt_text), f"Empty prompt: {prompt}")
    receipt, request = read(receipt_path), read(request_path)
    require(bool(receipt.get("output_hint")), f"Missing tool receipt: {p.name}")
    if "prompt" in request:
        require(request["prompt"].strip() == prompt_text, f"Prompt/request mismatch: {p.name}")
    if "promptFile" in request:
        require(path_of(request["promptFile"]) == prompt, f"Prompt path mismatch: {p.name}")
    refs = r.get("references", [])
    requested_refs = request.get("referenced_image_paths", [])
    require(refs and [path_of(a["file"]) for a in refs] == [path_of(a) for a in requested_refs], f"Reference list mismatch: {p.name}")
    verified_refs = []
    for ref in refs:
        refp = path_of(ref["file"])
        require(refp.is_file() and sha(refp) == ref["sha256"], f"Reference hash mismatch/missing: {refp}")
        require(bool(ref.get("role")), f"Reference role missing: {refp}")
        verified_refs.append({"file": str(refp), "sha256": ref["sha256"], "role": ref["role"]})
    original = receipt.get("originalFile")
    original_evidence = None
    if original:
        original_path = path_of(original)
        require(original_path.is_file() and sha(original_path) == native_hash, f"Tool-output copy mismatch: {p.name}")
        original_evidence = {"file": str(original_path), "sha256": native_hash}
    with Image.open(p) as image:
        image.load()
        require(image.format == "PNG" and image.size == (NATIVE, NATIVE), f"Actual PNG dimensions wrong: {p.name}")
        require(image.mode in ("RGB", "RGBA"), f"Unsupported pixel mode: {p.name}")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255, 255), f"Non-opaque map source: {p.name}")
        pixels = np.asarray(image)[..., :3].copy()
        source_mode = image.mode
    verified = {
        "sourceId": entry["sourceId"], "row": row, "column": col,
        "file": local(p), "sha256": native_hash,
        "generationRecord": local(rp), "generationRecordSha256": record_hash,
        "nativeSize": [NATIVE, NATIVE], "sourceMode": source_mode,
        "nativeOriginInAssembly": [(col - 1) * STRIDE, (row - 1) * STRIDE],
        "globalNativeBox": r["globalNativeBox"], "globalCoreBox": r["globalCoreBox"],
        "prompt": {"file": local(prompt), "sha256": sha(prompt)},
        "receipt": {"file": local(receipt_path), "sha256": sha(receipt_path)},
        "request": {"file": local(request_path), "sha256": sha(request_path)},
        "references": verified_refs, "toolOriginal": original_evidence,
        "configSnapshot": r["configSnapshot"], "submittedParameters": r["submittedParameters"],
        "actualModel": r["actualModel"], "actualQuality": r["actualQuality"],
        "unverifiedReason": r.get("unverifiedReason"), "statusAtAssembly": r.get("status")
    }
    return pixels, verified

def load_sources(plan):
    entries = contract(plan)
    pixels, verified = [], []
    for entry in entries:
        im, info = inspect_source(entry)
        pixels.append(im)
        verified.append(info)
    return pixels, verified

def minimum_vertical_seam(a, b):
    """Exact DP minimum sum squared RGB error; no feather or edge penalty."""
    require(a.shape == b.shape and a.ndim == 3, "Overlap shapes differ")
    difference = a.astype(np.int32) - b.astype(np.int32)
    cost = np.sum(difference * difference, axis=2, dtype=np.int64)
    height, width = cost.shape
    previous = cost[0].copy()
    back = np.zeros((height, width), dtype=np.int8)
    inf = np.int64(1 << 60)
    offsets = np.array([0, -1, 1], dtype=np.int8)  # deterministic tie order
    for y in range(1, height):
        left = np.concatenate((np.array([inf]), previous[:-1]))
        right = np.concatenate((previous[1:], np.array([inf])))
        candidates = np.stack((previous, left, right))
        choice = np.argmin(candidates, axis=0)
        back[y] = offsets[choice]
        previous = cost[y] + candidates[choice, np.arange(width)]
    seam = np.empty(height, dtype=np.int32)
    seam[-1] = np.argmin(previous)
    total = int(previous[seam[-1]])
    for y in range(height - 1, 0, -1):
        seam[y - 1] = seam[y] + back[y, seam[y]]
    require(np.all((seam >= 0) & (seam < width)), "Seam outside overlap")
    require(np.all(np.abs(np.diff(seam)) <= 1), "Disconnected seam")
    return seam, total

def append_hard(base, base_ids, incoming, incoming_ids, label):
    require(base.shape[0] == incoming.shape[0], "Join height mismatch")
    a, b = base[:, -OVERLAP:], incoming[:, :OVERLAP]
    seam, total = minimum_vertical_seam(a, b)
    take_new = np.arange(OVERLAP)[None, :] >= seam[:, None]
    selected = np.where(take_new[..., None], b, a)
    selected_ids = np.where(take_new, incoming_ids[:, :OVERLAP], base_ids[:, -OVERLAP:])
    result = np.concatenate((base[:, :-OVERLAP], selected, incoming[:, OVERLAP:]), axis=1)
    ids = np.concatenate((base_ids[:, :-OVERLAP], selected_ids, incoming_ids[:, OVERLAP:]), axis=1)
    diff = np.abs(a.astype(np.int16) - b.astype(np.int16))
    return result, ids, {
        "label": label, "overlap": OVERLAP, "pathLocal": seam.tolist(),
        "pathCostSumSquaredRGB": total, "overlapMeanAbsoluteRGB": float(diff.mean()),
        "selectionRule": "incoming where local transverse coordinate >= path; otherwise existing",
        "blend": False, "resample": False
    }

def compose(patches):
    strips, strip_ids, seams = [], [], []
    for row in range(GRID):
        index = row * GRID
        strip = patches[index].copy()
        ids = np.full((NATIVE, NATIVE), index + 1, dtype=np.uint8)
        for col in range(1, GRID):
            source_id = index + col + 1
            strip, ids, detail = append_hard(strip, ids, patches[index + col],
                np.full((NATIVE, NATIVE), source_id, dtype=np.uint8),
                f"row{row+1}_column{col}_to_{col+1}")
            detail.update({
                "axis": "vertical", "stage": "row-strip",
                "pathCoordinateSystem": "4326-square assembly before outer crop",
                "assemblyYStart": row * STRIDE,
                "assemblyXByY": [col * STRIDE + v for v in detail["pathLocal"]],
                "note": "Row-strip paths can be superseded inside later horizontal overlaps; final source-id map is authoritative."
            })
            seams.append(detail)
        require(strip.shape == (NATIVE, FULL, 3), "Row strip size wrong")
        strips.append(strip)
        strip_ids.append(ids)
    assembled, ids = strips[0], strip_ids[0]
    for row in range(1, GRID):
        transposed, trans_ids, detail = append_hard(
            assembled.transpose(1, 0, 2), ids.T,
            strips[row].transpose(1, 0, 2), strip_ids[row].T,
            f"row-strip{row}_to_{row+1}")
        assembled, ids = transposed.transpose(1, 0, 2), trans_ids.T
        detail.update({
            "axis": "horizontal", "stage": "strip-stack",
            "pathCoordinateSystem": "4326-square assembly before outer crop",
            "assemblyXStart": 0,
            "assemblyYByX": [row * STRIDE + v for v in detail["pathLocal"]]
        })
        seams.append(detail)
    require(assembled.shape == (FULL, FULL, 3) and ids.shape == (FULL, FULL), "Assembled size wrong")
    return assembled[HALO:HALO+FINAL, HALO:HALO+FINAL].copy(), ids[HALO:HALO+FINAL, HALO:HALO+FINAL].copy(), seams

def verify_contributions(pixels, ids, sources):
    require(pixels.shape == (FINAL, FINAL, 3) and ids.shape == (FINAL, FINAL), "Output size wrong")
    require(ids.dtype == np.uint8 and np.all((ids >= 1) & (ids <= 16)), "Missing/invalid pixel ownership")
    counts = []
    for source_id, source in enumerate(sources, 1):
        row, col = divmod(source_id - 1, GRID)
        ys, xs = np.nonzero(ids == source_id)
        require(len(xs) > 0, f"Source {source_id} contributes no pixels")
        sx, sy = xs + HALO - col * STRIDE, ys + HALO - row * STRIDE
        require(np.all((sx >= 0) & (sx < NATIVE) & (sy >= 0) & (sy < NATIVE)), "Pixel source coordinate out of bounds")
        require(np.array_equal(pixels[ys, xs], source[sy, sx]), f"Pixel provenance mismatch for source {source_id}")
        counts.append({"sourceId": source_id, "pixelCount": int(len(xs)),
            "outputBoundingBox": [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]})
    require(sum(c["pixelCount"] for c in counts) == FINAL * FINAL, "Incomplete contribution count")
    return counts

def save_png(pixels, path):
    temporary = path.with_name(path.stem + ".writing.png")
    Image.fromarray(pixels).save(temporary, format="PNG", optimize=True)
    temporary.replace(path)

def assemble(plan):
    patches, sources = load_sources(plan)
    pixels, ids, seams = compose(patches)
    counts = verify_contributions(pixels, ids, patches)
    # Sources are rechecked immediately before writing to detect concurrent replacement.
    _, rechecked = load_sources(plan)
    require(rechecked == sources, "Sources changed during composition")
    OUT.mkdir(parents=True, exist_ok=True)
    save_png(pixels, ART)
    save_png(ids, IDS)
    write_json(SEAMS, {"schemaVersion": 1, "tile": "r03_c03", "order": "12 row joins then 3 strip joins",
        "overlap": OVERLAP, "assembledSize": [FULL, FULL], "outerCrop": [115,115,4211,4211],
        "seamCost": "exact integer sum of squared RGB difference, neighbor steps -1/0/+1",
        "tieBreak": "straight predecessor, left predecessor, right predecessor; first minimum final column",
        "paths": seams})
    artifacts = [{"file": local(p), "sha256": sha(p)} for p in (ART, IDS, SEAMS)]
    manifest = {
        "schemaVersion": 1, "tile": "r03_c03", "createdAt": datetime.now(timezone.utc).isoformat(),
        "status": "candidate-pending-100percent-geometry-and-external-seam-review",
        "formalAccepted": False, "published": False, "completeMap": False,
        "script": {"file": local(Path(__file__)), "sha256": sha(Path(__file__))},
        "plan": {"file": local(PLAN), "sha256": sha(PLAN)},
        "globalCoreBox": [8192,8192,12288,12288],
        "nativeSize": [NATIVE,NATIVE], "stride": STRIDE, "overlap": OVERLAP,
        "assembledSizeBeforeCrop": [FULL,FULL], "outerCrop": [115,115,4211,4211],
        "outputSize": [FINAL,FINAL], "composition": {
            "method": "minimum-error hard cut in native overlap only",
            "feather": False, "interpolation": False, "scaling": False,
            "colorMatching": False, "pixelValueRewriting": False,
            "guidePixelsUsed": False, "allPixelsEqualRecordedNativeRGB": True},
        "sourceIdMap": {"file": local(IDS), "mode": "L", "range": [1,16],
            "coordinateFormula": "sourceX=outputX+115-(column-1)*1024; sourceY=outputY+115-(row-1)*1024",
            "note": "One original native source per output pixel; no mixed ownership."},
        "sources": sources, "contributions": counts, "artifacts": artifacts,
        "visualQA": {"status": "pending", "required": [
            "Inspect every seam and seam intersection at 100 percent.",
            "Reject duplicated/dropped features, displaced edges or broken slab/rail geometry.",
            "A low seam cost and pixel provenance do not establish correct geometry.",
            "Cross-tile/zone edges must be reviewed before any formal acceptance."]},
        "clientValidated": False, "navigationValidated": False, "capacity5000Validated": False
    }
    write_json(RECORD, manifest)
    return {"status": manifest["status"], "candidate": str(ART), "assemblyRecord": str(RECORD),
            "pixelProvenanceVerified": True, "formalAccepted": False}

def check(plan):
    manifest = read(RECORD)
    patches, sources = load_sources(plan)
    require(manifest["sources"] == sources, "Source evidence changed since assembly")
    require(manifest["script"]["sha256"] == sha(Path(__file__)), "Script changed since assembly")
    require(manifest["plan"]["sha256"] == sha(PLAN), "Plan changed since assembly")
    for artifact in manifest["artifacts"]:
        require(sha(path_of(artifact["file"])) == artifact["sha256"], "Assembly artifact hash mismatch")
    with Image.open(ART) as image:
        require(image.mode == "RGB" and image.size == (FINAL,FINAL), "Candidate encoding changed")
        pixels = np.asarray(image).copy()
    with Image.open(IDS) as image:
        require(image.mode == "L" and image.size == (FINAL,FINAL), "Source-id encoding changed")
        ids = np.asarray(image).copy()
    require(verify_contributions(pixels, ids, patches) == manifest["contributions"], "Contribution counts changed")
    expected_pixels, expected_ids, seams = compose(patches)
    require(np.array_equal(pixels, expected_pixels) and np.array_equal(ids, expected_ids), "Hard-seam replay differs")
    require(read(SEAMS)["paths"] == seams, "Saved seam paths differ from actual replay")
    return {"mechanicalValidation": "passed", "pixelsVerified": FINAL * FINAL, "formalAccepted": False,
            "visualQA": "still requires visual geometry and external seam review"}

def pin_pending(plan):
    updated = []
    for entry in contract(plan):
        if entry.get("sha256") is None or entry.get("generationRecordSha256") is None:
            _, info = inspect_source(entry, allow_unpinned=True)
            entry["sha256"] = info["sha256"]
            entry["generationRecordSha256"] = info["generationRecordSha256"]
            entry["selectionStatus"] = "pinned-candidate-not-formal"
            updated.append(entry["file"])
    if updated:
        plan["updatedAt"] = datetime.now(timezone.utc).isoformat()
        write_json(PLAN, plan)
    return {"pinned": updated, "assembled": False, "note": "Explicit filenames only; no automatic latest-version selection."}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--preflight", action="store_true", help="Read-only verify all16 sources; default.")
    modes.add_argument("--pin-pending", action="store_true", help="Pin missing hashes for explicitly named pending sources; only edits assembly-plan.json.")
    modes.add_argument("--assemble", action="store_true", help="Generate candidate and provenance only after all sources verify.")
    modes.add_argument("--check", action="store_true", help="Read-only full pixel provenance and seam replay.")
    args = parser.parse_args()
    plan = read(PLAN)
    if args.pin_pending:
        result = pin_pending(plan)
    elif args.assemble:
        result = assemble(plan)
    elif args.check:
        result = check(plan)
    else:
        _, sources = load_sources(plan)
        result = {"preflight": "passed", "sources": len(sources), "assembled": False, "formalAccepted": False}
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

