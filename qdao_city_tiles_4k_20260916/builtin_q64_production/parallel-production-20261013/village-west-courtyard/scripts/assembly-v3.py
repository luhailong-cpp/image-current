#!/usr/bin/env python3
"""Explicit-source native assembly v3 for village-west-courtyard.

No generation, shared-state writes, directory scans, resampling or RGB blending.
--validate-plan and --dry-run never create output files. Production requires an
explicit pinned selection and a fresh output directory inside this batch.
The tile-r12_c06 stage needs its 16 patches and exports one 4096 tile.
The c06 stage needs all 32 c06 patches; a 64-patch full run exports four tiles.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CORE, HALO, NATIVE, OVERLAP = 1024, 115, 1254, 230
TILES = ("r12_c06", "r13_c06", "r12_c07", "r13_c07")
ANCHOR_ID = 65535


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def resolve_path(value, inside=False):
    p = Path(value)
    p = (p if p.is_absolute() else ROOT / p).resolve()
    if inside:
        require(p.is_relative_to(ROOT), f"Path escapes batch directory: {p}")
    return p


def local(path):
    p = Path(path).resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p)


def pinned(value, snapshots, inside=False):
    require(isinstance(value, dict), "Pinned reference must be {path, sha256}")
    p = resolve_path(value.get("path", value.get("file", "")), inside)
    digest = value.get("sha256")
    require(isinstance(digest, str) and re.fullmatch(r"[0-9a-fA-F]{64}", digest),
            f"Missing or invalid SHA256 pin: {p}")
    data = p.read_bytes()
    require(sha_bytes(data) == digest.lower(), f"SHA256 mismatch: {p}")
    st = p.stat()
    snapshots[str(p)] = {"path": p, "sha256": digest.lower(),
                         "size": st.st_size, "mtimeNs": st.st_mtime_ns}
    return p, data


def parse_json(data):
    return json.loads(data.decode("utf-8-sig"))


def image_array(data, size, label):
    with Image.open(io.BytesIO(data)) as im:
        require(im.format == "PNG" and im.size == tuple(size),
                f"Wrong native PNG dimensions/format: {label}: {im.size}")
        require(im.mode in ("RGB", "RGBA"), f"Unsupported pixel mode: {label}")
        im.load()
        if im.mode == "RGBA":
            require(im.getextrema()[3] == (255, 255), f"Nonopaque map source: {label}")
        return np.asarray(im)[..., :3].copy()


def validate_plan(plan):
    require(plan.get("batch") == "village-west-courtyard", "Wrong batch plan")
    require(plan.get("allocation", {}).get("status") == "allocated_root_reserved",
            "Plan does not record the current root-reserved allocation")
    require(set(plan.get("scopeTiles", [])) == set(TILES), "Scope tile mismatch")
    require(plan.get("nativeCoreSize") == CORE and plan.get("halo") == HALO,
            "Core/halo contract mismatch")
    require(plan.get("expectedNativeDimensions") == [NATIVE, NATIVE],
            "Native dimensions mismatch")
    expected = {}
    for ti, tile in enumerate(TILES):
        tr, tc = map(int, re.findall(r"\d+", tile))
        for sr in range(1, 5):
            for sc in range(1, 5):
                x = (tc - 1) * 4096 + (sc - 1) * CORE
                y = (tr - 1) * 4096 + (sr - 1) * CORE
                key = tile, f"p{sr:02d}_{sc:02d}"
                expected[key] = {"sourceId": ti * 16 + (sr - 1) * 4 + sc,
                                 "globalCoreBox": [x, y, x + CORE, y + CORE],
                                 "globalNativeBox": [x - HALO, y - HALO,
                                                     x + CORE + HALO, y + CORE + HALO]}
    entries = plan.get("nativePatches", [])
    require(len(entries) == 64, "Plan must list exactly 64 patches")
    seen = set()
    for e in entries:
        key = e.get("tile"), e.get("patch")
        require(key in expected and key not in seen, f"Unknown/duplicate planned slot: {key}")
        seen.add(key)
        ref = expected[key]
        require(e.get("order") == ref["sourceId"], f"Order mismatch: {key}")
        for field in ("globalCoreBox", "globalNativeBox"):
            require(e.get(field) == ref[field], f"Coordinate mismatch: {key}/{field}")
        require(e.get("coreInNative") == [115, 115, 1139, 1139], f"Core crop mismatch: {key}")
    require(plan.get("batchCoreBox") == [20480, 45056, 28672, 53248], "Batch core changed")
    require(plan.get("batchContextBox") == [20365, 44941, 28787, 53363], "Batch context changed")
    return expected


def load_selection(selection, expected, snapshots):
    require(selection.get("schemaVersion") == 1, "Unsupported selection schema")
    require(selection.get("batch") == "village-west-courtyard", "Wrong selection batch")
    require(isinstance(selection.get("sources"), list), "Selection.sources must be an explicit list")
    loaded = {}
    for e in selection["sources"]:
        key = e.get("tile"), e.get("patch")
        require(key in expected and key not in loaded, f"Unknown/duplicate selected slot: {key}")
        require(e.get("state", "selected") == "selected", f"Unselected entry present: {key}")
        p, data = pinned(e, snapshots, inside=True)
        require(p.suffix.lower() == ".png", f"Source must be PNG: {p}")
        arr = image_array(data, [NATIVE, NATIVE], str(p))
        gp, gdata = pinned(e.get("generationRecord"), snapshots, inside=True)
        g = parse_json(gdata)
        image_hash = sha_bytes(data)
        require(g.get("sha256") == image_hash, f"Generation record image hash differs: {gp}")
        recorded_path = g.get("file", g.get("path"))
        require(recorded_path and resolve_path(recorded_path) == p,
                f"Generation record image path differs: {gp}")
        coords = g.get("coordinates", {})
        corebox = g.get("globalCoreBox", coords.get("globalCoreBox"))
        nativebox = g.get("globalNativeBox", coords.get("globalNativeBox", coords.get("globalContextBox")))
        require(corebox == expected[key]["globalCoreBox"], f"Recorded core box differs: {gp}")
        require(nativebox == expected[key]["globalNativeBox"], f"Recorded native box differs: {gp}")
        dimensions = [g.get("width"), g.get("height")]
        require(dimensions == [NATIVE, NATIVE], f"Recorded dimensions differ: {gp}")
        resampled = g.get("nativeScaleResampled", g.get("nativePixelsResampled"))
        require(resampled is False, f"Record does not explicitly deny native resampling: {gp}")
        require(g.get("route") == "builtin", f"Unapproved source route: {gp}")
        require("actualModel" in g and "actualQuality" in g, f"Actual model/quality fields missing: {gp}")
        state = str(g.get("status", "")).lower()
        require(not any(t in state for t in ("rejected", "superseded", "layout-only", "guide-only")),
                f"Rejected/guide source cannot be selected: {gp}")
        loaded[key] = {"array": arr, "sourceId": expected[key]["sourceId"],
                       "tile": key[0], "patch": key[1], "path": local(p),
                       "sha256": image_hash, "generationRecord": {"path": local(gp), "sha256": sha_bytes(gdata)},
                       "globalCoreBox": corebox, "globalNativeBox": nativebox,
                       "dimensions": [NATIVE, NATIVE], "sourceKind": "generated-native-patch",
                       "actualModel": g["actualModel"], "actualQuality": g["actualQuality"],
                       "route": g["route"], "nativePixelsResampled": False}
    return loaded


def minimum_seam(a, b):
    require(a.shape == b.shape and a.ndim == 3, "Overlap shape mismatch")
    diff = a.astype(np.int32) - b.astype(np.int32)
    cost = np.sum(diff * diff, axis=2, dtype=np.int64)
    h, w = cost.shape
    previous = cost[0].copy()
    back = np.zeros((h, w), dtype=np.int8)
    inf = np.int64(1 << 60)
    offsets = np.array([0, -1, 1], dtype=np.int8)
    for y in range(1, h):
        left = np.concatenate(([inf], previous[:-1]))
        right = np.concatenate((previous[1:], [inf]))
        candidates = np.stack((previous, left, right))
        choice = np.argmin(candidates, axis=0)
        back[y] = offsets[choice]
        previous = cost[y] + candidates[choice, np.arange(w)]
    path = np.empty(h, dtype=np.int32)
    path[-1] = np.argmin(previous)
    total = int(previous[path[-1]])
    for y in range(h - 1, 0, -1):
        path[y - 1] = path[y] + back[y, path[y]]
    require(np.all((path >= 0) & (path < w)) and np.all(np.abs(np.diff(path)) <= 1),
            "Invalid/disconnected seam path")
    return path, total


def append_hard(base, ids, incoming, incoming_ids):
    require(base.shape[0] == incoming.shape[0], "Append height differs")
    a, b = base[:, -OVERLAP:], incoming[:, :OVERLAP]
    path, total = minimum_seam(a, b)
    take = np.arange(OVERLAP)[None, :] >= path[:, None]
    overlap = np.where(take[..., None], b, a)
    overlap_ids = np.where(take, incoming_ids[:, :OVERLAP], ids[:, -OVERLAP:])
    return (np.concatenate((base[:, :-OVERLAP], overlap, incoming[:, OVERLAP:]), axis=1),
            np.concatenate((ids[:, :-OVERLAP], overlap_ids, incoming_ids[:, OVERLAP:]), axis=1),
            path, total)


def compose(loaded, cols, rows=8):
    grid = {}
    for key, s in loaded.items():
        x, y = s["globalCoreBox"][:2]
        gx, gy = (x - 20480) // CORE, (y - 45056) // CORE
        if 0 <= gx < cols and 0 <= gy < rows:
            grid[gy, gx] = s
    require(set(grid) == {(r, c) for r in range(rows) for c in range(cols)}, "Stage rectangle is incomplete")
    strips, strip_ids, seams = [], [], []
    for r in range(rows):
        s = grid[r, 0]
        strip = s["array"].copy()
        ids = np.full((NATIVE, NATIVE), s["sourceId"], dtype=np.uint16)
        for c in range(1, cols):
            s = grid[r, c]
            incoming_ids = np.full((NATIVE, NATIVE), s["sourceId"], dtype=np.uint16)
            strip, ids, path, total = append_hard(strip, ids, s["array"], incoming_ids)
            seams.append({"axis": "vertical", "stage": "row-strip", "row": r,
                          "columnBoundary": c, "overlap": OVERLAP,
                          "pathLocal": path.tolist(), "contextXByY": (c * CORE + path).tolist(),
                          "contextYStart": r * CORE, "pathCostSumSquaredRGB": total,
                          "selectionRule": "incoming if local x >= path; otherwise existing",
                          "laterHorizontalCutsMaySupersede": True})
        strips.append(strip)
        strip_ids.append(ids)
    assembled, ids = strips[0], strip_ids[0]
    for r in range(1, rows):
        transposed, trans_ids, path, total = append_hard(
            assembled.transpose(1, 0, 2), ids.T,
            strips[r].transpose(1, 0, 2), strip_ids[r].T)
        assembled, ids = transposed.transpose(1, 0, 2), trans_ids.T
        seams.append({"axis": "horizontal", "stage": "strip-stack", "rowBoundary": r,
                      "overlap": OVERLAP, "pathLocal": path.tolist(),
                      "contextYByX": (r * CORE + path).tolist(), "contextXStart": 0,
                      "pathCostSumSquaredRGB": total,
                      "selectionRule": "incoming if local y >= path; otherwise existing"})
    require(assembled.shape == (rows * CORE + OVERLAP, cols * CORE + OVERLAP, 3), "Assembled context size mismatch")
    return assembled, ids, seams, list(grid.values())


def load_north_anchor(plan, snapshots):
    anchor = plan.get("northAnchor")
    require(isinstance(anchor, dict), "No pinned north anchor in plan")
    p, data = pinned(anchor, snapshots)
    arr = image_array(data, [4326, 4326], str(p))
    upstream = None
    if anchor.get("trace"):
        ref = anchor["trace"]
        if isinstance(ref, dict):
            tp, tdata = pinned(ref, snapshots)
        else:
            tp = resolve_path(ref)
            tdata = tp.read_bytes()
            st = tp.stat()
            snapshots[str(tp)] = {"path": tp, "sha256": sha_bytes(tdata),
                                  "size": st.st_size, "mtimeNs": st.st_mtime_ns}
        upstream = {"path": str(tp), "sha256": sha_bytes(tdata),
                    "replayDepth": "context pixels verified directly; upstream native chain retained, not flattened"}
    return {"sourceId": ANCHOR_ID, "array": arr, "path": str(p),
            "sha256": sha_bytes(data), "sourceKind": "derived-upstream-context",
            "dimensions": [4326, 4326], "globalNativeBox": [20365, 40845, 24691, 45171],
            "upstreamTrace": upstream, "role": "top halo only; no new or external core changed"}


def inherit_north_halo(plan, pixels, ids, sources, snapshots):
    source = load_north_anchor(plan, snapshots)
    # Target context starts y=44941; the new core starts y=45056.
    # Only y<45056 is inherited. New-core pixels are never replaced.
    pixels[:HALO, :4326] = source["array"][4096:4211, :4326]
    ids[:HALO, :4326] = ANCHOR_ID
    sources.append(source)
    return {"sourceId": ANCHOR_ID, "sourceBox": [0, 4096, 4326, 4211],
            "targetContextBox": [0, 0, 4326, 115], "coreAffectedPixels": 0,
            "externalOwnerFilesWritten": False, "externalQa": "pending"}


def replay(pixels, ids, sources):
    by_id = {s["sourceId"]: s for s in sources}
    counts = {sid: 0 for sid in by_id}
    mismatches, uncovered = 0, 0
    for y0 in range(0, ids.shape[0], 256):
        tile_ids = ids[y0:y0 + 256]
        for value in np.unique(tile_ids):
            sid = int(value)
            require(sid in by_id, f"Unmapped source ID: {sid}")
            yy, xx = np.nonzero(tile_ids == sid)
            yy = yy + y0
            source = by_id[sid]
            box = source["globalNativeBox"]
            sx, sy = xx + 20365 - box[0], yy + 44941 - box[1]
            arr = source["array"]
            require(np.all((sx >= 0) & (sy >= 0) & (sx < arr.shape[1]) & (sy < arr.shape[0])),
                    f"Source ID {sid} samples outside registered native box")
            mismatches += int(np.count_nonzero(np.any(pixels[yy, xx] != arr[sy, sx], axis=1)))
            counts[sid] += int(xx.size)
    uncovered = int(ids.size - sum(counts.values()))
    require(mismatches == 0 and uncovered == 0, "Native source replay failed")
    require(not np.any(ids[HALO:-HALO, HALO:-HALO] == ANCHOR_ID), "Upstream halo leaked into new core")
    return {"contextPixels": int(ids.size), "mismatches": mismatches, "uncovered": uncovered,
            "sourcePixelCounts": {str(k): v for k, v in counts.items()},
            "newCoreContainsOnlySelectedGeneratedNativePatches": True,
            "upstreamAnchorCoreAffectedPixels": 0}


def unchanged(snapshots):
    for s in snapshots.values():
        require(file_sha(s["path"]) == s["sha256"], f"Input changed during assembly: {s['path']}")


def save_json(path, data):
    with path.open("x", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def save_image(path, arr):
    with path.open("xb") as f:
        Image.fromarray(arr).save(f, format="PNG")
    return {"path": path.name, "sha256": file_sha(path),
            "dimensions": [arr.shape[1], arr.shape[0]]}


def export_outputs(output, pixels, ids, seams, sources, proof, mode, args, snapshots, north):
    output.mkdir(parents=True, exist_ok=False)
    context = save_image(output / "context-native.png", pixels)
    source_map = save_image(output / "source-id.png", ids.astype(np.uint16))
    tiles = []
    exported_tiles = TILES if mode == "full" else TILES[:1] if mode == "tile-r12_c06" else ()
    if exported_tiles:
        for tile in exported_tiles:
            tr, tc = map(int, re.findall(r"\d+", tile))
            x, y = (tc - 6) * 4096 + HALO, (tr - 12) * 4096 + HALO
            crop = pixels[y:y + 4096, x:x + 4096]
            ref = save_image(output / f"{tile}.candidate.png", crop)
            ref.update(tile=tile, contextCropBox=[x, y, x + 4096, y + 4096],
                       globalCoreBox=[(tc - 1) * 4096, (tr - 1) * 4096, tc * 4096, tr * 4096],
                       formalAccepted=False, internalQa="pending", externalQa="pending")
            tiles.append(ref)
    qa_dir = output / "qa-native"
    qa_dir.mkdir()
    qa = []
    cols = 8 if mode == "full" else 4
    rows = 4 if mode == "tile-r12_c06" else 8
    def qa_crop(label, box, kind):
        x0, y0, x1, y1 = box
        ref = save_image(qa_dir / (label + ".png"), pixels[y0:y1, x0:x1])
        ref.update(path="qa-native/" + ref["path"], kind=kind, sourceContextBox=box,
                   sourceContextSha256=context["sha256"], scale=1,
                   operation="integer crop only; no resize or RGB rewriting", reviewed=False)
        qa.append(ref)
    for r in range(rows):
        for c in range(1, cols):
            cx, y0 = HALO + c * CORE, HALO + r * CORE
            qa_crop(f"vertical-r{r + 1:02d}-c{c:02d}", [cx - 345, y0, cx + 345, y0 + CORE], "seam")
    for r in range(1, rows):
        for c in range(cols):
            cy, x0 = HALO + r * CORE, HALO + c * CORE
            qa_crop(f"horizontal-r{r:02d}-c{c + 1:02d}", [x0, cy - 345, x0 + CORE, cy + 345], "seam")
    for r in range(1, rows):
        for c in range(1, cols):
            cx, cy = HALO + c * CORE, HALO + r * CORE
            qa_crop(f"junction-r{r:02d}-c{c:02d}", [cx - 345, cy - 345, cx + 345, cy + 345], "junction")
    legend = [{k: v for k, v in s.items() if k != "array"} for s in sources]
    record = {"schemaVersion": 1, "assemblyVersion": 3, "batch": "village-west-courtyard",
              "createdAtUtc": datetime.now(timezone.utc).isoformat(), "stage": mode,
              "status": "native-assembled-pending-visual-and-external-QA",
              "formalAccepted": False, "completeMap": False,
              "scopeTiles": list(TILES) if mode == "full" else list(TILES[:1]) if mode == "tile-r12_c06" else list(TILES[:2]),
              "missingUnfilledTiles": [] if mode == "full" else list(TILES[1:]) if mode == "tile-r12_c06" else list(TILES[2:]),
              "globalContextBox": [20365, 44941, 20365 + pixels.shape[1], 44941 + pixels.shape[0]],
              "context": context, "sourceIdMap": source_map, "tiles": tiles,
              "sourceLegend": legend, "seams": seams, "proof": proof, "northHaloInheritance": north,
              "composition": {"method": "230px minimum squared-RGB-error DP hard source selection",
                              "tieOrder": ["same", "previous-1", "previous+1"], "maxPathStep": 1,
                              "rowStripsThenHorizontalStack": True, "finalSourceIdMapAuthoritative": True,
                              "resample": False, "blend": False, "feather": False,
                              "paint": False, "colorProcessing": False, "guidePixelsUsed": False},
              "qa": {"nativeCrops": qa, "reviewed": False, "external": "pending"},
              "inputs": [{"path": str(s["path"]), "sha256": s["sha256"]} for s in snapshots.values()],
              "script": {"path": str(Path(__file__).resolve()), "sha256": file_sha(__file__)},
              "inputSelectionSha256": args.selection_sha256.lower(),
              "worldMappingValidated": False, "navigationValidated": False, "capacity5000Validated": False}
    save_json(output / "assembly.json", record)
    return {"outputDirectory": str(output), "assemblySha256": file_sha(output / "assembly.json"),
            "stage": mode, "exported4096Candidates": len(tiles), "qaNativeCropCount": len(qa), "proof": proof}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", default="production-plan-v1.json")
    parser.add_argument("--validate-plan", action="store_true", help="Validate 64 planned boxes; no files written")
    parser.add_argument("--selection", help="Explicit versioned JSON manifest; no discovery or newest-file inference")
    parser.add_argument("--selection-sha256", help="Required SHA256 pin of the explicit selection JSON")
    parser.add_argument("--dry-run", action="store_true", help="Validate selection hashes, sources and geometry; no output/DP")
    parser.add_argument("--stage", choices=("auto", "tile-r12_c06", "c06", "full"), default="auto")
    parser.add_argument("--output-dir", help="Fresh output directory INSIDE this batch; existing paths are refused")
    parser.add_argument("--north-halo", action="store_true", help="Copy pinned r11_c06 pixels into top halo only")
    args = parser.parse_args(argv)
    plan_path = resolve_path(args.plan, inside=True)
    plan_data = plan_path.read_bytes()
    plan = parse_json(plan_data)
    expected = validate_plan(plan)
    if args.validate_plan:
        require(not args.selection and not args.output_dir and not args.north_halo,
                "--validate-plan is standalone and does not read selection or produce output")
        print(json.dumps({"valid": True, "patchCount": 64, "uniqueCoreCount": len(expected),
                          "planSha256": sha_bytes(plan_data), "writes": 0}))
        return 0
    require(args.selection and args.selection_sha256, "Explicit --selection and --selection-sha256 are required")
    snapshots = {}
    selection_path, selection_data = pinned({"path": args.selection, "sha256": args.selection_sha256}, snapshots, inside=True)
    selection = parse_json(selection_data)
    pinned_plan, pinned_plan_data = pinned(selection.get("plan"), snapshots, inside=True)
    require(pinned_plan == plan_path and pinned_plan_data == plan_data, "Selection pins a different/changed plan")
    loaded = load_selection(selection, expected, snapshots)
    full = len(loaded) == 64
    c06 = all(k in loaded for k in expected if k[0] in TILES[:2])
    tile_r12_c06 = all(k in loaded for k in expected if k[0] == "r12_c06")
    mode = ("full" if full else "c06" if c06 else "tile-r12_c06" if tile_r12_c06 else None) if args.stage == "auto" else args.stage
    if args.dry_run:
        require(not args.output_dir, "--dry-run never accepts an output directory")
        if args.north_halo:
            load_north_anchor(plan, snapshots)
        unchanged(snapshots)
        ready = full if args.stage == "full" else c06 if args.stage == "c06" else tile_r12_c06 if args.stage == "tile-r12_c06" else bool(mode)
        require(args.stage == "auto" or ready,
                "Requested stage is incomplete; no output or filling permitted")
        print(json.dumps({"valid": True, "writes": 0, "selectedNativeSources": len(loaded),
                          "completeR12C06Tile": tile_r12_c06, "completeC06Stage": c06, "completeFullBatch": full,
                          "requestedStage": args.stage, "requestedStageReady": ready,
                          "northHaloValidated": bool(args.north_halo),
                          "recommendedStage": "full" if full else "c06" if c06 else "tile-r12_c06" if tile_r12_c06 else None,
                          "missingSlots": [f"{t}/{p}" for t, p in expected if (t, p) not in loaded]}))
        return 0
    require(mode is not None, "No complete stage rectangle; no output will be written")
    require((mode == "full" and full) or (mode == "c06" and c06) or (mode == "tile-r12_c06" and tile_r12_c06), "Requested stage is incomplete; no filling permitted")
    require(args.output_dir, "Production requires an explicit new --output-dir")
    output = resolve_path(args.output_dir, inside=True)
    require(output != ROOT and not output.exists(), "Output directory already exists or equals batch root")
    require(not output.is_relative_to(ROOT / "native") and not output.is_relative_to(ROOT / "scripts"),
            "Assembly output cannot be inside native or scripts directories")
    require(output.is_relative_to(ROOT / "qa"), "Assembly output must be a fresh versioned directory inside batch qa")
    pixels, ids, seams, sources = compose(loaded, 8 if mode == "full" else 4, 4 if mode == "tile-r12_c06" else 8)
    north = inherit_north_halo(plan, pixels, ids, sources, snapshots) if args.north_halo else None
    proof = replay(pixels, ids, sources)
    unchanged(snapshots)
    print(json.dumps(export_outputs(output, pixels, ids, seams, sources, proof, mode, args, snapshots, north)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc), "status": "assembly-refused"}), file=sys.stderr)
        raise SystemExit(2)
