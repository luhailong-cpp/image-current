"""Local native-image pipeline; never invokes generation and never grants visual QA.

Commands (Python with Pillow and NumPy):
  pipeline.py prepare r04_c04 s04_02
  pipeline.py ingest r04_c04 s04_01 --source host.png --parameters args.json --receipt result.json
  pipeline.py assemble r04_c04 --method minimum-error
  pipeline.py progress
  pipeline.py self-check

All writes stay under this file's directory. Existing bootstrap files are read
only. prepare writes unique pipeline-guides runs; ingest never overwrites native
files. The only mutable files are pipeline-selection.json and progress.json.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
CONTRACT = PROJECT / "production-contract.json"
ASSIGNMENTS = PROJECT.parent / "acceleration-20261010" / "assignments.json"
OWNED = ("r04_c04", "r04_c05", "r03_c04", "r03_c05")
GRID, CORE, HALO, PATCH, TILE, CANVAS = 4, 1024, 115, 1254, 4096, 65536
OVERLAP = 2 * HALO
PATCH_RE = re.compile(r"s(0[1-4])_(0[1-4])")


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def owned_path(path):
    path = Path(path).resolve()
    path.relative_to(ROOT)
    return path


def put_bytes(path, data):
    path = owned_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write(data)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def put_json(path, value):
    put_bytes(path, json_bytes(value))


def replace_json(path, value):
    path = owned_path(path)
    if path.name not in {"progress.json", "pipeline-selection.json", "worker-progress.json"}:
        raise ValueError("Only this pipeline's mutable state files may be replaced")
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".writing")
    put_bytes(tmp, json_bytes(value))
    os.replace(tmp, path)


def save_png(path, im):
    stream = io.BytesIO()
    im.save(stream, format="PNG")
    put_bytes(path, stream.getvalue())
    with Image.open(path) as saved:
        saved.load()
        if saved.mode != im.mode or saved.size != im.size or saved.tobytes() != im.tobytes():
            raise AssertionError("PNG save changed pixels")
    return {"file": str(path), "sha256": sha(path), "pixels": list(im.size), "mode": im.mode}


def contract():
    c = read(CONTRACT)
    p = c["nativePatchPlan"]
    if c["artCanvasPixels"] != [CANVAS, CANVAS] or c["formalTilePixels"] != [TILE, TILE]:
        raise ValueError("Contract coordinate system changed")
    if [p[k] for k in ("subrows", "subcolumns", "corePixels", "haloPixels", "expectedNativePixels")] != [GRID, GRID, CORE, HALO, PATCH]:
        raise ValueError("Contract patch geometry changed")
    assignment = next(a for a in read(ASSIGNMENTS)["assignments"] if a["id"] == "city_yamen_north")
    if set(assignment["coordinates"]) != set(OWNED) or Path(assignment["outputDirectory"]).resolve() != ROOT:
        raise ValueError("Exclusive assignment no longer matches this pipeline")
    return c


def validate_tile(tile):
    if tile not in OWNED:
        raise ValueError("Write target outside the four assigned tiles")


def tile_box(tile):
    m = re.fullmatch(r"r(0[1-9]|1[0-6])_c(0[1-9]|1[0-6])", tile)
    if not m:
        raise ValueError("Invalid tile")
    r, c = map(int, m.groups())
    x, y = (c - 1) * TILE, (r - 1) * TILE
    return [x, y, x + TILE, y + TILE]


def coords(tile, patch):
    m = PATCH_RE.fullmatch(patch)
    if not m:
        raise ValueError("Patch must be s01_01 through s04_04")
    r, c = map(int, m.groups())
    b = tile_box(tile)
    x, y = b[0] + (c - 1) * CORE, b[1] + (r - 1) * CORE
    return {"tile": tile, "patch": patch, "tileWorldBox": b,
            "coreWorldBox": [x, y, x + CORE, y + CORE],
            "worldBoxWithHalo": [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO],
            "coreCrop": [HALO, HALO, HALO + CORE, HALO + CORE]}


def identifier(patch, version):
    coords(OWNED[0], patch)
    if version and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", version):
        raise ValueError("Invalid version suffix")
    return patch + ("_" + version if version else "")


def patch_ids():
    return [f"s{r:02d}_{c:02d}" for r in range(1, 5) for c in range(1, 5)]


def production_order():
    return [(tile, f"s{r:02d}_{c:02d}") for tile in OWNED for r in range(4, 0, -1) for c in range(1, 5)]


def intersect(a, b):
    value = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    return value if value[0] < value[2] and value[1] < value[3] else None


def tile_dir(tile, c):
    if tile in OWNED:
        return ROOT / tile
    r, col = int(tile[1:3]), int(tile[5:7])
    owner = next(z for z in c["zones"] if z["rows"][0] <= r <= z["rows"][1] and z["columns"][0] <= col <= z["columns"][1])
    return PROJECT / owner["id"] / tile


def selected(directory, patch):
    value = directory / "native" / (patch + ".png")
    for name in ("selection.json", "pipeline-selection.json"):
        file = directory / name
        if file.is_file():
            entry = read(file).get(patch)
            if isinstance(entry, dict):
                entry = entry.get("file")
            if entry:
                value = Path(entry)
                if not value.is_absolute():
                    value = directory / value
    value = value.resolve()
    value.relative_to(directory.resolve())
    return value


def native_info(path, require_record=True):
    path = Path(path)
    with Image.open(path) as im:
        size, fmt, mode = list(im.size), im.format, im.mode
        opaque = im.convert("RGBA").getchannel("A").getextrema() == (255, 255)
    if size != [PATCH, PATCH] or fmt != "PNG" or not opaque:
        raise ValueError(f"Native must be opaque PNG {PATCH}x{PATCH}: {path} is {size}/{fmt}")
    value = {"file": str(path), "sha256": sha(path), "nativePixels": size, "nativeMode": mode}
    record_file = path.with_suffix(".png.generation.json")
    if record_file.is_file():
        record = read(record_file)
        if record.get("sha256") != value["sha256"]:
            raise ValueError(f"Generation hash mismatch: {path}")
        if record.get("resizedAfterGeneration") or record.get("finalArtUpscaled"):
            raise ValueError(f"Source records resampling: {path}")
        if record.get("width") != PATCH or record.get("height") != PATCH:
            raise ValueError(f"Generation dimensions mismatch: {path}")
        value["generationRecord"] = str(record_file)
    elif require_record:
        raise ValueError(f"No generation evidence: {path}")
    return value


def reference(path, role):
    path = Path(path).resolve()
    result = {"file": str(path), "sha256": sha(path), "role": role}
    with Image.open(path) as im:
        result["pixels"] = list(im.size)
    return result


def prepare(tile, patch, version="", edges="all"):
    validate_tile(tile)
    c = contract()
    identifier(patch, version)
    coordinate = coords(tile, patch)
    target = coordinate["worldBoxWithHalo"]
    aliases = {"left": "west", "right": "east", "top": "north", "bottom": "south"}
    enabled = {"north", "east", "south", "west"} if edges == "all" else ({aliases.get(x, x) for x in edges.split(",")} if edges != "none" else set())
    if not enabled <= {"north", "east", "south", "west"}:
        raise ValueError("Invalid --edges")
    layout = Path(c["layoutReference"])
    if sha(layout) != c["layoutSha256"]:
        raise ValueError("Approved layout hash changed")
    with Image.open(layout) as opened:
        source = opened.convert("RGB")
    source_box = [target[0] * source.width / CANVAS, target[1] * source.height / CANVAS,
                  target[2] * source.width / CANVAS, target[3] * source.height / CANVAS]
    base = source.transform((PATCH, PATCH), Image.Transform.EXTENT, source_box, Image.Resampling.BICUBIC)
    run = identifier(patch, version) + "-" + uuid.uuid4().hex[:12]
    output = ROOT / tile / "pipeline-guides" / run
    layout_ref = save_png(output / "layout-only.png", base)
    anchors, unavailable = [], []
    row, col = int(tile[1:3]), int(tile[5:7])
    for nr in range(max(1, row - 1), min(16, row + 1) + 1):
        for nc in range(max(1, col - 1), min(16, col + 1) + 1):
            nt = f"r{nr:02d}_c{nc:02d}"
            nd = tile_dir(nt, c)
            for npid in patch_ids():
                if nt == tile and npid == patch:
                    continue
                nb = coords(nt, npid)["worldBoxWithHalo"]
                hit = intersect(target, nb)
                if hit is None:
                    continue
                sides = set()
                if nb[0] < target[0]: sides.add("west")
                if nb[0] > target[0]: sides.add("east")
                if nb[1] < target[1]: sides.add("north")
                if nb[1] > target[1]: sides.add("south")
                if not sides <= enabled:
                    continue
                path = selected(nd, npid)
                if not path.is_file():
                    unavailable.append({"tile": nt, "patch": npid, "reason": "not_generated"})
                    continue
                anchor = native_info(path)
                anchor.update({"tile": nt, "patch": npid, "sides": sorted(sides), "worldBoxWithHalo": nb,
                               "overlapWorldBox": hit,
                               "sourceBox": [hit[0]-nb[0], hit[1]-nb[1], hit[2]-nb[0], hit[3]-nb[1]],
                               "targetBox": [hit[0]-target[0], hit[1]-target[1], hit[2]-target[0], hit[3]-target[1]],
                               "sourceResampled": False})
                anchors.append(anchor)
    anchors.sort(key=lambda a: (-len(a["sides"]), a["tile"], a["patch"]))
    mask = Image.new("L", (PATCH, PATCH), 0)
    draw = ImageDraw.Draw(mask)
    for order, a in enumerate(anchors):
        with Image.open(a["file"]) as opened:
            fragment = opened.convert("RGB").crop(a["sourceBox"])
        box = a["targetBox"]
        base.paste(fragment, (box[0], box[1]))
        draw.rectangle((box[0], box[1], box[2]-1, box[3]-1), fill=255)
        a["pasteOrder"] = order
    guide_ref = save_png(output / "continuation-guide.png", base)
    mask_ref = save_png(output / "native-anchor-mask.png", mask)
    refs = [reference(guide_ref["file"], "layout-only geometry plus exact native context"),
            reference(layout, "approved overview; positioning only"),
            reference(c["detailStyleReference"], "approved detail material style"),
            reference(c["primaryStyleReference"], "approved Daoist chibi style")]
    for a in anchors:
        refs.append(reference(a["file"], "real neighboring native artwork"))
    manifest = {"schemaVersion": 1, "createdAt": now(), **coordinate, "id": identifier(patch, version),
                "gameArt": False, "nativeSize": [PATCH, PATCH], "layoutSource": reference(layout, "positioning only"),
                "layoutSourceBox": source_box, "layoutOnly": layout_ref, "guide": guide_ref,
                "nativeAnchorMask": mask_ref, "nativeAnchors": anchors, "missingNeighbors": unavailable,
                "references": refs, "enabledEdges": sorted(enabled), "selfAnchorExcluded": True,
                "guideOperation": "Overview enlarged only for positioning; native anchor crops pasted unchanged at exact world coordinates",
                "cornerPolicy": "corner anchors first; cardinal strips last; paste order recorded"}
    put_json(output / "preparation.json", manifest)
    return {"guide": guide_ref["file"], "manifest": str(output / "preparation.json"),
            "nativeAnchors": len(anchors), "worldBoxWithHalo": target, "references": refs}


def ingest(tile, patch, source, parameters, receipt, version="", preparation=None):
    validate_tile(tile)
    contract()
    ident = identifier(patch, version)
    directory = ROOT / tile
    dest = directory / "native" / (ident + ".png")
    record_path = dest.with_suffix(".png.generation.json")
    if dest.exists() or record_path.exists():
        raise FileExistsError("Native ID exists; use a new --version, never overwrite")
    evidence_dir = directory / "pipeline-records" / ident
    if evidence_dir.exists():
        raise FileExistsError("Evidence ID exists; use a new --version")
    params = read(parameters)
    if "prompt" not in params and "parameters" in params:
        params = params["parameters"]
    if not isinstance(params.get("prompt"), str) or not params["prompt"].strip():
        raise ValueError("Parameters JSON needs exact submitted prompt")
    if "num_last_images_to_include" in params:
        raise ValueError("Use reproducible local referenced_image_paths")
    prep = read(preparation) if preparation else None
    roles = {r["file"]: r["role"] for r in (prep or {}).get("references", [])}
    refs = [reference(p, roles.get(str(Path(p).resolve()), "actual submitted reference")) for p in params.get("referenced_image_paths", [])]
    raw_receipt = Path(receipt).read_bytes()
    receipt_data = read(receipt)  # Validate before writing any source.
    if isinstance(receipt_data, dict) and receipt_data.get("isError") is True:
        raise ValueError("Tool receipt records an error")
    host = Path(source).resolve()
    with Image.open(host) as im:
        native_size, fmt, mode, png_info = list(im.size), im.format, im.mode, dict(im.info)
        opaque = im.convert("RGBA").getchannel("A").getextrema() == (255, 255)
    if fmt != "PNG":
        raise ValueError("Original tool source must be PNG; no conversion is performed")
    # Raw byte copy preserves original PNG and its disclosed metadata.
    dest.parent.mkdir(parents=True, exist_ok=True)
    with host.open("rb") as src, dest.open("xb") as out:
        shutil.copyfileobj(src, out)
    source_hash = sha(host)
    if sha(dest) != source_hash:
        raise AssertionError("Native byte copy mismatch")
    put_json(evidence_dir / "parameters.json", params)
    put_bytes(evidence_dir / "prompt.txt", params["prompt"].encode("utf-8"))
    put_bytes(evidence_dir / "tool-result.json", raw_receipt)
    if prep is not None:
        put_json(evidence_dir / "preparation.json", prep)
    usable = native_size == [PATCH, PATCH] and opaque
    record = {"schemaVersion": 1, "file": str(dest), "sha256": source_hash, "ingestedAt": now(), "generatedAt": None,
              **coords(tile, patch), "id": ident, "width": native_size[0], "height": native_size[1],
              "format": fmt, "mode": mode, "opaque": opaque, "tool": "image_gen.imagegen", "route": "builtin",
              "hostOutputPath": str(host), "resizedAfterGeneration": False, "finalArtUpscaled": False,
              "nativeDimensionsMatchPlan": native_size == [PATCH, PATCH], "usableGeometry": usable,
              "actualModel": None, "actualQuality": None,
              "unverifiedReason": "No independently verified actual execution model/quality; raw tool receipt retained",
              "submittedParameters": params, "references": refs,
              "prompt": str(evidence_dir / "prompt.txt"),
              "evidence": {"request": str(evidence_dir / "parameters.json"), "receipt": str(evidence_dir / "tool-result.json"),
                           "requestSha256": sha(evidence_dir / "parameters.json"), "receiptSha256": sha(evidence_dir / "tool-result.json"),
                           "promptSha256": sha(evidence_dir / "prompt.txt"), "pngInfo": png_info},
              "status": "native_candidate_pending_visual_seam_review" if usable else "native_preserved_rejected_geometry",
              "formalAccepted": False}
    # PNG metadata may contain bytes; retain a truthful printable representation.
    record["evidence"]["pngInfo"] = {k: v if isinstance(v, (str, int, float, bool, type(None))) else repr(v) for k, v in png_info.items()}
    put_json(record_path, record)
    if usable:
        selection_path = directory / "pipeline-selection.json"
        selection = read(selection_path) if selection_path.exists() else {}
        selection[patch] = str(dest)
        replace_json(selection_path, selection)
    progress = update_progress()
    return {"file": str(dest), "record": str(record_path), "nativePixels": native_size,
            "sha256": source_hash, "usableGeometry": usable, "nextCoordinate": progress["nextCoordinate"]}


def minimum_seam(left, right):
    if left.shape != right.shape:
        raise ValueError("Overlap shapes differ")
    d = left.astype(np.float32) - right.astype(np.float32)
    cost = np.mean(d * d, axis=2)
    height, width = cost.shape
    center = (width - 1) / 2
    cost += (np.abs(np.arange(width) - center) / max(center, 1)) ** 4 * (float(np.median(cost)) + 1) * .16
    previous = cost[0].copy()
    back = np.zeros((height, width), dtype=np.int8)
    for y in range(1, height):
        choices = np.stack((np.r_[np.inf, previous[:-1]], previous, np.r_[previous[1:], np.inf]))
        choice = np.argmin(choices, axis=0)
        back[y] = choice.astype(np.int8) - 1
        previous = cost[y] + np.take_along_axis(choices, choice[None, :], axis=0)[0]
    seam = np.empty(height, dtype=np.int32)
    seam[-1] = int(np.argmin(previous))
    for y in range(height-1, 0, -1):
        seam[y-1] = seam[y] + int(back[y, seam[y]])
    return seam


def append_native(base, patch, overlap=OVERLAP):
    left, right = base[:, -overlap:], patch[:, :overlap]
    seam = minimum_seam(left, right)
    choose = np.arange(overlap)[None, :] >= seam[:, None]
    joined = np.where(choose[..., None], right, left)
    return np.concatenate((base[:, :-overlap], joined, patch[:, overlap:]), axis=1), seam


def assemble_arrays(arrays, method):
    if method == "hard":
        out = np.empty((TILE, TILE, 3), dtype=np.uint8)
        for (r, c), pixels in arrays.items():
            out[r*CORE:(r+1)*CORE, c*CORE:(c+1)*CORE] = pixels[HALO:HALO+CORE, HALO:HALO+CORE]
        return Image.fromarray(out), []
    strips, paths = [], []
    for r in range(GRID):
        strip = arrays[r, 0]
        for c in range(1, GRID):
            strip, seam = append_native(strip, arrays[r, c])
            paths.append({"axis": "x", "patchRow": r+1, "nextPatchColumn": c+1, "overlapPath": seam.tolist()})
        strips.append(strip)
    out = strips[0].transpose(1, 0, 2)
    for r in range(1, GRID):
        out, seam = append_native(out, strips[r].transpose(1, 0, 2))
        paths.append({"axis": "y", "nextPatchRow": r+1, "overlapPath": seam.tolist()})
    out = out.transpose(1, 0, 2)
    if out.shape != (TILE+OVERLAP, TILE+OVERLAP, 3):
        raise AssertionError("Assembled extended geometry changed")
    return Image.fromarray(out[HALO:HALO+TILE, HALO:HALO+TILE].copy()), paths


def assemble(tile, method="minimum-error"):
    validate_tile(tile)
    contract()
    arrays, sources = {}, []
    for patch in patch_ids():
        path = selected(ROOT / tile, patch)
        ref = native_info(path)
        ref.update(coords(tile, patch))
        sources.append(ref)
        r, col = int(patch[1:3])-1, int(patch[4:6])-1
        with Image.open(path) as im:
            arrays[r, col] = np.array(im.convert("RGB"))
    image, paths = assemble_arrays(arrays, method)
    fingerprint = hashlib.sha256(json_bytes({"method": method, "sources": sources})).hexdigest()[:12]
    name = f"{tile}-pipeline-{method}-{fingerprint}-{uuid.uuid4().hex[:6]}"
    candidate_path = ROOT / tile / "candidate" / (name + ".png")
    result = save_png(candidate_path, image)
    qa_dir = ROOT / tile / "qa" / name
    qa = []
    def crop(label, box, rotate=False):
        piece = image.crop(box)
        if rotate:
            piece = piece.transpose(Image.Transpose.ROTATE_90)
        record = save_png(qa_dir / (label + ".png"), piece)
        record.update({"cropLTRB": box, "rotationCCW90": rotate, "nativePixelScale": 1,
                       "sourceResampled": False, "actuallyViewed": False, "visualVerdict": "pending"})
        qa.append(record)
    for axis in ("x", "y"):
        for pos in (CORE, 2*CORE, 3*CORE):
            for segment in range(GRID):
                start = segment*CORE
                box = [pos-160, start, pos+160, start+CORE] if axis == "x" else [start, pos-160, start+CORE, pos+160]
                crop(f"internal-{axis}{pos}-segment{segment+1:02d}", box, axis == "x")
    for y in (CORE, 2*CORE, 3*CORE):
        for x in (CORE, 2*CORE, 3*CORE):
            crop(f"junction-x{x}-y{y}", [x-160, y-160, x+160, y+160])
    metrics = []
    for (r, col), pixels in arrays.items():
        for axis, other in (("x", (r, col+1)), ("y", (r+1, col))):
            if other not in arrays:
                continue
            a = pixels[:, -OVERLAP:] if axis == "x" else pixels[-OVERLAP:, :]
            b = arrays[other][:, :OVERLAP] if axis == "x" else arrays[other][:OVERLAP, :]
            diff = np.abs(a.astype(np.int16) - b.astype(np.int16))
            metrics.append({"from": f"s{r+1:02d}_{col+1:02d}", "to": f"s{other[0]+1:02d}_{other[1]+1:02d}", "axis": axis,
                            "meanAbsoluteDifference": float(diff.mean()), "p95AbsoluteDifference": float(np.percentile(diff, 95)), "diagnosticOnly": True})
    manifest = {"schemaVersion": 1, "createdAt": now(), "tile": tile, "candidate": result,
                "method": method, "corePixels": CORE, "haloPixels": HALO, "overlapPixels": OVERLAP,
                "nativeSources": sources, "seamPaths": paths, "overlapDiagnostics": metrics,
                "qaFiles": qa, "internalSeamSegments": 24, "junctions": 9,
                "operation": "Unscaled original source pixels only; no resampling, color correction, blending or feathering",
                "seamPathCoordinates": "0-based in each 230px overlap; x joins indexed by native y; y joins indexed by extended x",
                "outerCropLTRB": [HALO, HALO, HALO+TILE, HALO+TILE],
                "internalQA": {"status": "pending", "actuallyViewed": False},
                "externalQA": {"status": "pending", "actuallyViewed": False}, "formalAccepted": False}
    put_json(candidate_path.with_suffix(".assembly.json"), manifest)
    update_progress()
    return {"candidate": result, "manifest": str(candidate_path.with_suffix(".assembly.json")), "qaDirectory": str(qa_dir),
            "qaFiles": 33, "formalAccepted": False}


def update_progress():
    old_path = ROOT / "progress.json"
    value = read(old_path) if old_path.exists() else {}
    tiles, valid, errors = {}, set(), []
    for tile in OWNED:
        sources = []
        for patch in patch_ids():
            path = selected(ROOT / tile, patch)
            if not path.is_file():
                continue
            try:
                source = native_info(path)
            except (ValueError, OSError, KeyError) as exc:
                errors.append({"tile": tile, "patch": patch, "error": str(exc)})
                continue
            valid.add((tile, patch))
            sources.append({"patch": patch, **source})
        wanted_hashes = sorted(s["sha256"] for s in sources)
        current_candidates = []
        for assembly in (ROOT / tile / "candidate").glob("*-pipeline-*.assembly.json"):
            record = read(assembly)
            if len(sources) == 16 and sorted(s["sha256"] for s in record["nativeSources"]) == wanted_hashes:
                current_candidates.append({"manifest": str(assembly), "candidate": record["candidate"]})
        tiles[tile] = {"usableSelectedNativeCount": len(sources), "nativeSources": sources,
                       "currentCandidates": current_candidates, "completeNativeCoverage": len(sources) == 16,
                       "visualAcceptance": "not_granted_by_pipeline"}
    next_item = next((pair for pair in production_order() if pair not in valid), None)
    value.update({"schemaVersion": 1, "updatedAt": now(), "ownedTiles": list(OWNED), "builtinOnly": True,
                  "paidApiAllowed": False, "nativeCount": len(valid), "expectedNativeCount": 64,
                  "missingNativeCount": 64-len(valid), "tilesComplete": sum(bool(t["currentCandidates"]) for t in tiles.values()),
                  "tilesWithSixteenNativeCores": sum(t["completeNativeCoverage"] for t in tiles.values()),
                  "nextCoordinate": "/".join(next_item) if next_item else None,
                  "status": "native_production_in_progress" if next_item else "candidates_pending_visual_QA",
                  "formalAcceptedCount": value.get("formalAcceptedCount", 0), "pipelineTiles": tiles,
                  "pipelineValidationErrors": errors,
                  "pipelineAcceptancePolicy": "Mechanical checks never imply visual/internal/external/formal acceptance"})
    replace_json(old_path, value)
    return value


def self_check():
    c = contract()
    a = coords("r04_c04", "s04_01")["worldBoxWithHalo"]
    b = coords("r05_c04", "s01_01")["worldBoxWithHalo"]
    assert a == [12173, 15245, 13427, 16499]
    assert intersect(a, b) == [12173, 16269, 13427, 16499]
    assert production_order()[0] == ("r04_c04", "s04_01")
    assert production_order()[15] == ("r04_c04", "s01_04")
    seed = np.random.default_rng(126)
    left = seed.integers(0, 255, (17, 10, 3), dtype=np.uint8)
    right = seed.integers(0, 255, (17, 10, 3), dtype=np.uint8)
    joined, seam = append_native(left, right, overlap=4)
    assert joined.shape == (17, 16, 3)
    assert np.array_equal(joined[:, :6], left[:, :6])
    assert np.array_equal(joined[:, -6:], right[:, -6:])
    middle = joined[:, 6:10]
    assert np.all(np.all(middle == left[:, -4:], axis=2) | np.all(middle == right[:, :4], axis=2))
    assert np.all(np.abs(np.diff(seam)) <= 1)
    refs = []
    for col in range(1, 5):
        refs.append(native_info(PROJECT / "northwest" / "r05_c04" / "native" / f"s01_{col:02d}.png"))
    return {"status": "passed", "writes": 0, "checks": ["exclusive assignment", "contract geometry", "northward 230px overlap", "bottom-to-top order", "binary pixel-preserving seam", "four real south neighbor hashes/dimensions"], "southNeighbors": refs}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("tile"); p.add_argument("patch"); p.add_argument("--version", default=""); p.add_argument("--edges", default="all")
    p = sub.add_parser("ingest")
    p.add_argument("tile"); p.add_argument("patch"); p.add_argument("--source", required=True)
    p.add_argument("--parameters", required=True); p.add_argument("--receipt", required=True)
    p.add_argument("--version", default=""); p.add_argument("--preparation")
    p = sub.add_parser("assemble")
    p.add_argument("tile"); p.add_argument("--method", choices=("hard", "minimum-error"), default="minimum-error")
    sub.add_parser("progress"); sub.add_parser("self-check")
    args = vars(parser.parse_args())
    command = args.pop("command")
    handlers = {"prepare": prepare, "ingest": ingest, "assemble": assemble, "progress": update_progress, "self-check": self_check}
    result = handlers[command](**args)
    if command == "progress":
        result = {k: result[k] for k in ("nativeCount", "missingNativeCount", "tilesComplete", "nextCoordinate", "status", "pipelineValidationErrors")}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": type(exc).__name__, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
