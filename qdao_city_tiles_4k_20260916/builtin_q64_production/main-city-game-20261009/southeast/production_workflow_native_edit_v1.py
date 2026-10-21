#!/usr/bin/env python3
"""New southeast tiles only: immutable preparation, native ingestion and assembly.

This helper never calls an image model or grants art acceptance. Run --help.
Layout previews are enlarged GEOMETRY GUIDES ONLY, never deliverable pixels.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
ZONE = Path(__file__).resolve().parent
CONTRACT = ZONE.parent / "production-contract.json"
CONFIG = ZONE.parents[3] / "config" / "image-generation.json"
NATIVE, CORE, HALO, OVERLAP, TILE_SIZE, CONTEXT = 1254, 1024, 115, 230, 4096, 4326
PATCHES = [f"p{r:02d}_{c:02d}" for r in range(1, 5) for c in range(1, 5)]
HISTORIC_TILE = "r13_c13"
HISTORIC_CONTEXT_SHA = "d15bf1ad12cb71edcfbd54d7692c4e8b69131937b7b32c54b848bb1983e9cf12"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def atomic_json(path, value, *, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive:
        with path.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
        return
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temp.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def write_png_exclusive(path, image):
    with Path(path).open("xb") as stream:
        image.save(stream, format="PNG")


def tile_parts(tile, *, writable=True):
    match = re.fullmatch(r"r(\d{2})_c(\d{2})", tile)
    require(match, "Tile must be rNN_cNN")
    r, c = map(int, match.groups())
    require(9 <= r <= 16 and 9 <= c <= 16, "Outside southeast rows/columns 9..16")
    require(not writable or tile != HISTORIC_TILE, "Historical r13_c13 is read-only")
    return r, c


def tile_dir(tile):
    tile_parts(tile)
    return ZONE / tile


def coordinate(tile, patch):
    r, c = tile_parts(tile, writable=False)
    require(patch in PATCHES, "Patch must be p01_01 through p04_04")
    pr, pc = int(patch[1:3]), int(patch[4:6])
    x, y = (c - 1) * TILE_SIZE + (pc - 1) * CORE, (r - 1) * TILE_SIZE + (pr - 1) * CORE
    return {"id": patch, "row": pr, "column": pc,
            "coreBox": [x, y, x + CORE, y + CORE],
            "contextBox": [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO],
            "nativeExpected": [NATIVE, NATIVE], "coreCropExpected": [HALO, HALO, HALO + CORE, HALO + CORE]}


def current_authority():
    contract = read(CONTRACT)
    require(contract.get("newArtworkGenerationAllowed") is True, "Production contract does not release new artwork")
    resume_path = Path(contract["productionResumeControl"])
    resume = read(resume_path)
    require(resume.get("newArtworkGenerationAllowed") is True, "Production resume is not released")
    require(contract.get("artCanvasPixels") == [65536, 65536], "Unexpected artwork coordinate contract")
    require(contract.get("formalTilePixels") == [4096, 4096], "Unexpected formal tile contract")
    require(contract.get("builtinOnly") is True and contract.get("paidApiAllowed") is False, "Builtin-only contract required")
    plan = contract["nativePatchPlan"]
    require((plan["expectedNativePixels"], plan["corePixels"], plan["haloPixels"], plan["subrows"], plan["subcolumns"]) == (1254, 1024, 115, 4, 4), "Unexpected native patch plan")
    require(plan.get("resizeFinalArtAllowed") is False, "Final-art resizing must remain disabled")
    refs = []
    for key, hashkey, role in [("layoutReference", "layoutSha256", "approved v9 whole-city geometry reference"),
                               ("detailStyleReference", "detailSha256", "approved close-up material style"),
                               ("primaryStyleReference", "primaryStyleSha256", "current approved primary illustration style")]:
        path = Path(contract[key]).resolve()
        require(path.is_file() and sha(path) == contract[hashkey], f"Current reference missing or changed: {path}")
        with Image.open(path) as im:
            refs.append({"path": str(path), "sha256": sha(path), "dimensions": list(im.size), "role": role})
    return contract, resume, refs, resume_path


def progress(tile, status, **extra):
    t = tile_dir(tile)
    p = read(t / "progress.json") if (t / "progress.json").exists() else {}
    mapping = read(t / "active-native-map.json") if (t / "active-native-map.json").exists() else {}
    p.update(tile=tile, status=status, updatedAt=now(), activeNativeCount=len(mapping),
             formalAccepted=False, internalArtQA="pending", externalNeighborSeamQA="pending",
             worldSize=None, clientMappingValidated=False, capacity5000Validated=False)
    p.update(extra)
    atomic_json(t / "progress.json", p)


def init(tile):
    t = tile_dir(tile)
    contract, resume, refs, resume_path = current_authority()
    if (t / "initialization.json").exists():
        saved = read(t / "initialization.json")
        require(saved.get("tile") == tile and saved.get("schemaVersion") == 1, "Foreign initialization")
        require((t / "coordinates.json").exists(), "Incomplete initialization; inspect rather than overwrite")
        return {"tile": tile, "alreadyInitialized": True, "directory": str(t)}
    require(not (t / "native").exists() or not any((t / "native").iterdir()), "Existing native work cannot be initialized")
    for name in ["coordinates.json", "active-native-map.json", "progress.json"]:
        require(not (t / name).exists(), f"Existing tile evidence: {name}")
    require(not (t / "layout-only").exists() or not any((t / "layout-only").iterdir()), "Existing layout guides cannot be overwritten")
    for folder in ["layout-only", "native", "records", "review"]:
        (t / folder).mkdir(parents=True, exist_ok=True)
    r, c = tile_parts(tile)
    x, y = (c - 1) * TILE_SIZE, (r - 1) * TILE_SIZE
    bounds = [x - HALO, y - HALO, x + TILE_SIZE + HALO, y + TILE_SIZE + HALO]
    with Image.open(refs[0]["path"]) as source:
        source = source.convert("RGB")
        refbox = [bounds[0] * source.width / 65536, bounds[1] * source.height / 65536,
                  bounds[2] * source.width / 65536, bounds[3] * source.height / 65536]
        context = source.transform((CONTEXT, CONTEXT), Image.Transform.EXTENT, refbox, Image.Resampling.NEAREST)
        preview = source.transform((1254, 1254), Image.Transform.EXTENT,
                                   [x * source.width / 65536, y * source.height / 65536,
                                    (x + TILE_SIZE) * source.width / 65536, (y + TILE_SIZE) * source.height / 65536], Image.Resampling.NEAREST)
    for patch in PATCHES:
        co = coordinate(tile, patch)
        dx, dy = (co["column"] - 1) * CORE, (co["row"] - 1) * CORE
        path = t / "layout-only" / f"{patch}-layout-only.png"
        write_png_exclusive(path, context.crop((dx, dy, dx + NATIVE, dy + NATIVE)))
        atomic_json(str(path) + ".derived.json", {"role": "layout-only geometry guide; NEVER deliverable/native detail",
                    "operation": "nearest-neighbor EXTENT of approved overview, then integer crop; enlarged guide only",
                    "derivedFrom": refs[0], "artCanvasBox": co["contextBox"], "size": [NATIVE, NATIVE], "sha256": sha(path)}, exclusive=True)
    tile_guide = t / "layout-only" / "tile-layout-only.png"
    write_png_exclusive(tile_guide, preview)
    atomic_json(str(tile_guide) + ".derived.json", {"role": "layout-only overview; NEVER deliverable", "derivedFrom": refs[0],
                "artCanvasBox": [x, y, x + TILE_SIZE, y + TILE_SIZE], "operation": "nearest-neighbor EXTENT", "sha256": sha(tile_guide)}, exclusive=True)
    atomic_json(t / "coordinates.json", {"tile": tile, "coreBox": [x, y, x + TILE_SIZE, y + TILE_SIZE],
                "contextBox": bounds, "coordinateAuthority": str(CONTRACT), "referenceSha256": refs[0]["sha256"],
                "patches": [coordinate(tile, p) for p in PATCHES]}, exclusive=True)
    if not (t / "local-content.json").exists():
        atomic_json(t / "local-content.json", {}, exclusive=True)
    atomic_json(t / "active-native-map.json", {}, exclusive=True)
    atomic_json(t / "initialization.json", {"schemaVersion": 1, "tile": tile, "createdAt": now(),
                "contract": {"path": str(CONTRACT), "sha256": sha(CONTRACT), "snapshot": contract},
                "resume": {"path": str(resume_path), "sha256": sha(resume_path), "snapshot": resume},
                "layoutOnly": True, "formalAccepted": False}, exclusive=True)
    progress(tile, "initialized_pending_local_content_and_native_generation")
    return {"tile": tile, "directory": str(t), "patches": 16, "localContent": str(t / "local-content.json"), "formalAccepted": False}


def status_ok(status):
    return isinstance(status, str) and (status == "succeeded" or re.fullmatch(r"succeeded_pending_[a-z0-9_]+", status) is not None) and not any(s in status for s in ["failed", "rejected", "cancelled", "error"])


def reject_failed_record(record, label):
    state = str(record.get("status", "")).lower()
    require(state and not any(s in state for s in ["reject", "fail", "cancel", "error"]), f"Unusable record status: {label}")


def verified_native(t, patch):
    mapping = read(t / "active-native-map.json")
    require(patch in mapping, f"Adjacent native missing: {t.name}/{patch}")
    version = mapping[patch]
    require(isinstance(version, str) and re.fullmatch(re.escape(patch) + r"(?:_[A-Za-z0-9_-]+)?", version), "Invalid active version")
    path = t / "native" / f"{version}.png"
    record = read(str(path) + ".generation.json")
    reject_failed_record(record, version)
    require(record.get("resizedAfterGeneration") is False and record.get("finalArtUpscaled") is False, "Resized/unknown native source")
    require(record.get("coordinates") == coordinate(t.name, patch), "Native coordinate mismatch")
    require(sha(path) == record.get("sha256"), f"Native hash mismatch: {path}")
    with Image.open(path) as im:
        require(im.format == "PNG" and im.size == (NATIVE, NATIVE), "Native source must be actual 1254 PNG")
        im.load()
        image = im.convert("RGB")
    return image, path, record


def outer_anchor(tile, co, direction):
    r, c = tile_parts(tile)
    nr, nc = (r, c - 1) if direction == "left" else (r - 1, c)
    if not (9 <= nr <= 16 and 9 <= nc <= 16):
        return None
    name = f"r{nr:02d}_c{nc:02d}"
    nt = ZONE / name
    origin = ((nc - 1) * TILE_SIZE - HALO, (nr - 1) * TILE_SIZE - HALO)
    reliable = [(nc - 1) * TILE_SIZE, (nr - 1) * TILE_SIZE, nc * TILE_SIZE, nr * TILE_SIZE]
    expected_size = (CONTEXT, CONTEXT)
    if name == HISTORIC_TILE:
        path = nt / "candidate" / f"{name}-context-4326-repaired.png"
        require(path.is_file() and sha(path) == HISTORIC_CONTEXT_SHA, "Corrected historical neighbor context missing/changed")
        # Core-only intersection excludes ALL unreliable halo, including east x4150..4211.
        reliable = [(nc - 1) * TILE_SIZE, (nr - 1) * TILE_SIZE, nc * TILE_SIZE, nr * TILE_SIZE]
        quality = "verified corrected historical context; CORE ONLY, 115-pixel anchor; east halo local x4150..4211 excluded"
    elif (nt / "candidate" / "latest-assembly.json").exists():
        manifest = read(nt / "candidate" / "latest-assembly.json")
        path = Path(manifest["context"]["path"])
        require(path.resolve().is_relative_to(nt.resolve()), "Neighbor context path escaped tile")
        require(sha(path) == manifest["context"]["sha256"], "Neighbor context changed")
        quality = "assembled native source clipped to formal4096 CORE ONLY; 115-pixel outer anchor; unreviewed external halo excluded; visual seam pending"
    else:
        boundary = f'p{co["row"]:02d}_04' if direction == "left" else f'p04_{co["column"]:02d}'
        if not (nt / "active-native-map.json").exists() or boundary not in read(nt / "active-native-map.json"):
            return None
        image, path, record = verified_native(nt, boundary)
        origin = tuple(record["coordinates"]["contextBox"][:2])
        expected_size = (NATIVE, NATIVE)
        reliable = [max(reliable[0], origin[0]), max(reliable[1], origin[1]),
                    min(reliable[2], origin[0] + NATIVE), min(reliable[3], origin[1] + NATIVE)]
        name = name + "/" + boundary
        quality = "unscaled active native source clipped to formal4096 CORE ONLY; external115 halo excluded; art QA pending"
    cb = co["contextBox"]
    intersection = [max(cb[0], reliable[0]), max(cb[1], reliable[1]), min(cb[2], reliable[2]), min(cb[3], reliable[3])]
    require(intersection[0] < intersection[2] and intersection[1] < intersection[3], "No valid external overlap")
    scrop = [intersection[0] - origin[0], intersection[1] - origin[1], intersection[2] - origin[0], intersection[3] - origin[1]]
    target = [intersection[0] - cb[0], intersection[1] - cb[1], intersection[2] - cb[0], intersection[3] - cb[1]]
    with Image.open(path) as image:
        require(image.size == expected_size, "Neighbor source dimensions changed")
        crop = image.convert("RGB").crop(scrop)
    return crop, {"neighbor": name, "path": str(path), "sha256": sha(path), "sourceCrop": scrop,
                  "target": target, "resized": False, "reliability": quality}


def outer_corner_anchor(tile, patch):
    """One explicitly authorized immutable NW core corner for the current2x2."""
    if tile != "r14_c14" or patch != "p01_01":
        return None
    path = ZONE / HISTORIC_TILE / "candidate" / f"{HISTORIC_TILE}-context-4326-repaired.png"
    require(path.is_file() and sha(path) == HISTORIC_CONTEXT_SHA, "Historical northwest core corner changed")
    box = [TILE_SIZE, TILE_SIZE, TILE_SIZE + HALO, TILE_SIZE + HALO]
    with Image.open(path) as image:
        require(image.size == (CONTEXT, CONTEXT), "Historical northwest context dimensions changed")
        crop = image.convert("RGB").crop(box)
    return crop, {"neighbor": HISTORIC_TILE, "direction": "corner", "path": str(path), "sha256": sha(path),
                  "sourceCrop": box, "target": [0, 0, HALO, HALO], "resized": False,
                  "reliability": "immutable historical formal CORE southeast115x115 corner; independent third source, no external halo"}


def prepare(tile, patch, local_text=None):
    t = tile_dir(tile)
    require((t / "initialization.json").exists(), "Run init first")
    contract, resume, refs, resume_path = current_authority()
    co = coordinate(tile, patch)
    local = read(t / "local-content.json").get(patch)
    local_evidence = {"path": str(t / "local-content.json"), "sha256": sha(t / "local-content.json")}
    if local_text:
        extra = Path(local_text).read_text(encoding="utf-8-sig").strip()
        require(extra, "Empty local content text")
        local = (str(local) + "\n" if local else "") + extra
        local_evidence["additionalText"] = {"path": str(Path(local_text).resolve()), "sha256": sha(local_text)}
    require(isinstance(local, (str, dict, list)) and bool(local), f"Fill local-content.json[{patch!r}] after examining this crop, or pass a local text file")
    local = local if isinstance(local, str) else json.dumps(local, ensure_ascii=False)
    guide = t / "layout-only" / f"{patch}-layout-only.png"
    derivation = read(str(guide) + ".derived.json")
    require(sha(guide) == derivation["sha256"], "Layout guide changed")
    with Image.open(guide) as image:
        target = image.convert("RGB")
    anchors = []
    mask = np.zeros((NATIVE, NATIVE), dtype=bool)
    for direction in ["left", "top"]:
        adjacent = (co["column"] > 1) if direction == "left" else (co["row"] > 1)
        if adjacent:
            neighbor = f'p{co["row"]:02d}_{co["column"] - 1:02d}' if direction == "left" else f'p{co["row"] - 1:02d}_{co["column"]:02d}'
            image, path, record = verified_native(t, neighbor)
            scrop = [CORE, 0, NATIVE, NATIVE] if direction == "left" else [0, CORE, NATIVE, NATIVE]
            box = [0, 0, OVERLAP, NATIVE] if direction == "left" else [0, 0, NATIVE, OVERLAP]
            result = (image.crop(scrop), {"neighbor": tile + "/" + neighbor, "path": str(path), "sha256": sha(path),
                      "sourceCrop": scrop, "target": box, "resized": False, "reliability": "unscaled active native overlap"})
        else:
            result = outer_anchor(tile, co, direction)
        if result is None:
            continue
        crop, evidence = result
        x0, y0, x1, y1 = evidence["target"]
        overlap = mask[y0:y1, x0:x1]
        if overlap.any():
            a = np.asarray(target.crop((x0, y0, x1, y1))).astype(np.int16)
            b = np.asarray(crop).astype(np.int16)
            evidence["anchorIntersection"] = {"pixelCount": int(overlap.sum()),
                "meanAbsoluteChannelDifference": float(np.abs(a - b)[overlap].mean()),
                "precedence": "top anchor replaces left only at their intersection; geometry discrepancy remains visible-QA pending"}
        target.paste(crop, (x0, y0))
        mask[y0:y1, x0:x1] = True
        evidence["direction"] = direction
        anchors.append(evidence)
    corner = outer_corner_anchor(tile, patch)
    if corner is not None:
        corner_pixels, corner_evidence = corner
        require(not mask[:HALO, :HALO].any(), "External core strips unexpectedly overlap the independent northwest corner")
        target.paste(corner_pixels, (0, 0))
        mask[:HALO, :HALO] = True
        anchors.append(corner_evidence)
    require(anchors, "No neighboring native anchor available; connected production needs an existing left/top native")
    version = patch + "_v" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8]
    prefix = t / "records" / version
    target_path = t / "layout-only" / f"{version}-native-anchor-guide.png"
    write_png_exclusive(target_path, target)
    target_evidence = {"path": str(target_path), "sha256": sha(target_path), "dimensions": [NATIVE, NATIVE],
                       "role": "LAST IMAGE / sole edit target: nearest layout-only geometry crop plus unscaled native anchors"}
    atomic_json(str(target_path) + ".derived.json", {"role": "generation guide only; never deliverable", "layoutSource": str(guide),
                "layoutSourceSha256": sha(guide), "anchors": anchors, "anchorOrder": ["left", "top"] + (["corner"] if corner is not None else []), "sha256": sha(target_path),
                "operation": "integer native crop/paste, NO resizing of any native pixels; top wins only shared corner"}, exclusive=True)
    anchor_text = "\n".join(f'{a["direction"].upper()} anchor rectangle {a["target"]} (right/bottom exclusive): preserve its existing pixels and continue its geometry beyond that rectangle. {a["reliability"]}.' for a in anchors)
    prompt = f'''Use case: precise-object-edit / stylized game environment. Create ONE real native opaque 1254x1254 context patch, {tile}/{patch}.
Inputs 1/2/3 are reference only: approved whole-city v9 layout, approved material close-up, current mail illustration style. Input 4, THE LAST IMAGE, is the ONLY EDIT TARGET. It is a giant DETAIL CROP of the art, not a world-scale/capacity diagram and not a whole object. Keep its exact framing.
Artwork coordinates are 65536x65536: context {co['contextBox']}, core {co['coreBox']}; this is not a statement of gameplay size. The final image must contain genuinely new native detail, never a resized/pixelated layout crop.
Repaint the blocky layout-only area at native detail while retaining sharp neighboring native anchor rectangles pixel-aligned. Do not zoom out, recenter, pan, rotate, fit a whole table/umbrella/building, or copy the entire previous patch. Objects naturally continue outside the crop. Follow target silhouettes and only the essential visible local objects below; a wooden fragment does not authorize a complete table.
ANCHORS (pixel rectangles, no scaling):
{anchor_text}
At overlapping upper-left strips, the LAST target has already selected the visible anchor pixels. Continue those exact pixels, not two contradictory source images.
CONTINUITY: continue stone slab grids, grout centerlines, broad blue-grey inset road borders, wood edges and shadows through EACH anchor/new-paint boundary at exactly matching position, width, direction, spacing and value. Never restart the paving grid at x230/y230 or at the 115-pixel core boundary. Keep broad quiet slabs broad; do not substitute tiny repeated bricks. Road borders are flat inlaid stone, not channels/water/raised walls. Preserve connected open paving and building entrances visible in the target.
STYLE: rounded full bright clean Taoist chibi game painting. Natural pale-grey/blue-grey stone with restrained hand-painted shading, warm clean wood, gentle daylight. Approved references set finish/material only: do not import their buildings, furniture or scene. No gritty realism, blur, plastic glare, red paving, labels, UI, people, diagram lines, frame or watermark. No additional architecture, freestanding street-tree islands, pots or complete furniture. Only existing wall/building-side foliage where specified. Sparse festive red paper remnants are scraps, not new furnishings.
ESSENTIAL VISIBLE LOCAL CONTENT (binding for this crop):
{local}
Output a single native square filling the canvas; preserve the current partial-object framing and native anchor detail density.'''
    prompt_path = Path(str(prefix) + ".prompt.txt")
    with prompt_path.open("x", encoding="utf-8") as stream:
        stream.write(prompt)
    request = {"prompt": prompt, "referenced_image_paths": [r["path"] for r in refs] + [str(target_path)], "transparent_background": False}
    atomic_json(str(prefix) + ".request.json", request, exclusive=True)
    atomic_json(str(prefix) + ".reference-evidence.json", refs + [target_evidence], exclusive=True)
    preparation = {"schemaVersion": 1, "tile": tile, "logicalPatch": patch, "version": version, "preparedAt": now(), "coordinates": co,
                   "request": str(prefix) + ".request.json", "requestSha256": sha(str(prefix) + ".request.json"),
                   "prompt": str(prompt_path), "promptSha256": sha(prompt_path), "references": refs + [target_evidence], "anchors": anchors,
                   "localContent": local, "localContentEvidence": local_evidence, "configSnapshot": read(CONFIG),
                   "configFile": str(CONFIG), "configSha256": sha(CONFIG),
                   "contractSnapshot": contract, "contractSha256": sha(CONTRACT), "resumeSnapshot": resume, "resumeSha256": sha(resume_path),
                   "tool": "image_gen.imagegen", "route": "builtin", "actualModel": None, "actualQuality": None,
                   "submittedModel": None, "submittedQuality": None, "status": "prepared_not_generated"}
    atomic_json(str(prefix) + ".preparation.json", preparation, exclusive=True)
    progress(tile, "prepared_pending_builtin_generation", currentPatch=patch, currentVersion=version)
    return {"tile": tile, "patch": patch, "version": version, "request": preparation["request"], "target": str(target_path), "anchors": anchors}


def validate_preparation(t, version):
    require(re.fullmatch(r"p0[1-4]_0[1-4]_v[A-Za-z0-9_-]+", version), "Invalid prepared version")
    prep = read(t / "records" / f"{version}.preparation.json")
    require(prep["tile"] == t.name and prep["version"] == version, "Preparation identity mismatch")
    require(prep["coordinates"] == coordinate(t.name, prep["logicalPatch"]), "Preparation coordinates changed")
    for field in ["request", "prompt"]:
        require(sha(prep[field]) == prep[field + "Sha256"], f"Prepared {field} changed")
    request = read(prep["request"])
    require(request["prompt"] == Path(prep["prompt"]).read_text(encoding="utf-8"), "Request/prompt mismatch")
    require(request["referenced_image_paths"] == [r["path"] for r in prep["references"]], "Prepared reference order changed")
    for ref in prep["references"] + prep["anchors"]:
        require(sha(ref["path"]) == ref["sha256"], f"Prepared source missing/changed: {ref['path']}")
    return prep


def ingest(tile, version, source, receipt):
    t = tile_dir(tile)
    prep = validate_preparation(t, version)
    source, receipt = Path(source).resolve(), Path(receipt).resolve()
    require(source.is_file() and receipt.is_file(), "Source PNG and truthful receipt JSON are required")
    raw_receipt = read(receipt)
    require(status_ok(raw_receipt.get("status")), "Receipt must say succeeded or succeeded_pending_*; rejected/failed records cannot be ingested")
    require(raw_receipt.get("tool", "image_gen.imagegen") == "image_gen.imagegen", "Only builtin imagegen receipts accepted")
    require(not raw_receipt.get("resizedAfterGeneration") and not raw_receipt.get("finalArtUpscaled"), "Receipt reports resized output")
    require("layout-only" not in source.parts and not Path(str(source) + ".derived.json").exists(), "A derived layout/guide is not a native generation")
    with Image.open(source) as im:
        require(im.format == "PNG" and im.size == (NATIVE, NATIVE), f"Actual output must be native1254 PNG, received {im.format}/{im.size}; NEVER resize to fit")
        im.load()
        require(im.mode in ["RGB", "RGBA"], f"Unexpected native mode: {im.mode}")
        if im.mode == "RGBA":
            require(im.getextrema()[3] == (255, 255), "Map native must be fully opaque")
        mode = im.mode
    source_sha = sha(source)
    require(source_sha not in {r["sha256"] for r in prep["references"] + prep["anchors"]}, "Reference/anchor bytes cannot be passed as generated output")
    for key in ["sourceSha256", "outputSha256", "sha256"]:
        if raw_receipt.get(key):
            require(raw_receipt[key] == source_sha, f"Receipt output hash mismatch: {key}")
    dest = t / "native" / f"{version}.png"
    record_path = Path(str(dest) + ".generation.json")
    saved_receipt = t / "records" / f"{version}.receipt.json"
    require(not dest.exists() and not record_path.exists(), "Native versions are immutable; prepare a new version")
    require(receipt == saved_receipt.resolve() or not saved_receipt.exists(), "Saved receipt already exists; do not overwrite evidence")
    if receipt != saved_receipt.resolve():
        with receipt.open("rb") as src, saved_receipt.open("xb") as dst:
            shutil.copyfileobj(src, dst)
    with source.open("rb") as src, dest.open("xb") as dst:
        shutil.copyfileobj(src, dst)
    require(sha(dest) == source_sha, "Native byte-copy mismatch")
    record = {"schemaVersion": 1, "id": version, "logicalPatch": prep["logicalPatch"], "tile": tile, "file": str(dest),
              "sha256": source_sha, "generatedAt": raw_receipt.get("generatedAt", raw_receipt.get("createdAt")), "ingestedAt": now(),
              "width": NATIVE, "height": NATIVE, "format": "PNG", "mode": mode, "tool": "image_gen.imagegen", "route": "builtin",
              "configSnapshot": prep["configSnapshot"], "submittedParameters": {"model": None, "quality": None, "transparent_background": False,
              "referenced_image_paths": [r["path"] for r in prep["references"]]}, "actualModel": raw_receipt.get("actualModel"),
              "actualQuality": raw_receipt.get("actualQuality"), "backendModelVerified": False,
              "unverifiedReason": "Builtin host exposes no model/quality selectors; configuration/prompt is not actual backend evidence. Unknown actual values remain null.",
              "evidence": {"receipt": str(saved_receipt), "receiptSha256": sha(saved_receipt), "request": prep["request"], "requestSha256": prep["requestSha256"],
                           "preparation": str(t / "records" / f"{version}.preparation.json"), "preparationSha256": sha(t / "records" / f"{version}.preparation.json"),
                           "originalOutputPath": str(source), "originalSha256": source_sha, "receiptSuppliedPath": str(receipt)},
              "prompt": prep["prompt"], "promptSha256": prep["promptSha256"], "references": prep["references"], "anchors": prep["anchors"],
              "coordinates": prep["coordinates"], "resizedAfterGeneration": False, "finalArtUpscaled": False,
              "nativeEvidenceScope": "Actual received1254 PNG copied byte-for-byte without resizing; native detail still requires visual review",
              "status": "native_in_progress_pending_seam_and_layout_review", "formalAccepted": False}
    atomic_json(record_path, record, exclusive=True)
    mapping = read(t / "active-native-map.json")
    previous = mapping.get(prep["logicalPatch"])
    mapping[prep["logicalPatch"]] = version
    atomic_json(t / "active-native-map.json", mapping)
    nxt = next((p for p in PATCHES if p not in mapping), None)
    progress(tile, "native_ingested_pending_review" if nxt else "sixteen_natives_pending_assembly_and_review",
             currentPatch=nxt, lastIngestedVersion=version, previousActiveVersion=previous)
    return {"tile": tile, "version": version, "file": str(dest), "sha256": source_sha, "activeNativeCount": len(mapping), "nextPatch": nxt, "formalAccepted": False}


def assemble(tile):
    """Build an immutable candidate from sixteen verified natives; never grant QA."""
    t = tile_dir(tile)
    guards = {}

    def checked(path, expected=None):
        path = Path(path).resolve()
        require(path.is_file(), f"Assembly input missing: {path}")
        digest = sha(path)
        if expected is not None:
            require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected), f"Invalid recorded hash: {path}")
            require(digest == expected, f"Assembly input changed: {path}")
        require(str(path) not in guards or guards[str(path)] == digest, f"Input changed during validation: {path}")
        guards[str(path)] = digest
        return digest

    def unchanged():
        for filename, digest in guards.items():
            require(Path(filename).is_file() and sha(filename) == digest, f"Input changed during assembly: {filename}")

    def evidence_path(value, *, local=False):
        require(isinstance(value, str) and bool(value), "Missing evidence path")
        path = Path(value)
        path = (path if path.is_absolute() else t / path).resolve()
        require(not local or path.is_relative_to(t.resolve()), f"Tile evidence path escaped tile: {path}")
        return path

    checked(t / "initialization.json")
    initialization = read(t / "initialization.json")
    require(initialization.get("schemaVersion") == 1 and initialization.get("tile") == tile, "Invalid tile initialization")
    checked(CONTRACT)
    contract = read(CONTRACT)
    require(contract.get("artCanvasPixels") == [65536, 65536] and contract.get("formalTilePixels") == [TILE_SIZE, TILE_SIZE]
            and contract.get("rows") == 16 and contract.get("columns") == 16, "Artwork coordinate contract changed")
    plan = contract.get("nativePatchPlan", {})
    require((plan.get("expectedNativePixels"), plan.get("corePixels"), plan.get("haloPixels"), plan.get("subrows"), plan.get("subcolumns"))
            == (NATIVE, CORE, HALO, 4, 4) and plan.get("resizeFinalArtAllowed") is False, "Native composition contract changed")
    require(contract.get("builtinOnly") is True and contract.get("paidApiAllowed") is False, "Builtin-only composition required")
    checked(t / "coordinates.json")
    co = read(t / "coordinates.json")
    r, c = tile_parts(tile)
    x, y = (c - 1) * TILE_SIZE, (r - 1) * TILE_SIZE
    require(co.get("tile") == tile and co.get("coreBox") == [x, y, x + TILE_SIZE, y + TILE_SIZE]
            and co.get("contextBox") == [x - HALO, y - HALO, x + TILE_SIZE + HALO, y + TILE_SIZE + HALO]
            and co.get("patches") == [coordinate(tile, p) for p in PATCHES], "Tile coordinates changed")
    checked(t / "active-native-map.json")
    active = read(t / "active-native-map.json")
    require(set(active) == set(PATCHES), f"Exactly16 logical patches required; missing={sorted(set(PATCHES) - set(active))}; extra={sorted(set(active) - set(PATCHES))}")
    require(all(isinstance(v, str) for v in active.values()) and len(set(active.values())) == 16, "Active native versions must be sixteen distinct names")
    sources, pixels, native_hashes = [], [], set()
    for patch in PATCHES:
        version = active[patch]
        require(re.fullmatch(re.escape(patch) + r"_v[A-Za-z0-9_-]+", version), f"Invalid active version: {version}")
        prep_path = t / "records" / f"{version}.preparation.json"
        prep_sha = checked(prep_path)
        prep = validate_preparation(t, version)
        require(prep.get("logicalPatch") == patch and prep.get("tool") == "image_gen.imagegen" and prep.get("route") == "builtin", "Preparation identity/route mismatch")
        require(prep.get("actualModel") is None and prep.get("actualQuality") is None, "Preparation must not claim actual backend selectors")
        image, native, record = verified_native(t, patch)
        native_sha = checked(native, record.get("sha256"))
        record_path = Path(str(native) + ".generation.json")
        record_sha = checked(record_path)
        require(native_sha not in native_hashes, f"Same native output assigned twice: {version}")
        native_hashes.add(native_sha)
        require(record.get("id") == version and record.get("logicalPatch") == patch and record.get("tile") == tile
                and evidence_path(record.get("file"), local=True) == native.resolve(), "Native record identity mismatch")
        require(record.get("tool") == "image_gen.imagegen" and record.get("route") == "builtin", "Non-builtin native source")
        require([record.get("width"), record.get("height")] == [NATIVE, NATIVE] and record.get("format") == "PNG", "Native recorded dimensions/format changed")
        require(record.get("actualModel") is None and record.get("actualQuality") is None, "Actual builtin model/quality must remain unknown")
        with Image.open(native) as actual:
            actual.load()
            require(actual.mode in ("RGB", "RGBA") and actual.mode == record.get("mode"), f"Native mode differs: {version}")
            require(actual.mode != "RGBA" or actual.getextrema()[3] == (255, 255), f"Native has transparent pixels: {version}")
        evidence = record.get("evidence", {})
        require(evidence_path(evidence.get("preparation"), local=True) == prep_path.resolve(), "Wrong preparation evidence")
        require(evidence.get("preparationSha256") == prep_sha and evidence.get("originalSha256") == native_sha, "Preparation/original hash mismatch")
        receipt_path = evidence_path(evidence.get("receipt"), local=True)
        require(isinstance(evidence.get("receiptSha256"), str), "Missing immutable receipt hash")
        receipt_sha = checked(receipt_path, evidence.get("receiptSha256"))
        receipt = read(receipt_path)
        require(status_ok(receipt.get("status")) and receipt.get("tool", "image_gen.imagegen") == "image_gen.imagegen", "Missing successful builtin receipt")
        require(receipt.get("actualModel") is None and receipt.get("actualQuality") is None, "Receipt claims unverified actual backend values")
        require(not receipt.get("resizedAfterGeneration") and not receipt.get("finalArtUpscaled"), "Receipt reports resized output")
        for key in ("sourceSha256", "outputSha256", "sha256"):
            require(not receipt.get(key) or receipt[key] == native_sha, f"Receipt output hash mismatch: {key}")
        original = evidence_path(evidence.get("originalOutputPath"))
        original_present = original.is_file()
        if original_present:
            checked(original, native_sha)
        request_path = evidence_path(evidence.get("request"), local=True)
        prompt_path = evidence_path(record.get("prompt"), local=True)
        require(request_path == evidence_path(prep.get("request"), local=True)
                and prompt_path == evidence_path(prep.get("prompt"), local=True), "Preparation request/prompt paths differ")
        request_sha = checked(request_path, prep.get("requestSha256"))
        prompt_sha = checked(prompt_path, prep.get("promptSha256"))
        require(evidence.get("requestSha256") == request_sha and record.get("promptSha256") == prompt_sha, "Record request/prompt hashes differ")
        request = read(request_path)
        require(request.get("transparent_background") is False and "num_last_images_to_include" not in request, "Opaque explicit-reference request required")
        require(record.get("references") == prep.get("references") and record.get("anchors") == prep.get("anchors"), "Native preparation references/anchors differ")
        references = prep["references"]
        require(isinstance(references, list) and len(references) == 4, "Three style/layout references plus one anchored target required")
        prepared_contract = prep.get("contractSnapshot", {})
        for reference, field, hash_field in zip(references[:3],
                ("layoutReference", "detailStyleReference", "primaryStyleReference"),
                ("layoutSha256", "detailSha256", "primaryStyleSha256")):
            require(evidence_path(reference.get("path")) == evidence_path(prepared_contract.get(field))
                    and reference.get("sha256") == prepared_contract.get(hash_field), "Submitted style/layout reference differs from preparation contract")
        submitted = record.get("submittedParameters", {})
        require(submitted.get("referenced_image_paths") == request.get("referenced_image_paths")
                and submitted.get("transparent_background") is False
                and submitted.get("model") is None and submitted.get("quality") is None, "Submitted parameters differ")
        for ref in references:
            path = evidence_path(ref.get("path"))
            checked(path, ref.get("sha256"))
            with Image.open(path) as ref_image:
                require(list(ref_image.size) == ref.get("dimensions"), f"Reference dimensions changed: {path}")
            require(bool(ref.get("role")), f"Reference role missing: {path}")
        guide_references, guide_prep = references, prep
        native_edit_evidence = None
        correction = prep.get("nativeCorrectionOf")
        if correction:
            # The input is a prior actual native, not a layout-derived image.
            # Verify its complete recorded generation lineage, then independently
            # replay the original anchored guide instead of inventing a derivative.
            original_target = evidence_path(references[-1]["path"], local=True)
            base_version = correction.get("version")
            require(isinstance(base_version, str) and base_version.startswith(patch + "_v")
                    and base_version != version, "Invalid native edit parent")
            require(original_target == evidence_path(correction.get("path"), local=True)
                    and references[-1]["sha256"] == correction.get("sha256"), "Native edit parent target differs")
            base_native = t / "native" / (base_version + ".png")
            require(base_native.resolve() == original_target, "Native edit parent location differs")
            checked(base_native, correction["sha256"])
            base_record_path = Path(str(base_native) + ".generation.json")
            base_record_sha = checked(base_record_path)
            base_record = read(base_record_path)
            require(base_record.get("sha256") == correction["sha256"]
                    and base_record.get("tile") == tile and base_record.get("logicalPatch") == patch
                    and base_record.get("coordinates") == coordinate(tile, patch)
                    and base_record.get("tool") == "image_gen.imagegen" and base_record.get("route") == "builtin"
                    and base_record.get("actualModel") is None and base_record.get("actualQuality") is None
                    and base_record.get("resizedAfterGeneration") is False
                    and base_record.get("finalArtUpscaled") is False, "Native edit parent generation evidence differs")
            base_evidence = base_record.get("evidence", {})
            base_prep_path = t / "records" / (base_version + ".preparation.json")
            checked(base_prep_path, base_evidence.get("preparationSha256"))
            base_prep = validate_preparation(t, base_version)
            require(not base_prep.get("nativeCorrectionOf"), "Nested native edit not implemented; inspect lineage")
            require(base_prep.get("anchors") == prep["anchors"]
                    and base_prep.get("references", [])[:3] == references[:3]
                    and base_record.get("references") == base_prep.get("references"), "Native edit inherited continuity lineage differs")
            for field in ("request", "prompt"):
                checked(base_prep[field], base_prep[field + "Sha256"])
            base_receipt_path = evidence_path(base_evidence.get("receipt"), local=True)
            checked(base_receipt_path, base_evidence.get("receiptSha256"))
            base_receipt = read(base_receipt_path)
            require(status_ok(base_receipt.get("status"))
                    and base_receipt.get("actualModel") is None
                    and not base_receipt.get("resizedAfterGeneration")
                    and not base_receipt.get("finalArtUpscaled")
                    and base_evidence.get("originalSha256") == correction["sha256"], "Native edit parent receipt is not successful native generation")
            for key in ("sourceSha256", "outputSha256", "sha256"):
                require(not base_receipt.get(key) or base_receipt[key] == correction["sha256"], "Native edit parent receipt hash differs")
            base_original = evidence_path(base_evidence.get("originalOutputPath"))
            if base_original.is_file():
                checked(base_original, correction["sha256"])
            with Image.open(base_native) as parent_image:
                require(parent_image.size == (NATIVE, NATIVE) and parent_image.format == "PNG"
                        and parent_image.mode in ("RGB", "RGBA"), "Native edit parent dimensions differ")
                require(parent_image.mode != "RGBA" or parent_image.getextrema()[3] == (255, 255), "Native edit parent not opaque")
            guide_references, guide_prep = base_prep["references"], base_prep
            native_edit_evidence = {"target": str(base_native), "sha256": correction["sha256"],
                "parentGenerationRecord": str(base_record_path), "parentGenerationRecordSha256": base_record_sha,
                "parentPreparation": str(base_prep_path), "targetIsActualNative": True,
                "originalAnchoredGuideReplayedBelow": True, "nativeInputIsNotClaimedAsDerivedGuide": True}
        target = evidence_path(guide_references[-1]["path"], local=True)
        derivation_path = Path(str(target) + ".derived.json")
        checked(derivation_path)
        derivation = read(derivation_path)
        require(derivation.get("sha256") == guide_references[-1]["sha256"] and derivation.get("anchors") == guide_prep["anchors"]
                and derivation.get("anchorOrder") == ["left", "top"] + (["corner"] if any(a.get("direction") == "corner" for a in guide_prep["anchors"]) else []), "Target derivation differs from preparation")
        layout = evidence_path(derivation.get("layoutSource"), local=True)
        checked(layout, derivation.get("layoutSourceSha256"))
        checked(str(layout) + ".derived.json")
        layout_record = read(str(layout) + ".derived.json")
        require(layout_record.get("sha256") == sha(layout) and layout_record.get("artCanvasBox") == coordinate(tile, patch)["contextBox"], "Layout guide coordinates/hash changed")
        require(layout_record.get("derivedFrom", {}).get("sha256") == references[0]["sha256"], "Layout guide uses another overview")
        with Image.open(layout) as layout_image:
            require(layout_image.size == (NATIVE, NATIVE), "Layout guide dimensions changed")
            replay = layout_image.convert("RGB")
        require(guide_prep["anchors"], "Native preparation has no continuity anchor")
        for anchor in guide_prep["anchors"]:
            path = evidence_path(anchor.get("path"))
            checked(path, anchor.get("sha256"))
            require(anchor.get("resized") is False, "Anchor was resized")
            crop_box, box = anchor.get("sourceCrop"), anchor.get("target")
            require(isinstance(crop_box, list) and isinstance(box, list) and len(crop_box) == len(box) == 4
                    and all(isinstance(v, int) for v in crop_box + box), "Invalid integer anchor rectangles")
            require(0 <= box[0] < box[2] <= NATIVE and 0 <= box[1] < box[3] <= NATIVE
                    and crop_box[2] - crop_box[0] == box[2] - box[0]
                    and crop_box[3] - crop_box[1] == box[3] - box[1], "Anchor is outside target or changes scale")
            with Image.open(path) as anchor_image:
                require(0 <= crop_box[0] < crop_box[2] <= anchor_image.width
                        and 0 <= crop_box[1] < crop_box[3] <= anchor_image.height, "Anchor source crop outside image")
                replay.paste(anchor_image.convert("RGB").crop(crop_box), (box[0], box[1]))
        with Image.open(target) as target_image:
            require(target_image.size == (NATIVE, NATIVE) and np.array_equal(np.asarray(replay), np.asarray(target_image.convert("RGB"))), "Anchor guide cannot be replayed exactly")
        pixels.append(np.asarray(image).copy())
        sources.append({"logicalId": patch, "activeVersion": version, "native": str(native), "nativeSha256": native_sha,
                        "measuredSize": [NATIVE, NATIVE], "generationRecord": str(record_path), "generationRecordSha256": record_sha,
                        "generationRecordSnapshot": record, "preparation": str(prep_path), "preparationSha256": prep_sha,
                        "preparationSnapshot": prep, "receiptSha256": receipt_sha, "receiptSnapshot": receipt,
                        "requestSha256": request_sha, "requestSnapshot": request, "coordinates": coordinate(tile, patch),
                        "anchorGuideReplayVerified": True, "anchorGuideReplayScope": "native edit parent original guide" if correction else "submitted target", "nativeEditInputVerification": native_edit_evidence, "originalFilePresentAndVerified": original_present})

    # Import only the proven numeric join function, never historical preflight/output code.
    algorithm_path = ZONE / "assemble_candidate.py"
    algorithm_sha = checked(algorithm_path)
    checked(Path(__file__))
    spec = importlib.util.spec_from_file_location("_southeast_native_seam_algorithm", algorithm_path)
    require(spec is not None and spec.loader is not None, "Cannot load seam algorithm")
    algorithm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(algorithm)
    require(algorithm.OVERLAP == OVERLAP and algorithm.FEATHER_RADIUS == 2.0, "Seam algorithm parameters changed")
    seam_arrays, seams, strips = {}, [], []
    for row in range(4):
        strip = pixels[row * 4]
        for col in range(1, 4):
            strip, metric = algorithm.append_patch(strip, pixels[row * 4 + col], f"row{row+1:02d}_c{col:02d}_c{col+1:02d}", seam_arrays)
            seams.append(metric)
        require(strip.shape == (NATIVE, CONTEXT, 3), "Assembled row size changed")
        strips.append(strip)
    context = strips[0].transpose(1, 0, 2)
    for row in range(1, 4):
        context, metric = algorithm.append_patch(context, strips[row].transpose(1, 0, 2), f"rows_r{row:02d}_r{row+1:02d}", seam_arrays)
        seams.append(metric)
    context = context.transpose(1, 0, 2)
    require(context.shape == (CONTEXT, CONTEXT, 3), "Assembled context size changed")
    final = Image.fromarray(context[HALO:HALO + TILE_SIZE, HALO:HALO + TILE_SIZE].copy())
    identity = {"tile": tile, "activeMap": active, "inputs": guards, "algorithmSha256": algorithm_sha,
                "overlap": OVERLAP, "featherRadiusPixels": 2.0, "crop": [HALO, HALO, HALO + TILE_SIZE, HALO + TILE_SIZE]}
    version_hash = hashlib.sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    suffix = version_hash[:20]
    candidate_dir, review_dir = t / "candidate", t / "review" / f"assembly-{suffix}"
    manifest_path = candidate_dir / f"{tile}-assembly-{suffix}.json"
    unchanged()
    if manifest_path.exists():
        previous = read(manifest_path)
        require(previous.get("assemblyIdentitySha256") == version_hash, "Assembly filename hash collision")
        for item in [previous["context"], previous["candidate"], previous["seamPathsAndAlpha"], *previous["reviewImages"]]:
            require(Path(item["path"]).is_file() and sha(item["path"]) == item["sha256"], "Existing immutable assembly output changed")
        return {"tile": tile, "status": previous["status"], "alreadyAssembled": True, "candidate": previous["candidate"]["path"],
                "context": previous["context"]["path"], "manifest": str(manifest_path), "formalAccepted": False}
    candidate_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)

    def output_png(path, image):
        if not path.exists():
            write_png_exclusive(path, image)
        with Image.open(path) as saved:
            require(saved.size == image.size and np.array_equal(np.asarray(saved), np.asarray(image)), f"Saved output pixel mismatch: {path}")
        return {"path": str(path), "sha256": sha(path), "size": list(image.size)}

    context_output = output_png(candidate_dir / f"{tile}-context-4326-{suffix}.png", Image.fromarray(context))
    candidate_output = output_png(candidate_dir / f"{tile}-4k-candidate-{suffix}.png", final)
    review_items = []
    rectangles = {}
    for position in (CORE, CORE * 2, CORE * 3):
        rectangles[f"vertical-x{position}-full-height"] = [position - 256, 0, position + 256, TILE_SIZE]
        rectangles[f"horizontal-y{position}-full-width"] = [0, position - 256, TILE_SIZE, position + 256]
    for sy in (CORE, CORE * 2, CORE * 3):
        for sx in (CORE, CORE * 2, CORE * 3):
            rectangles[f"junction-x{sx}-y{sy}"] = [sx - 450, sy - 450, sx + 450, sy + 450]
    rectangles.update({"edge-north": [0, 0, TILE_SIZE, 256], "edge-south": [0, TILE_SIZE - 256, TILE_SIZE, TILE_SIZE],
                       "edge-west": [0, 0, 256, TILE_SIZE], "edge-east": [TILE_SIZE - 256, 0, TILE_SIZE, TILE_SIZE]})
    for label, box in rectangles.items():
        item = output_png(review_dir / f"{label}-100pct.png", final.crop(box))
        item.update(kind="native-pixel-crop", cropBoxIn4096=box, resized=False)
        review_items.append(item)
    overview = output_png(review_dir / "overview-preview-only.png", final.resize((1024, 1024), Image.Resampling.LANCZOS))
    overview.update(kind="downsampled-preview-only", resized=True, deliverable=False)
    review_items.append(overview)
    masks_path = review_dir / "seam-paths-and-alpha.npz"
    if masks_path.exists():
        with np.load(masks_path, allow_pickle=False) as saved_masks:
            require(set(saved_masks.files) == set(seam_arrays) and all(np.array_equal(saved_masks[key], value)
                    for key, value in seam_arrays.items()), "Existing seam arrays differ; preserve them and inspect")
    else:
        with masks_path.open("xb") as stream:
            np.savez_compressed(stream, **seam_arrays)
    masks = {"path": str(masks_path), "sha256": sha(masks_path), "arrayKeys": sorted(seam_arrays)}
    unchanged()
    manifest = {"schemaVersion": 1, "createdAt": now(), "tile": tile, "assemblyIdentitySha256": version_hash,
                "status": "candidate_pending_internal_and_external_visual_review", "formalAccepted": False,
                "internalArtQA": "pending", "externalNeighborSeamQA": "pending", "worldSize": None,
                "clientMappingValidated": False, "capacity5000Validated": False, "activeNativeMapSnapshot": active,
                "contractSnapshot": contract, "verifiedInputHashes": guards, "nativeSources": sources,
                "parameters": {"grid": [4, 4], "order": "row-major", "tileGlobalCoreBox": co["coreBox"],
                    "tileGlobalContextBox": co["contextBox"], "nativePixels": [NATIVE, NATIVE], "corePixels": CORE,
                    "haloPerSide": HALO, "adjacentOverlap": OVERLAP, "assembledSize": [CONTEXT, CONTEXT],
                    "finalCropBox": [HALO, HALO, HALO + TILE_SIZE, HALO + TILE_SIZE],
                    "method": "minimum-error seam; horizontal row joins, then vertical strip joins",
                    "algorithm": {"path": str(algorithm_path), "sha256": algorithm_sha, "function": "append_patch"},
                    "featherRadiusPixels": 2.0, "blendArithmetic": "(left*(255-alpha)+right*alpha+127)//255, uint32",
                    "sourceResampling": False, "sourceUpscaling": False, "registration": False, "colorMatching": False,
                    "globalBlur": False, "sharpening": False, "layoutOnlyPixelsComposited": False},
                "seamMetrics": seams, "seamPathsAndAlpha": masks, "context": context_output,
                "candidate": candidate_output, "reviewImages": review_items,
                "visualReview": {"status": "pending", "fullVerticalSeamBands": 3, "fullHorizontalSeamBands": 3,
                    "junctionCrops": 9, "externalEdgeCrops": 4, "required": "Inspect native seam/edge crops; numeric error and blending do not establish geometry continuity or formal acceptance"}}
    atomic_json(manifest_path, manifest, exclusive=True)
    atomic_json(candidate_dir / "latest-assembly.json", {"schemaVersion": 1, "tile": tile, "status": manifest["status"],
                "manifest": {"path": str(manifest_path), "sha256": sha(manifest_path)}, "assemblyIdentitySha256": version_hash,
                "context": context_output, "candidate": candidate_output, "formalAccepted": False})
    progress(tile, manifest["status"], candidate=candidate_output["path"],
             context=context_output["path"], assemblyManifest=str(manifest_path), complete4kCandidateCount=1,
             missingNativeCount=0, nextStep="Inspect all six full seam bands, nine junctions and four edges at 100%; verify neighboring tile seams before acceptance")
    return {"tile": tile, "status": manifest["status"], "nativeSourceCount": 16, "candidate": candidate_output["path"],
            "context": context_output["path"], "manifest": str(manifest_path), "reviewDirectory": str(review_dir), "formalAccepted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ["init", "assemble"]:
        sub = subs.add_parser(name)
        sub.add_argument("tile")
    sub = subs.add_parser("prepare")
    sub.add_argument("tile")
    sub.add_argument("patch")
    sub.add_argument("local_text", nargs="?", help="Optional UTF-8 local crop instructions, appended to local-content.json entry")
    sub = subs.add_parser("ingest")
    sub.add_argument("tile")
    sub.add_argument("version")
    sub.add_argument("source", help="Actual original PNG output from builtin imagegen")
    sub.add_argument("receipt", help="Truthful JSON receipt: status succeeded_pending_*, tool image_gen.imagegen, actualModel/actualQuality null if unknown")
    args = vars(parser.parse_args())
    command = args.pop("command")
    try:
        print(json.dumps(globals()[command](**args), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, FileNotFoundError) as exc:
        print(json.dumps({"error": str(exc), "writtenCandidate": False, "formalAccepted": False}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
