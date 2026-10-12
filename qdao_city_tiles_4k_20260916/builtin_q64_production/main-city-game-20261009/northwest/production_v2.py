"""Northwest native-art production, with immutable generation evidence.

Run with the bundled Python containing Pillow. This does not invoke ImageGen.
  python production_v2.py --tile r05_c05 init
  python production_v2.py --tile r05_c05 prepare --patch s01_01 --edges north,left
  python production_v2.py --tile r05_c05 record-request --id s01_01 --parameters-file args.json
  python production_v2.py --tile r05_c05 ingest --id s01_01 --source host.png --receipt result.json
  python production_v2.py --tile r05_c05 record-selection --patch s01_01 --id s01_01 --reason "Reviewed native output"
  python production_v2.py --tile r05_c05 progress --write --next-step "Generate s01_02"
  python production_v2.py self-check

prepare creates layout-only guides, never final art. North/left is also accepted
as north,west; diagonal anchors need BOTH adjoining edges enabled. All commands
write only inside this northwest directory. Only progress --write updates the
zone progress file; source workers can ingest concurrently into distinct IDs.

QA is deliberately explicit: qa/acceptance.json must bind a candidate file and
SHA-256 to internalQA={status:"passed",actuallyViewed:true,seamSegments:24,
junctions:9}. Formal acceptance additionally needs formalAccepted:true and
externalQA={status:"passed",actuallyViewed:true,reviewedSides:[...],
worldBoundarySides:[...]}, together covering north,east,south,west. Existing
repair reports do not imply approval. The candidate must use CURRENT selected
source hashes. No command in this script grants QA or formal acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

ZONE = Path(__file__).resolve().parent
PROJECT = ZONE.parent
REPO = next((p for p in ZONE.parents if (p / "config/image-generation.json").is_file()), Path("D:/work/image"))
GRID, CORE, HALO, PATCH, TILE, CANVAS = 4, 1024, 115, 1254, 4096, 65536
TILE_RE = re.compile(r"r(0[1-8])_c(0[1-8])")
PATCH_RE = re.compile(r"s(0[1-4])_(0[1-4])")
ID_RE = re.compile(r"(s0[1-4]_0[1-4])(?:_[A-Za-z0-9][A-Za-z0-9_-]{0,63})?")
SIDES = {"north", "east", "south", "west"}
ALIASES = {"left": "west", "right": "east", "top": "north", "bottom": "south"}


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(part)
    return digest.hexdigest()


def within(path, directory=ZONE):
    value = Path(path).resolve()
    try:
        value.relative_to(Path(directory).resolve())
    except ValueError as exc:
        raise ValueError(f"Path escapes allowed directory: {path}") from exc
    return value


def resolve_ref(value, tile_dir):
    path = Path(value)
    return within(path if path.is_absolute() else tile_dir / path, tile_dir)


def write_bytes(path, data, replace=False):
    path = within(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not replace:
        if path.read_bytes() == data:
            return  # Identical evidence is idempotent, changed evidence never overwrites.
        raise FileExistsError(f"Refusing to overwrite: {path}")
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".writing")
    try:
        temporary.write_bytes(data)
        if replace:
            os.replace(temporary, path)
        else:
            os.rename(temporary, path)  # Windows refuses an existing destination.
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path, value, replace=False):
    write_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"), replace)


def save_png(path, image):
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    write_bytes(path, stream.getvalue())


def load_contract():
    contract = read(PROJECT / "production-contract.json")
    plan = contract["nativePatchPlan"]
    expected = (contract["artCanvasPixels"] == [CANVAS, CANVAS]
                and contract["formalTilePixels"] == [TILE, TILE]
                and [plan["subrows"], plan["subcolumns"], plan["corePixels"],
                     plan["haloPixels"], plan["expectedNativePixels"]]
                == [GRID, GRID, CORE, HALO, PATCH]
                and plan["resizeFinalArtAllowed"] is False
                and contract["builtinOnly"] is True)
    if not expected:
        raise ValueError("Contract geometry or route changed; inspect before production")
    zone = next(z for z in contract["zones"] if z["id"] == "northwest")
    if zone["rows"] != [1, 8] or zone["columns"] != [1, 8] or zone["tileCount"] != 64:
        raise ValueError("Northwest ownership changed")
    return contract


def tile_box(tile):
    match = TILE_RE.fullmatch(tile)
    if not match:
        raise ValueError("Only northwest tile names r01_c01 through r08_c08 are accepted")
    row, column = map(int, match.groups())
    x, y = (column - 1) * TILE, (row - 1) * TILE
    return [x, y, x + TILE, y + TILE]


def patch_id(value):
    if not PATCH_RE.fullmatch(value):
        raise ValueError("Patch must be s01_01 through s04_04")
    return value


def logical_id(value):
    match = ID_RE.fullmatch(value)
    if not match:
        raise ValueError("ID must be a logical patch with an optional alphanumeric revision suffix")
    return match.group(1)


def coordinates(tile, external_neighbor=False):
    if external_neighbor:
        match = re.fullmatch(r"r(0[1-9]|1[0-6])_c(0[1-9]|1[0-6])", tile)
        if not match:
            raise ValueError("Neighbor lies outside the contracted 16 by 16 city")
        row, column = map(int, match.groups())
        x, y = (column - 1) * TILE, (row - 1) * TILE
        box = [x, y, x + TILE, y + TILE]
    else:
        box = tile_box(tile)
    entries = []
    for row in range(1, GRID + 1):
        for column in range(1, GRID + 1):
            x, y = box[0] + (column - 1) * CORE, box[1] + (row - 1) * CORE
            entries.append({"id": f"s{row:02d}_{column:02d}",
                            "worldBoxWithHalo": [x-HALO, y-HALO, x+CORE+HALO, y+CORE+HALO],
                            "coreWorldBox": [x, y, x+CORE, y+CORE],
                            "coreCrop": [HALO, HALO, HALO+CORE, HALO+CORE]})
    return {"tile": tile, "tileWorldBox": box, "canvas": [CANVAS, CANVAS], "patches": entries}


def ensure_coordinates(tile, create=False):
    directory = within(ZONE / tile)
    expected = coordinates(tile)
    path = directory / "coordinates.json"
    if path.exists():
        actual = read(path)
        for key, value in expected.items():
            if actual.get(key) != value:
                raise ValueError(f"Existing coordinates disagree: {path}: {key}")
    elif create:
        write_json(path, expected)
    else:
        raise FileNotFoundError(f"Run init first: {path}")
    return directory, expected


def init_tile(tile):
    contract = load_contract()
    directory, coords = ensure_coordinates(tile, create=True)
    for name in ("layout-only", "native", "prompts", "receipts", "qa", "candidate"):
        (directory / name).mkdir(parents=True, exist_ok=True)
    source = Path(contract["layoutReference"])
    source_hash = sha(source)
    if source_hash != contract["layoutSha256"]:
        raise ValueError("Approved layout image hash differs from production contract")
    with Image.open(source) as opened:
        layout = opened.convert("RGB")
    for entry in coords["patches"]:
        output = directory / "layout-only" / (entry["id"] + ".layout-only.png")
        if output.exists():
            derivation = output.with_suffix(".png.derivation.json")
            if not derivation.is_file():
                raise ValueError(f"Existing guide has no derivation: {output}")
            record = read(derivation)
            if record.get("worldBox") != entry["worldBoxWithHalo"] or record.get("derivedFrom", {}).get("sha256") != source_hash:
                raise ValueError(f"Existing layout guide provenance differs: {output}")
            continue
        world = entry["worldBoxWithHalo"]
        source_box = [world[0]*layout.width/CANVAS, world[1]*layout.height/CANVAS,
                      world[2]*layout.width/CANVAS, world[3]*layout.height/CANVAS]
        guide = layout.transform((PATCH, PATCH), Image.Transform.EXTENT,
                                 source_box, Image.Resampling.BICUBIC)
        save_png(output, guide)
        write_json(output.with_suffix(".png.derivation.json"), {
            "file": str(output), "role": "layout-only; not game artwork or native detail",
            "derivedFrom": {"file": str(source), "sha256": source_hash, "nativeSize": list(layout.size)},
            "worldBox": world, "operation": "bicubic enlargement only for geometry reference",
            "size": [PATCH, PATCH], "gameArt": False})
    # Keep existing v1 guides; new files have unique v2 names and provenance.
    for name, size, box in [
        ("tile-v2.layout-only.png", (1024, 1024), coords["tileWorldBox"]),
    ]:
        output = directory / "layout-only" / name
        if not output.exists():
            b = [box[0]*layout.width/CANVAS, box[1]*layout.height/CANVAS,
                 box[2]*layout.width/CANVAS, box[3]*layout.height/CANVAS]
            save_png(output, layout.transform(size, Image.Transform.EXTENT, b, Image.Resampling.BICUBIC))
            write_json(output.with_suffix(".png.derivation.json"), {
                "file": str(output), "role": "layout-only; not game artwork", "gameArt": False,
                "derivedFrom": {"file": str(source), "sha256": source_hash},
                "worldBox": box, "size": list(size), "operation": "layout-only scaled crop"})
    return {"tile": tile, "coordinates": str(directory / "coordinates.json"),
            "patches": GRID*GRID, "gameArtGenerated": 0}


def selected_path(tile_dir, pid, selection=None):
    selection = read(tile_dir / "selection.json") if selection is None and (tile_dir / "selection.json").exists() else (selection or {})
    value = selection.get(pid, str(tile_dir / "native" / (pid + ".png")))
    if not isinstance(value, str):
        raise ValueError(f"Selection value must be a file path: {tile_dir.name}/{pid}")
    return resolve_ref(value, tile_dir)


def validate_native(path, tile_dir, pid):
    """Mechanical usability only; no aesthetic or seam approval is inferred."""
    path = within(path, tile_dir)
    record_path = path.with_suffix(".png.generation.json")
    record = read(record_path)
    if resolve_ref(record["file"], tile_dir) != path:
        raise ValueError("Generation record points to a different image")
    native_hash = sha(path)
    if record.get("sha256") != native_hash:
        raise ValueError("Native image hash differs from generation record")
    if record.get("route") not in {"builtin", "builtin_image_gen"}:
        raise ValueError("Source does not record the built-in route")
    if record.get("resizedAfterGeneration") or record.get("finalArtUpscaled"):
        raise ValueError("Upscaled/resized source is not usable native detail")
    if logical_id(path.stem) != pid:
        raise ValueError("Selected image does not belong to this logical patch")
    with Image.open(path) as image:
        if image.format != "PNG" or image.size != (PATCH, PATCH):
            raise ValueError(f"Expected native {PATCH}x{PATCH} PNG")
        if [record.get("width"), record.get("height")] != list(image.size):
            raise ValueError("Recorded native dimensions disagree")
        if image.convert("RGBA").getchannel("A").getextrema() != (255, 255):
            raise ValueError("Ground source contains transparent pixels")
    prompt = resolve_ref(record.get("prompt", f"prompts/{path.stem}.txt"), tile_dir)
    evidence = record.get("evidence", {})
    request = resolve_ref(evidence.get("request", f"receipts/{path.stem}.request.json"), tile_dir)
    receipt = resolve_ref(evidence.get("receipt", f"receipts/{path.stem}.result.json"), tile_dir)
    if not prompt.read_text(encoding="utf-8-sig").strip():
        raise ValueError("Native source prompt is empty")
    read(request)
    read(receipt)
    for label, item in (("prompt", prompt), ("request", request), ("receipt", receipt)):
        expected = evidence.get(label + "Sha256")
        if expected and sha(item) != expected:
            raise ValueError(f"Immutable evidence hash differs: {label}")
    return {"file": str(path), "sha256": native_hash, "generationRecord": str(record_path),
            "prompt": str(prompt), "request": str(request), "receipt": str(receipt)}


def parse_edges(value):
    if value == "all":
        return set(SIDES)
    if value == "none":
        return set()
    edges = {ALIASES.get(x.strip().lower(), x.strip().lower()) for x in value.split(",")}
    if not edges or not edges <= SIDES:
        raise ValueError("Edges must be all, none, or north,east,south,west (left/right aliases accepted)")
    return edges


def overlap(first, second):
    result = [max(first[0], second[0]), max(first[1], second[1]),
              min(first[2], second[2]), min(first[3], second[3])]
    return result if result[0] < result[2] and result[1] < result[3] else None


def relative_sides(target, neighbor):
    sides = set()
    if neighbor[0] < target[0]: sides.add("west")
    if neighbor[0] > target[0]: sides.add("east")
    if neighbor[1] < target[1]: sides.add("north")
    if neighbor[1] > target[1]: sides.add("south")
    return sides


def prepare(tile, pid, version, edges):
    contract = load_contract()
    directory, coords = ensure_coordinates(tile)
    patch_id(pid)
    output_id = pid + ("_" + version if version else "")
    logical_id(output_id)
    enabled = parse_edges(edges)
    target = next(p for p in coords["patches"] if p["id"] == pid)["worldBoxWithHalo"]
    source = directory / "layout-only" / (pid + ".layout-only.png")
    with Image.open(source) as opened:
        base = opened.convert("RGB")
    if base.size != (PATCH, PATCH):
        raise ValueError("Layout guide has unexpected dimensions")
    anchors, missing = [], []
    # Geometry is checked before images are loaded. Selected revisions without a
    # default file are still eligible, including patches in adjacent tile folders.
    for nr in range(1, 17):
        for nc in range(1, 17):
            neighbor_tile = f"r{nr:02d}_c{nc:02d}"
            neighbor_coords = coordinates(neighbor_tile, external_neighbor=True)
            tile_context = neighbor_coords["tileWorldBox"]
            if overlap(target, [tile_context[0]-HALO, tile_context[1]-HALO,
                                tile_context[2]+HALO, tile_context[3]+HALO]) is None:
                continue
            owner = next(z for z in contract["zones"]
                         if z["rows"][0] <= nr <= z["rows"][1]
                         and z["columns"][0] <= nc <= z["columns"][1])
            neighbor_dir = within(PROJECT / owner["id"] / neighbor_tile, PROJECT)
            selection_file = neighbor_dir / "selection.json"
            selection = read(selection_file) if selection_file.exists() else {}
            for entry in neighbor_coords["patches"]:
                if neighbor_tile == tile and entry["id"] == pid:
                    continue  # A repair never uses its own previous version as an anchor.
                nb = entry["worldBoxWithHalo"]
                intersection = overlap(target, nb)
                sides = relative_sides(target, nb)
                if intersection is None or not sides <= enabled:
                    continue
                path = selected_path(neighbor_dir, entry["id"], selection)
                if not path.exists():
                    missing.append({"tile": neighbor_tile, "patch": entry["id"], "sides": sorted(sides)})
                    continue
                actual_coords = read(neighbor_dir / "coordinates.json")
                if any(actual_coords.get(key) != value for key, value in neighbor_coords.items()):
                    raise ValueError(f"Neighbor coordinates disagree: {neighbor_dir}")
                ref = validate_native(path, neighbor_dir, entry["id"])
                ref.update({"zone": owner["id"], "tile": neighbor_tile, "patch": entry["id"], "sides": sorted(sides),
                            "worldBox": nb, "overlapWorldBox": intersection,
                            "sourceBox": [intersection[0]-nb[0], intersection[1]-nb[1],
                                          intersection[2]-nb[0], intersection[3]-nb[1]],
                            "targetBox": [intersection[0]-target[0], intersection[1]-target[1],
                                          intersection[2]-target[0], intersection[3]-target[1]]})
                anchors.append(ref)
    # Corner-only anchors first; cardinal bands last. Order is recorded, not hidden.
    anchors.sort(key=lambda item: (-len(item["sides"]), item["tile"], item["patch"]))
    covered = Image.new("1", (PATCH, PATCH), 0)
    draw = ImageDraw.Draw(covered)
    repeated_pixels = 0
    for order, ref in enumerate(anchors):
        box = ref["targetBox"]
        repeated_pixels += sum(covered.crop(box).getdata())
        with Image.open(ref["file"]) as opened:
            pixels = opened.convert("RGB").crop(ref["sourceBox"])
        base.paste(pixels, (box[0], box[1]))
        draw.rectangle((box[0], box[1], box[2]-1, box[3]-1), fill=1)
        ref["pasteOrder"] = order
        ref["sourceResampled"] = False
    guide = directory / "layout-only" / (output_id + ".continuation-guide.png")
    save_png(guide, base)
    record = {"file": str(guide), "sha256": sha(guide), "createdAt": now(),
              "role": "mixed native overlap and layout-only guide; never final game artwork",
              "gameArt": False, "worldBox": target, "enabledEdges": sorted(enabled),
              "selfAnchorExcluded": True, "nativeNeighbors": anchors,
              "missingNeighborSlots": missing, "repeatedlyCoveredGuidePixels": repeated_pixels,
              "cornerPolicy": "both adjoining edges must be enabled; corners first, cardinal anchors last",
              "layoutSource": str(source), "layoutSourceSha256": sha(source),
              "operation": "exact unscaled pasting at global coordinates; layout enlargement is guide only"}
    write_json(guide.with_suffix(".png.derivation.json"), record)
    return {"guide": str(guide), "derivation": str(guide.with_suffix(".png.derivation.json")),
            "nativeAnchors": len(anchors), "missingNeighborSlots": missing,
            "worldBox": target, "references": anchors}


def record_request(tile, identifier, parameters_file, roles_file=None):
    directory, coords = ensure_coordinates(tile)
    pid = logical_id(identifier)
    parameters = read(parameters_file)
    if not isinstance(parameters.get("prompt"), str) or not parameters["prompt"].strip():
        raise ValueError("Parameters need the exact nonempty tool prompt")
    if "num_last_images_to_include" in parameters:
        raise ValueError("Use explicit local reference paths for reproducible production")
    references = parameters.get("referenced_image_paths", [])
    if not isinstance(references, list) or not all(isinstance(v, str) for v in references):
        raise ValueError("referenced_image_paths must be a list of actual local paths")
    roles = read(roles_file) if roles_file else {}
    if not isinstance(roles, dict):
        raise ValueError("Roles JSON must map reference path to role")
    refs = [{"file": str(Path(value).resolve()), "sha256": sha(value),
             "role": roles.get(value, "submitted image reference")} for value in references]
    patch = next(p for p in coords["patches"] if p["id"] == pid)
    prompt = directory / "prompts" / (identifier + ".txt")
    request = directory / "receipts" / (identifier + ".request.json")
    if prompt.exists() or request.exists():
        raise FileExistsError("Generation ID already has evidence; use a new revision ID")
    write_bytes(prompt, parameters["prompt"].encode("utf-8"))
    write_json(request, {"schemaVersion": 2, "recordedAt": now(), "tile": tile,
                         "id": identifier, "logicalPatch": pid, "parameters": parameters,
                         "references": refs,
                         "configurationSnapshot": (read(REPO / "config/image-generation.json")
                             if (REPO / "config/image-generation.json").is_file() else
                             {"available": False, "path": str(REPO / "config/image-generation.json"),
                              "note": "Shared configuration absent at request time; exact builtin tool arguments remain recorded. No backend model or quality inferred."}),
                         "worldBoxWithHalo": patch["worldBoxWithHalo"],
                         "coreWorldBox": patch["coreWorldBox"], "promptSha256": sha(prompt),
                         "actualModel": None, "actualQuality": None,
                         "evidenceMeaning": "Exact planned submission; this is not proof of tool completion"})
    return {"prompt": str(prompt), "request": str(request), "references": refs}


def ingest(tile, identifier, source, receipt):
    directory, coords = ensure_coordinates(tile)
    pid = logical_id(identifier)
    destination = directory / "native" / (identifier + ".png")
    record_file = destination.with_suffix(".png.generation.json")
    if destination.exists() or record_file.exists():
        raise FileExistsError("Never overwrite native generation; choose another ID")
    request_path = directory / "receipts" / (identifier + ".request.json")
    prompt = directory / "prompts" / (identifier + ".txt")
    request = read(request_path)
    if request.get("promptSha256") and sha(prompt) != request["promptSha256"]:
        raise ValueError("Prompt changed since request recording")
    receipt_data = read(receipt)
    source = Path(source).resolve()
    with Image.open(source) as image:
        image.load()
        size, fmt = image.size, image.format
        png_info = {k: str(v)[:1000] for k, v in image.info.items()}
        opaque = image.convert("RGBA").getchannel("A").getextrema() == (255, 255)
    if fmt != "PNG":
        raise ValueError("Keep the native PNG; this script never re-encodes generated output")
    patch = next(p for p in coords["patches"] if p["id"] == pid)
    result = directory / "receipts" / (identifier + ".result.json")
    if result.exists():
        raise FileExistsError("Result already exists for this ID")
    write_bytes(destination, source.read_bytes())  # Exact generated file, no conversion.
    write_json(result, receipt_data)
    refs = request.get("references", [])
    valid_size = size == (PATCH, PATCH)
    record = {"schemaVersion": 2, "file": str(destination), "sha256": sha(destination),
              "generatedAt": now(), "tile": tile, "logicalPatch": pid, "generationId": identifier,
              "width": size[0], "height": size[1], "format": fmt,
              "tool": "image_gen.imagegen", "route": "builtin",
              "configSnapshot": (request["configurationSnapshot"] if "configurationSnapshot" in request
                                 else read(REPO / "config/image-generation.json")),
              "submittedParameters": {"model": None, "quality": None, **request["parameters"]},
              "actualModel": None, "actualQuality": None,
              "unverifiedReason": "Built-in tool exposes no model/quality selectors and discloses no verified backend values.",
              "prompt": str(prompt), "references": refs,
              "evidence": {"request": str(request_path), "requestSha256": sha(request_path),
                           "promptSha256": sha(prompt), "receipt": str(result), "receiptSha256": sha(result),
                           "pngInfo": png_info, "hostOutputPath": str(source)},
              "worldBoxWithHalo": patch["worldBoxWithHalo"], "coreWorldBox": patch["coreWorldBox"],
              "coreCrop": patch["coreCrop"], "nativeDimensionsMatchPlan": valid_size,
              "opaque": opaque, "resizedAfterGeneration": False, "finalArtUpscaled": False,
              "status": "native_candidate_pending_seam_review" if valid_size and opaque else "invalid_native_geometry_or_alpha"}
    write_json(record_file, record)
    return {"file": str(destination), "size": list(size), "sha256": record["sha256"],
            "mechanicallyEligible": valid_size and opaque, "selectedExplicitly": False,
            "formalAccepted": False, "progressUpdated": False}


def record_selection(tile, pid, identifier, reason, review_file=None):
    directory, _ = ensure_coordinates(tile)
    patch_id(pid)
    if logical_id(identifier) != pid:
        raise ValueError("Revision belongs to another patch")
    source = directory / "native" / (identifier + ".png")
    validation = validate_native(source, directory, pid)
    review = None
    if review_file:
        review_path = within(review_file, directory)
        review = {"file": str(review_path), "sha256": sha(review_path)}
    lock = directory / ".selection-v2.lock"
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError("Another selection writer is active; retry after it completes") from exc
    try:
        os.close(descriptor)
        path = directory / "selection.json"
        selection = read(path) if path.exists() else {}
        previous = str(selected_path(directory, pid, selection))
        journal = {"createdAt": now(), "tile": tile, "logicalPatch": pid,
                   "previous": previous, "selected": validation, "reason": reason,
                   "review": review, "grantsInternalQA": False, "grantsFormalAcceptance": False}
        journal_path = directory / "receipts" / "selections" / (identifier + "-" + uuid.uuid4().hex + ".json")
        write_json(journal_path, journal)
        selection[pid] = str(source)
        write_json(path, selection, replace=True)
    finally:
        lock.unlink()
    return {"selection": str(path), "journal": str(journal_path), "selected": str(source),
            "progressUpdated": False}


def candidate_info(path, tile_dir, usable):
    record = read(path)
    output = record.get("output", {})
    candidate = resolve_ref(output.get("file", ""), tile_dir)
    if (record.get("tile") != tile_dir.name or record.get("missingNativePatches")
            or len(record.get("nativeSources", [])) != GRID*GRID):
        return None
    if record.get("sourceResampled") or record.get("sourceUpscaled"):
        return None
    if not candidate.is_file() or sha(candidate) != output.get("sha256"):
        return None
    with Image.open(candidate) as image:
        if image.format != "PNG" or image.size != (TILE, TILE) or image.convert("RGBA").getchannel("A").getextrema() != (255, 255):
            return None
    sources = {s["id"]: s["sha256"] for s in record["nativeSources"]}
    if len(sources) != GRID*GRID:
        return None
    current = len(usable) == GRID*GRID and sources == {pid: ref["sha256"] for pid, ref in usable.items()}
    return {"file": str(candidate), "sha256": output["sha256"], "manifest": str(path),
            "createdAt": record.get("createdAtUtc", ""), "usesCurrentSelection": current}


def qa_verdict(tile_dir, candidates):
    path = tile_dir / "qa" / "acceptance.json"
    if not path.exists():
        return {"internalPassed": False, "formalPassed": False, "status": "no_explicit_current_acceptance"}
    evidence = read(path)
    ref = evidence.get("candidate", {})
    if not isinstance(ref, dict) or not ref.get("file"):
        return {"internalPassed": False, "formalPassed": False, "status": "acceptance_missing_candidate_binding"}
    candidate_path = resolve_ref(ref["file"], tile_dir)
    matches = [c for c in candidates if c["usesCurrentSelection"] and Path(c["file"]) == candidate_path and c["sha256"] == ref.get("sha256")]
    if not matches:
        return {"internalPassed": False, "formalPassed": False, "status": "acceptance_stale_or_candidate_invalid"}
    internal = evidence.get("internalQA", {})
    internal_ok = (internal.get("status") == "passed" and internal.get("actuallyViewed") is True
                   and internal.get("seamSegments") == 24 and internal.get("junctions") == 9)
    external = evidence.get("externalQA", {})
    reviewed = set(external.get("reviewedSides", []))
    boundaries = set(external.get("worldBoundarySides", []))
    box = tile_box(tile_dir.name)
    actual_boundaries = set()
    if box[0] == 0: actual_boundaries.add("west")
    if box[1] == 0: actual_boundaries.add("north")
    if box[2] == CANVAS: actual_boundaries.add("east")
    if box[3] == CANVAS: actual_boundaries.add("south")
    external_ok = (external.get("status") == "passed" and external.get("actuallyViewed") is True
                   and boundaries <= actual_boundaries and reviewed | boundaries == SIDES)
    return {"internalPassed": internal_ok,
            "formalPassed": internal_ok and external_ok and evidence.get("formalAccepted") is True,
            "status": "explicit_current_evidence", "evidence": str(path), "sha256": sha(path)}


def aggregate_progress(active_tile=None, next_step=None):
    load_contract()
    generated, records, record_errors, available_history = 0, [], [], 0
    for path in sorted(ZONE.glob("r??_c??/native/*.png.generation.json")):
        if not TILE_RE.fullmatch(path.parent.parent.name):
            continue
        try:
            record = read(path)
            # Generation count is historical and includes revisions even after authorized cleanup.
            if record.get("route") not in {"builtin", "builtin_image_gen"} or not record.get("sha256"):
                raise ValueError("Not a completed built-in generation record")
            generated += 1
            records.append(str(path))
            image_path = resolve_ref(record["file"], path.parent.parent)
            available_history += int(image_path.is_file())
        except (OSError, ValueError, KeyError, TypeError) as exc:
            record_errors.append({"file": str(path), "error": str(exc)})
    tiles = []
    native_files = []
    for row in range(1, 9):
        for column in range(1, 9):
            tile = f"r{row:02d}_c{column:02d}"
            directory = ZONE / tile
            entry = {"tile": tile, "selectedAvailable": 0, "selectedUsable": 0, "missingNativePatches": [],
                     "invalidSelected": [], "completeCandidate": False, "currentCompleteCandidate": False,
                     "internalQAPassed": False, "formalAccepted": False}
            selection_path = directory / "selection.json"
            try:
                selection = read(selection_path) if selection_path.exists() else {}
                if (directory / "coordinates.json").exists():
                    ensure_coordinates(tile)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                selection = {}
                entry["invalidSelected"].append({"error": str(exc), "kind": "selection_or_coordinates"})
            usable = {}
            for patch in coordinates(tile)["patches"]:
                pid = patch["id"]
                try:
                    path = selected_path(directory, pid, selection)
                    if path.is_file():
                        entry["selectedAvailable"] += 1
                        native_files.append(str(path))
                        if entry["invalidSelected"] and entry["invalidSelected"][0].get("kind") == "selection_or_coordinates":
                            raise ValueError("Tile selection/coordinates need repair")
                        ensure_coordinates(tile)
                        usable[pid] = validate_native(path, directory, pid)
                    else:
                        entry["missingNativePatches"].append(pid)
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    entry["missingNativePatches"].append(pid)
                    entry["invalidSelected"].append({"patch": pid, "error": str(exc)})
            entry["selectedUsable"] = len(usable)
            candidates = []
            candidate_errors = []
            for manifest in sorted((directory / "candidate").glob("*-candidate-*.assembly.json")):
                try:
                    info = candidate_info(manifest, directory, usable)
                    if info:
                        candidates.append(info)
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    candidate_errors.append({"file": str(manifest), "error": str(exc)})
            entry["completeCandidate"] = bool(candidates)
            entry["currentCompleteCandidate"] = any(c["usesCurrentSelection"] for c in candidates)
            if candidates:
                ordered = sorted(candidates, key=lambda c: (c["usesCurrentSelection"], c["createdAt"]))
                entry["latestCandidate"] = ordered[-1]["file"]
                entry["candidateVariants"] = len(candidates)
            if candidate_errors:
                entry["candidateErrors"] = candidate_errors
            try:
                qa = qa_verdict(directory, candidates)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                qa = {"internalPassed": False, "formalPassed": False, "status": "invalid_acceptance", "error": str(exc)}
            entry["internalQAPassed"] = qa["internalPassed"]
            entry["formalAccepted"] = qa["formalPassed"]
            entry["qa"] = qa
            tiles.append(entry)
    old = read(ZONE / "progress.json") if (ZONE / "progress.json").exists() else {}
    candidate_count = sum(t["completeCandidate"] for t in tiles)
    current_count = sum(t["currentCompleteCandidate"] for t in tiles)
    formal = sum(t["formalAccepted"] for t in tiles)
    selected_available = sum(t["selectedAvailable"] for t in tiles)
    selected_usable = sum(t["selectedUsable"] for t in tiles)
    selected_tile = active_tile or old.get("activeTile", "r05_c04")
    tile_box(selected_tile)
    active = next(t for t in tiles if t["tile"] == selected_tile)
    result = {"schemaVersion": 2, "zone": "northwest", "updatedAt": now(),
              "status": "complete" if formal == 64 else "in_progress", "tileRows": [1, 8], "tileColumns": [1, 8],
              "tileCount": 64, "expectedNativeCoreCount": 1024, "firstTile": "r05_c04", "activeTile": selected_tile,
              "generatedNativeCount": generated, "generatedNativeCountIncludesRevisions": True,
              "historicalNativeFilesStillPresent": available_history, "generationRecords": records,
              "generationRecordErrors": record_errors, "selectedNativeCount": selected_available,
              "selectedAvailableNativeCount": selected_available, "selectedUsableNativeCount": selected_usable,
              "selectedSourceProvenanceValidatedCount": selected_usable,
              "usableDefinition": "Correct original PNG dimensions, opacity, hash and own prompt/request/receipt; NOT visual seam acceptance",
              "missingNativePatchCount": 1024-selected_usable,
              "complete4kCandidateCount": candidate_count, "currentComplete4kCandidateCount": current_count,
              "candidateCountMeansPixelCoverageNotAcceptance": True,
              "internalQAPassedCount": sum(t["internalQAPassed"] for t in tiles), "formalAcceptedCount": formal,
              "remainingTileCountWithoutCompleteCandidate": 64-candidate_count,
              "remainingTileCountWithoutCurrentCompleteCandidate": 64-current_count,
              "remainingTileCountWithoutFormalAcceptance": 64-formal,
              "remainingTileCountWithoutFullUsableSourceCoverage": sum(t["selectedUsable"] != 16 for t in tiles),
              "nativeFiles": native_files, "tiles": tiles,
              "nextStep": next_step if next_step is not None else old.get("nextStep", "Continue native generation and explicit seam review"),
              "clientMappingValidated": False, "capacity5000Validated": False,
              "artCanvasPixels": [CANVAS, CANVAS], "nativeCorePixels": CORE, "haloPixels": HALO}
    if active.get("latestCandidate"):
        result["latestCandidate"] = active["latestCandidate"]
    return result


def self_check():
    expected = coordinates("r05_c04")
    assert expected["tileWorldBox"] == [12288, 16384, 16384, 20480]
    assert expected["patches"][0]["worldBoxWithHalo"] == [12173, 16269, 13427, 17523]
    east = coordinates("r05_c05")["patches"][0]["worldBoxWithHalo"]
    west = expected["patches"][3]["worldBoxWithHalo"]
    assert overlap(east, west) == [16269, 16269, 16499, 17523]
    assert relative_sides(east, west) == {"west"}
    assert coordinates("r01_c01")["patches"][0]["worldBoxWithHalo"] == [-115, -115, 1139, 1139]
    assert coordinates("r08_c08")["tileWorldBox"] == [28672, 28672, 32768, 32768]
    assert coordinates("r08_c09", external_neighbor=True)["tileWorldBox"] == [32768, 28672, 36864, 32768]
    assert parse_edges("north,left") == {"north", "west"}
    assert relative_sides([100, 100, 1354, 1354], [0, 0, 1254, 1254]) == {"north", "west"}
    assert logical_id("s04_03_fix01") == "s04_03"
    # Exact native crop-paste proof, entirely in memory, no production image writes.
    native = Image.new("RGB", (PATCH, PATCH), (12, 34, 56))
    target = Image.new("RGB", (PATCH, PATCH), (0, 0, 0))
    target.paste(native.crop((1024, 0, 1254, 1254)), (0, 0))
    assert target.getpixel((229, 1253)) == (12, 34, 56)
    assert target.getpixel((230, 1253)) == (0, 0, 0)
    for invalid in ("r00_c01", "r09_c01", "../r01_c01", "r01_c16"):
        try:
            tile_box(invalid)
        except ValueError:
            continue
        raise AssertionError("Out-of-zone tile accepted")
    return {"selfCheck": "passed", "writes": 0, "productionImagesRead": 0,
            "checks": ["global tile coordinates", "cross-tile 230px overlap", "world-edge halo",
                       "NW ownership bounds", "direction filtering", "revision IDs", "exact in-memory crop/paste"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tile", help="Northwest tile r01_c01 through r08_c08; required except progress/self-check")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Create immutable coordinates and layout-only guides for one tile")
    prepare_parser = sub.add_parser("prepare", help="Guide using selected native overlaps at exact world coordinates")
    prepare_parser.add_argument("--patch", required=True)
    prepare_parser.add_argument("--version", default="", help="Unique repair suffix, e.g. fix03; avoids old guide overwrite")
    prepare_parser.add_argument("--edges", default="all", help="all, none, or north,left etc.; diagonals require both sides")
    request_parser = sub.add_parser("record-request", help="Record exact intended ImageGen parameters before submission")
    request_parser.add_argument("--id", required=True)
    request_parser.add_argument("--parameters-file", required=True, help="JSON containing exact ImageGen tool arguments")
    request_parser.add_argument("--roles-file", help="Optional JSON mapping submitted reference paths to roles")
    ingest_parser = sub.add_parser("ingest", help="Copy native tool output unchanged and attach its immutable evidence")
    ingest_parser.add_argument("--id", required=True)
    ingest_parser.add_argument("--source", required=True)
    ingest_parser.add_argument("--receipt", required=True)
    selection_parser = sub.add_parser("record-selection", help="Select a validated version; does not grant visual QA")
    selection_parser.add_argument("--patch", required=True)
    selection_parser.add_argument("--id", required=True)
    selection_parser.add_argument("--reason", required=True)
    selection_parser.add_argument("--review-file")
    progress_parser = sub.add_parser("progress", help="Read-only by default; --write atomically refreshes progress.json")
    progress_parser.add_argument("--write", action="store_true")
    progress_parser.add_argument("--next-step")
    sub.add_parser("self-check", help="Pure in-memory geometry/ownership checks; writes no files")
    args = parser.parse_args()
    if args.command == "self-check":
        result = self_check()
    else:
        load_contract()
        if args.command not in {"progress"} and not args.tile:
            parser.error("--tile is required for this command")
        if args.command == "init":
            result = init_tile(args.tile)
        elif args.command == "prepare":
            result = prepare(args.tile, args.patch, args.version, args.edges)
        elif args.command == "record-request":
            result = record_request(args.tile, args.id, args.parameters_file, args.roles_file)
        elif args.command == "ingest":
            result = ingest(args.tile, args.id, args.source, args.receipt)
        elif args.command == "record-selection":
            result = record_selection(args.tile, args.patch, args.id, args.reason, args.review_file)
        elif args.command == "progress":
            result = aggregate_progress(args.tile, args.next_step)
            if args.write:
                write_json(ZONE / "progress.json", result, replace=True)
            result["progressWritten"] = args.write
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc), "type": type(exc).__name__}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)

