"""Batch-local mechanical prepare/ingest/assemble. Never generates art or calls APIs.

Use Python -B. All outputs are append-only and contained by this batch directory.
Actual image_gen tool calls remain root's job; precall saves fresh allocation evidence.
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import importlib.util
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

BATCH = Path(__file__).resolve().parent.parent
PRODUCTION = BATCH.parent.parent
REPO = PRODUCTION.parent.parent
CONTRACT = PRODUCTION / "island-game-20261009/production-contract.json"
SPLIT = REPO / "docs/MAP_PARALLEL_SPLIT_20261013.json"
RULES = REPO / "AGENTS.md"
NORTHWEST = PRODUCTION / "island-game-20261009/northwest"
WORKER = "01a1338b-b20b-7ad2-861f-3b771a61e085"
TILES = {f"r{r:02d}_c{c:02d}" for r in (1, 2) for c in (2, 3, 4)}
SIZE, CORE, HALO, OVERLAP, TILE = 1254, 1024, 115, 230, 4096
STEM_RE = re.compile(r"(r\d{2}_c\d{2})_s(\d{2})_(\d{2})_a(\d{2,})")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def safe_path(value, base=BATCH):
    p = Path(value)
    p = (p if p.is_absolute() else base / p).resolve()
    require(not any(s.lower() == ".git" for s in p.parts), "Git paths are forbidden")
    return p


def output_path(value):
    p = safe_path(value)
    require(p.is_relative_to(BATCH), f"Output must stay inside this batch: {p}")
    return p


def sha(path):
    h = hashlib.sha256()
    with safe_path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def file_record(path, role=None):
    p = safe_path(path)
    require(p.is_file(), f"Required file missing: {p}")
    result = {"path": p.as_posix(), "sha256": sha(p), "bytes": p.stat().st_size}
    if role:
        result["role"] = role
    return result


def read_json(path):
    return json.loads(safe_path(path).read_text(encoding="utf-8-sig"))


def save_json(path, value):
    p = output_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return file_record(p)


def save_bytes(path, data):
    p = output_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("xb") as f:
        f.write(data)
    return file_record(p)


def save_image(path, image):
    p = output_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("xb") as f:
        image.save(f, format="PNG")
    return {**file_record(p), "dimensions": list(image.size)}


def dimensions(path):
    with Image.open(path) as im:
        im.load()
        return {"nativeSize": list(im.size), "originalMode": im.mode, "format": im.format}


def copy_original(src, dst):
    # Byte-for-byte import; never resize, convert, or relabel dimensions.
    before = file_record(src)
    result = save_bytes(dst, safe_path(src).read_bytes())
    require(before["sha256"] == result["sha256"] == sha(src), "Source changed during copy")
    return result


def parse_stem(stem):
    match = STEM_RE.fullmatch(stem)
    require(match is not None, "Stem must be rNN_cNN_sNN_NN_aNN")
    tile, row, col, attempt = match.groups()
    require(tile in TILES and 1 <= int(row) <= 4 and 1 <= int(col) <= 4 and int(attempt) > 0,
            "Tile/subcell/attempt is outside this six-tile batch")
    return tile, int(row), int(col), int(attempt)


def boxes(tile, row, col):
    tr, tc = map(int, re.findall(r"\d+", tile))
    x, y = (tc - 1) * TILE + (col - 1) * CORE, (tr - 1) * TILE + (row - 1) * CORE
    return [x, y, x + CORE, y + CORE], [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO]


def authority():
    contract, split = read_json(CONTRACT), read_json(SPLIT)
    entry = next(x for x in split["batches"] if x["key"] == "island-west-residences")
    require(set(entry["tiles"]) == TILES, "Current split changes this batch's six coordinates")
    require(safe_path(entry["outputDirectory"], REPO) == BATCH, "Split output path changed")
    require(entry.get("worker") == WORKER, "Split assigned worker changed")
    p = contract["nativePatchPlan"]
    require((p["corePixels"], p["haloPixels"], p["expectedNativePixels"]) == (CORE, HALO, SIZE),
            "Production contract geometry changed")
    return contract, {"contract": file_record(CONTRACT), "split": file_record(SPLIT),
                      "rootRules": file_record(RULES), "allocation": entry}


def gate():
    _, auth = authority()
    require(auth["allocation"].get("status") == "allocated_root_reserved", "Current batch is not allocated_root_reserved")
    rules = RULES.read_text(encoding="utf-8-sig")
    require("allocated_root_reserved" in rules, "Current root rules do not contain the allocation rule")
    require(sha(SPLIT) == auth["split"]["sha256"] and sha(RULES) == auth["rootRules"]["sha256"],
            "Allocation/rules changed during read; retry")
    return {"checkedAtUtc": now(), "ready": True, "basis": "allocated_root_reserved",
            "authority": auth, "ownerAcknowledged": auth["allocation"].get("ownerAcknowledged", False),
            "ownerAcknowledgementRequired": False, "reservedTiles": sorted(TILES),
            "scope": "Formal root allocation; actual coordinate conflicts are checked by precall. No owner acknowledgement inferred."}


def same_selected_anchor_sources(path, dependencies):
    """An unrelated current-index update must not invalidate identical pinned anchors."""
    if path != NORTHWEST / "current-adopted-20261012.json" or not path.is_file():
        return False
    expected = {}
    for rec in dependencies:
        p = safe_path(rec["path"])
        match = re.match(r"(r\d{2}_c\d{2})", p.name)
        if match and p.is_relative_to(NORTHWEST / "tiles") and p.suffix.lower() in {".png", ".json"}:
            expected.setdefault(match[1], {})["image" if p.suffix.lower() == ".png" else "record"] = rec
    if not expected:
        return False
    actual = {x.get("tileId"): x for x in read_json(path).get("tiles", [])}
    for tile, fields in expected.items():
        for key, rec in fields.items():
            current = actual.get(tile, {}).get(key, {})
            if not isinstance(current, dict) or current.get("sha256") != rec["sha256"]:
                return False
            if safe_path(current.get("path", ""), NORTHWEST) != safe_path(rec["path"]):
                return False
    return True


def input_checks(inp):
    """Image, contract and provenance integrity; split upgrades are separate evidence."""
    drift, updates, checked = [], [], set()
    records = [*inp["inputs"], inp["layout"], inp["prompt"], inp["referencesFile"], inp["authority"]["contract"]]
    for neighbor in inp.get("neighbors", []):
        records.extend([neighbor, neighbor["coordinateEvidence"], *neighbor.get("sourceProvenanceDependencies", [])])
    for rec in records:
        p = safe_path(rec["path"])
        if p in checked:
            continue
        checked.add(p)
        current = sha(p) if p.is_file() else None
        if current != rec["sha256"]:
            if same_selected_anchor_sources(p, records):
                updates.append({"kind": "current_index_metadata_updated_same_anchor_sources", "prepared": rec,
                                "current": file_record(p), "imageDrift": False})
                continue
            drift.append({"path": p.as_posix(), "submittedSha256": rec["sha256"], "currentSha256": current,
                          "role": "prepared image, layout, prompt, contract or neighbor provenance changed/missing"})
    old = inp["authority"].get("split")
    if old and sha(SPLIT) != old["sha256"]:
        updates.append({"kind": "allocation_metadata_updated", "prepared": old, "current": file_record(SPLIT),
                        "imageDrift": False, "reason": "Current allocation validated independently; historical split hash is not image bytes."})
    return drift, updates


def current_conflicts(stem):
    """Read only current selection/progress and exact tile-native filenames; no history scan."""
    tile, row, col, _ = parse_stem(stem)
    coordinate = f"{tile}_s{row:02d}_{col:02d}"
    def relevant(value):
        text = json.dumps(value, ensure_ascii=False)
        patches = re.findall(r"r\d{2}_c\d{2}_s\d{2}_\d{2}", text)
        return coordinate in patches if patches else tile in text
    evidence, conflicts = [], []
    names = ("current-adopted-20261012.json", "selected-native.json", "root-current-selection-20261012.json",
             "west-current-selection-20261012.json", "right-current-selection-20261012.json", "progress.json")
    for name in names:
        path = NORTHWEST / name
        if not path.is_file():
            evidence.append({"path": path.as_posix(), "exists": False})
            continue
        data = read_json(path)
        evidence.append(file_record(path))
        def visit(node, at="$", context=None):
            if isinstance(node, dict):
                context = node.get("tileId", node.get("tile", context))
                for key, value in node.items():
                    child = f"{at}.{key}"
                    if isinstance(value, str) and value.lower().endswith(".png") and (relevant(value) or (context == tile and not re.search(r"r\d{2}_c\d{2}", value))):
                        candidate = safe_path(value, NORTHWEST)
                        if candidate.is_file() and not candidate.is_relative_to(BATCH):
                            conflicts.append({"kind": "current_external_source", "source": path.as_posix(), "jsonPath": child,
                                              "image": file_record(candidate)})
                    if "inflight" in key.lower() and value and relevant(value):
                        conflicts.append({"kind": "current_external_inflight", "source": path.as_posix(), "jsonPath": child, "value": value})
                    visit(value, child, key if key in TILES else context)
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    visit(value, f"{at}[{index}]", context)
        visit(data)
        if name == "progress.json" and relevant(data.get("currentPatch") or data.get("currentTile")):
            if data.get("inflightCount", 0) > 0 or data.get("status") in {"generating", "generation_running", "inflight"}:
                conflicts.append({"kind": "current_external_progress_inflight", "source": path.as_posix(),
                                  "currentTile": data.get("currentTile"), "currentPatch": data.get("currentPatch"), "status": data.get("status")})
    native_dir = NORTHWEST / "native"
    for path in native_dir.glob(f"{coordinate}_a*.png"):
        conflicts.append({"kind": "external_native_exists_for_reserved_coordinate", "image": file_record(path)})
    existing = [{**file_record(p), **dimensions(p)} for p in (BATCH / "native").glob(f"{coordinate}_a*.png")]
    return {"checkedAtUtc": now(), "tile": tile, "coordinate": coordinate, "currentStateEvidence": evidence,
            "externalConflicts": conflicts, "existingBatchNativeForCoordinate": existing,
            "scope": "Current northwest indexes and exact reserved native coordinate names; conflict hold applies only to the requested coordinate."}


def precall(args):
    tile, row, col, _ = parse_stem(args.stem)
    allocation = gate()
    input_path = BATCH / f"guides/{args.stem}.input.json"
    inp = read_json(input_path)
    core, box = boxes(tile, row, col)
    require(inp.get("globalBox") == box and inp.get("coreBox") == core and inp.get("stem") == args.stem,
            "Prepared attempt coordinates mismatch")
    drift, updates = input_checks(inp)
    conflict = current_conflicts(args.stem)
    same_attempt = (BATCH / f"native/{args.stem}.png").exists()
    retry_needed = bool(conflict["existingBatchNativeForCoordinate"]) and not args.retry_reason
    ready = not (drift or conflict["externalConflicts"] or same_attempt or retry_needed)
    value = {"schemaVersion": 2, "checkedAtUtc": now(), "stem": args.stem, "ready": ready,
             "status": "ready_for_actual_builtin_call" if ready else "coordinate_hold_review_evidence",
             "input": file_record(input_path), "allocationGate": allocation, "authorizationUpdates": updates,
             "inputDrift": drift, "coordinateCheck": conflict, "sameAttemptAlreadySaved": same_attempt,
             "retryReasonRequired": retry_needed, "retryReason": args.retry_reason,
             "prompt": inp["prompt"], "referenced_image_paths": inp["imageGenReferencedImagePaths"],
             "transparent_background": False, "nativeGenerationPerformed": False}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    record = save_json(BATCH / f"precall/{args.stem}.{stamp}.json", value)
    return {**value, "precallRecord": record}


def coordinate_evidence(path, explicit=None):
    if explicit:
        candidates = [safe_path(explicit)]
    else:
        candidates = [path.with_name(path.name + ".derivation.json"), path.with_suffix(".derivation.json"),
                      path.parent.parent / "guides" / f"{path.stem}.input.json"]
    for p in candidates:
        if p.is_file():
            data = read_json(p)
            box = data.get("globalBox", data.get("globalNativeBox"))
            if box is None:
                box = data.get("geometry", {}).get("globalNativeBox")
            if box is not None:
                image_sha = sha(path)
                dependencies = []
                if isinstance(data.get("sha256"), str):
                    require(data["sha256"] == image_sha, "Neighbor sidecar is for different image bytes")
                    named = data.get("file", data.get("path"))
                    if isinstance(named, str):
                        require(safe_path(named, p.parent) == path, "Neighbor sidecar names another image")
                else:
                    generation_path = path.with_name(path.name + ".generation.json")
                    require(generation_path.is_file(), "Neighbor requires pinned image sidecar or original generation record")
                    gen = read_json(generation_path)
                    require(gen.get("sha256") == image_sha, "Neighbor generation record hash mismatch")
                    require(p.name == f"{path.stem}.input.json", "Neighbor input must name the exact raw attempt")
                    require(gen.get("globalBox") == box, "Neighbor generation/input global coordinates mismatch")
                    require(safe_path(gen.get("input", {}).get("path", ""), generation_path.parent) == p
                            and gen.get("input", {}).get("sha256") == sha(p),
                            "Neighbor generation must pin this exact input path/hash")
                    dependencies.append(file_record(generation_path))
                if data.get("mechanicalReference") is True:
                    manifest_path = path.parent / "current-south-anchors.manifest.json"
                    manifest = read_json(manifest_path)
                    require(manifest.get("status") == "ready_mechanical_references_only" and manifest.get("inputDrift") == [] and manifest.get("authorityUnchanged") is True,
                            "Current mechanical anchor export must be complete and drift-free")
                    exported = [x.get("reference", {}) for x in manifest.get("exports", [])]
                    require(any(safe_path(x.get("path", ""), manifest_path.parent) == path and x.get("sha256") == image_sha for x in exported),
                            "Anchor manifest does not pin this exact reference")
                    dependencies.extend([file_record(manifest_path), manifest["authorityAtEnd"]])
                    for key in ("currentCandidate", "currentCandidateRecord", "verifiedCurrentCoreProof"):
                        if isinstance(data.get(key), dict):
                            dependencies.append(data[key])
                    for source in data.get("currentCoreSourceRegistry", []):
                        dependencies.extend(source[k] for k in ("image", "record", "proof") if isinstance(source.get(k), dict))
                for dependency in dependencies:
                    dependency_path = safe_path(dependency["path"], p.parent)
                    require(sha(dependency_path) == dependency["sha256"] or same_selected_anchor_sources(dependency_path, dependencies),
                            "Neighbor provenance/authority changed; export/review a new anchor version")
                return box, file_record(p), dependencies
    raise ValueError(f"No explicit same-version neighbor coordinate evidence: {path}; supply --SIDE-record")


def returned_model_evidence(value):
    """Read only explicitly actual-model fields, never a submitted/requested model."""
    found = []
    forbidden = {"submitted", "request", "requested", "input", "prompt", "config", "configSnapshot"}
    def visit(node, at="$", depth=0):
        if depth > 20:
            return
        if isinstance(node, dict):
            for key, item in node.items():
                if key in forbidden:
                    continue
                child = f"{at}.{key}"
                if key in {"actualModel", "actual_model", "actual_model_id", "model_used"} and isinstance(item, str) and item.strip():
                    found.append({"jsonPath": child, "value": item})
                elif isinstance(item, (dict, list)):
                    visit(item, child, depth + 1)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                visit(item, f"{at}[{index}]", depth + 1)
    visit(value)
    models = {x["value"] for x in found}
    return (next(iter(models)) if len(models) == 1 else None), found


def default_prompt(stem, global_box, neighbors):
    sides = ", ".join(x["direction"] for x in neighbors) or "none yet"
    return (f"Generate ONE native 1254x1254 opaque square PNG for eight-immortals island patch {stem}. "
            f"Its exact global halo box is {global_box}; central 1024x1024 core starts at (115,115). "
            "Reference1 is the exact target layout crop with unresampled neighbor overlap strips, only a layout guide; "
            "redraw the low-resolution guide into genuinely detailed native art. Reference2 is independent island detail style, "
            "reference3 and reference4 are approved Daoist Q painterly style only: do not copy UI, text, characters or night lighting. "
            f"Exact adjacent sides in guide: {sides}; continue their roads, shore, stone joints, walls, plants and values "
            "at matching coordinates throughout each 230px overlap, do not move them or invent seams. "
            "Keep the approved island's north sea, rocks, courtyard walls, plants and immortal-residence upper edges in place. "
            "Bright daylight; refined rounded Daoist Q hand-painted art, natural light grey/blue-grey stones with subtle joints, "
            "jade/teal roofs, ivory walls, modest warm gold, vermilion doors and Spring Festival lantern/window details; "
            "sparse Lantern Festival/Mid-Autumn props, no district redesign. Keep roads open and connected, trees only by buildings "
            "or walls, existing short north/south exits. No people, NPCs, UI, frames, labels, grids, watermark, red paving, "
            "free-standing street trees, added residences or enlarged coast. Do not upscale the overview or return a preview. "
            "Use the existing included builtin image route: free2.5 preferred, builtin2.0 allowed, no paid API. "
            "The full image must be exactly1254x1254, detailed to its edges, with no padding frame.")


def prepare(args):
    contract, auth = authority()
    require(not args.geometry_references_only or args.prompt_file,
            "--geometry-references-only requires --prompt-file with the actual reduced-reference instructions")
    require(args.tile in TILES and 1 <= args.subrow <= 4 and 1 <= args.subcol <= 4 and args.attempt > 0,
            "Requested coordinate/attempt is outside batch")
    stem = f"{args.tile}_s{args.subrow:02d}_{args.subcol:02d}_a{args.attempt:02d}"
    core_box, global_box = boxes(args.tile, args.subrow, args.subcol)
    paths = {"guide": BATCH / f"guides/{stem}.layout-with-native.png",
             "input": BATCH / f"guides/{stem}.input.json",
             "references": BATCH / f"guides/{stem}.references.json",
             "prompt": BATCH / f"prompts/{stem}.txt",
             "contact": BATCH / f"guides/{stem}.neighbor-contact.png"}
    for p in paths.values():
        require(not output_path(p).exists(), f"Attempt already has an artifact; choose a new aNN: {p}")
    require(not (BATCH / f"native/{stem}.png").exists(), "Native attempt already exists")
    layout_path = safe_path(contract["layoutReference"])
    layout_file = file_record(layout_path, "sole current layout; forbidden as final pixels")
    require(layout_file["sha256"] == contract["layoutSha256"], "Contract layout source hash changed")
    with Image.open(layout_path) as im:
        im.load()
        require(im.width == im.height, "Contract layout must have uniform square mapping")
        layout_size = im.size
        source = np.asarray(im.convert("RGB"))
    canvas_w, canvas_h = contract["artCanvasPixels"]
    crop = [global_box[0] * layout_size[0] / canvas_w, global_box[1] * layout_size[1] / canvas_h,
            global_box[2] * layout_size[0] / canvas_w, global_box[3] * layout_size[1] / canvas_h]
    pad = max(3, int(np.ceil(max(0, -min(crop), max(crop) - max(layout_size)))) + 3)
    padded = Image.fromarray(np.pad(source, ((pad, pad), (pad, pad), (0, 0)), mode="edge"))
    guide = padded.transform((SIZE, SIZE), Image.Transform.EXTENT,
                             tuple(v + pad for v in crop), Image.Resampling.BICUBIC)
    shifts = {"north": (0, -CORE), "south": (0, CORE), "west": (-CORE, 0), "east": (CORE, 0)}
    paste = {"north": ((0, CORE, SIZE, SIZE), (0, 0)),
             "south": ((0, 0, SIZE, OVERLAP), (0, CORE)),
             "west": ((CORE, 0, SIZE, SIZE), (0, 0)),
             "east": ((0, 0, OVERLAP, SIZE), (CORE, 0))}
    neighbors, contacts = [], []
    for direction in ("north", "south", "west", "east"):
        value = getattr(args, direction)
        if not value:
            continue
        p = safe_path(value)
        box, coord, provenance_dependencies = coordinate_evidence(p, getattr(args, direction + "_record"))
        dx, dy = shifts[direction]
        require(box == [global_box[0] + dx, global_box[1] + dy, global_box[2] + dx, global_box[3] + dy],
                f"{direction} neighbor is not exactly one1024-core step from target: {box}")
        meta = dimensions(p)
        require(meta["nativeSize"] == [SIZE, SIZE] and meta["format"] == "PNG", "Neighbor must actually be1254 square PNG")
        with Image.open(p) as im:
            require(im.mode in ("RGB", "RGBA"), "Neighbor mode must be RGB/RGBA")
            if im.mode == "RGBA":
                require(im.getextrema()[3] == (255, 255), "Neighbor alpha must be opaque")
            im = im.convert("RGB")
            source_crop, destination = paste[direction]
            guide.paste(im.crop(source_crop), destination)
            contacts.append(im.copy())
        neighbors.append({**file_record(p, f"{direction} exact1254 adjacent native/verified mechanical reference"),
                          **meta, "direction": direction, "globalBox": box, "coordinateEvidence": coord,
                          "sourceProvenanceDependencies": provenance_dependencies,
                          "sourceCrop": list(source_crop), "destination": list(destination), "resized": False})
    guide_file = save_image(paths["guide"], guide)
    refs = [{**guide_file, "role": "target-layout-only guide with exact native230px neighbor overlap; not final art"}]
    style_references = (
        (safe_path(contract["detailStyleReference"]), "independent island material/style detail; not coordinate crop", contract["detailSha256"]),
        (REPO / "designs/mail-ui-v1/01-mail-event.png", "user primary mail style only; exclude UI/night/characters", None),
        (REPO / "designs/team-ui-v2/team-ui-v2.png", "user primary team style only; exclude UI/night/characters", None))
    for path, role, expected in (() if args.geometry_references_only else style_references):
        rec = {**file_record(path, role), **dimensions(path)}
        require(expected is None or rec["sha256"] == expected, "Contract detail hash changed")
        refs.append(rec)
    if contacts and not args.no_neighbor_contact:
        # Unresampled full-size contact. It is an auxiliary reference, never native source art.
        contact = Image.new("RGB", (SIZE * len(contacts), SIZE))
        for index, im in enumerate(contacts):
            contact.paste(im, (SIZE * index, 0))
        refs.append({**save_image(paths["contact"], contact), "role": "full-size adjacent contact; panels in recorded neighbor order; no resampling", "neighbors": neighbors})
    require(len(refs) <= 5, "At most five submitted image references")
    prompt_text = safe_path(args.prompt_file).read_text(encoding="utf-8-sig") if args.prompt_file else default_prompt(stem, global_box, neighbors)
    require(bool(prompt_text.strip()), "Prompt is empty")
    prompt_file = save_bytes(paths["prompt"], prompt_text.encode("utf-8"))
    references_file = save_json(paths["references"], {"schemaVersion": 1, "stem": stem, "inputs": refs,
                                                    "imageGenReferencedImagePaths": [x["path"] for x in refs]})
    out_of_canvas = {"left": max(0, -global_box[0]), "top": max(0, -global_box[1]),
                     "right": max(0, global_box[2] - canvas_w), "bottom": max(0, global_box[3] - canvas_h)}
    data = {"schemaVersion": 1, "createdAtUtc": now(), "tile": args.tile, "versionStem": stem, "stem": stem,
            "attempt": f"a{args.attempt:02d}", "subrow": args.subrow, "subcolumn": args.subcol,
            "globalBox": global_box, "coreBox": core_box, "referenceBox": crop,
            "geometry": {"nativePixels": SIZE, "corePixels": CORE, "haloPixels": HALO, "overlapPixels": OVERLAP},
            "inputs": refs, "imageGenReferencedImagePaths": [x["path"] for x in refs], "inputCount": len(refs),
            "referenceMode": "target_geometry_and_adjacent_only" if args.geometry_references_only else "layout_style_and_adjacent",
            "layout": layout_file, "neighbors": neighbors, "neighborPasteOrder": [x["direction"] for x in neighbors],
            "cornerRule": "later explicitly listed neighbor owns overlapping guide corner; visual continuity not asserted",
            "guide": guide_file, "referencesFile": references_file, "prompt": prompt_file,
            "authority": auth, "edgeExtension": {"method": "edge-repeat overview pad then floating EXTENT bicubic sampling; layout guide only",
                                                   "overviewPadPixelsPerSide": pad, "outOfCanvasHaloPixels": out_of_canvas,
                                                   "coreOutsideCanvas": False, "blackFillUsed": False},
            "nativeGenerationPerformed": False, "layoutPixelsForbiddenInFinal": True,
            "status": "prepared_only_fresh_allocation_precall_required_before_actual_generation", "formalAccepted": False}
    input_file = save_json(paths["input"], data)
    return {"status": data["status"], "stem": stem, "input": input_file, "prompt": prompt_file,
            "guide": guide_file, "referenced_image_paths": data["imageGenReferencedImagePaths"], "nativeGenerationPerformed": False}


def ingest(args):
    tile, row, col, _ = parse_stem(args.stem)
    allocation_gate = gate()
    input_path = BATCH / f"guides/{args.stem}.input.json"
    inp = read_json(input_path)
    expected_core, expected_box = boxes(tile, row, col)
    require(inp.get("globalBox") == expected_box and inp.get("coreBox") == expected_core, "Attempt input coordinates mismatch")
    drift, authorization_updates = input_checks(inp)
    prompt = inp["prompt"]
    require(sha(safe_path(prompt["path"])) == prompt["sha256"], "Prepared prompt changed; create fresh attempt instead")
    precall_record = None
    if args.precall_record:
        pre_path = safe_path(args.precall_record)
        pre = read_json(pre_path)
        require(pre.get("ready") is True and pre.get("stem") == args.stem,
                "Precall record must be ready and for this exact attempt")
        require(pre.get("input", {}).get("sha256") == sha(input_path)
                and pre.get("referenced_image_paths") == inp["imageGenReferencedImagePaths"],
                "Precall record must pin this exact input and reference list")
        precall_record = file_record(pre_path)
    raw, tool_result = safe_path(args.raw), safe_path(args.tool_result)
    require(raw != tool_result, "Raw image and real tool-result JSON must be distinct")
    actual_result = read_json(tool_result)
    require(isinstance(actual_result, (dict, list)) and bool(actual_result), "Save the actual nonempty image_gen tool result, not an invented receipt")
    require(not (isinstance(actual_result, dict) and actual_result.get("isError") is True), "Tool result reports an error")
    actual_model, model_evidence = returned_model_evidence(actual_result)
    measured = dimensions(raw)
    dest = BATCH / f"native/{args.stem}.png"
    record_path = dest.with_name(dest.name + ".generation.json")
    receipt_path = BATCH / f"receipts/{args.stem}.receipt.json"
    saved_result = BATCH / f"receipts/{args.stem}.tool-result.json"
    for p in (dest, record_path, receipt_path, saved_result):
        require(not output_path(p).exists(), f"Ingest artifact already exists: {p}")
    # Preserve even wrong-size actual outputs. No resize or dimensions substitution.
    image_record = copy_original(raw, dest)
    tool_record = copy_original(tool_result, saved_result)
    valid = measured["nativeSize"] == [SIZE, SIZE] and measured["format"] == "PNG" and measured["originalMode"] in ("RGB", "RGBA")
    if valid and measured["originalMode"] == "RGBA":
        with Image.open(dest) as im:
            valid = im.getextrema()[3] == (255, 255)
    receipt = {"schemaVersion": 1, "capturedAtUtc": now(), "tool": "image_gen.imagegen", "route": "builtin",
               "receiptIsMechanicalWrapper": True, "originalToolResult": tool_record,
               "originalRawSource": file_record(raw), "importedRaw": image_record,
               "submitted": {"promptFile": prompt["path"], "promptSha256": prompt["sha256"],
                             "referenced_image_paths": inp["imageGenReferencedImagePaths"], "transparent_background": False},
               "submissionEvidenceBasis": "root selected prepared prompt/references and supplied the actual tool-result JSON; wrapper does not independently execute the tool",
               "allocationGateAtIngest": allocation_gate, "authorizationUpdates": authorization_updates,
               "precallEvidence": precall_record,
               "generationPreCallGateMustBeRecordedByRoot": True,
               "noAiCallPerformedByThisTool": True}
    receipt_file = save_json(receipt_path, receipt)
    _, auth = authority()
    generation = {"schemaVersion": 1, "ingestedAtUtc": now(), "generatedAt": args.generated_at,
                  "stem": args.stem, "tile": tile, "subrow": row, "subcolumn": col,
                  "globalBox": expected_box, "coreBox": expected_core, "path": dest.as_posix(),
                  "sha256": image_record["sha256"], "nativeWidth": measured["nativeSize"][0], "nativeHeight": measured["nativeSize"][1],
                  "format": measured["format"], "originalMode": measured["originalMode"],
                  "tool": "image_gen.imagegen", "route": "builtin", "actualModel": actual_model, "actualQuality": None,
                  "actualModelEvidence": model_evidence or "未返回；本工具不从目标偏好推断实际型号",
                  "unverifiedReason": "Quality unconfirmed; model remains null if explicit actual-model field is absent/contradictory; original tool result preserved",
                  "modelPreference": "free/included2.5 preferred; builtin2.0 allowed; no paidAPI",
                  "resizedAfterGeneration": False, "finalArtUpscaled": False,
                  "prompt": prompt["path"], "promptSha256": prompt["sha256"], "references": inp["inputs"],
                  "input": file_record(input_path), "submittedParameters": receipt["submitted"],
                  "configSnapshot": auth, "evidence": {"receipt": receipt_file["path"], "toolResult": tool_record},
                  "allocationGateAtIngest": allocation_gate, "authorizationUpdates": authorization_updates,
                  "precallEvidence": precall_record,
                  "status": "native_candidate_unreviewed" if valid else "rejected_actual_dimensions_format_or_alpha_raw_preserved",
                  "nativeGeometryEligible": valid, "requiresReferenceRecheck": bool(drift), "inputDrift": drift,
                  "visualReviewed": False, "formalAccepted": False}
    if valid and drift:
        generation["status"] = "native_candidate_reference_drift_requires_recheck"
    gen_file = save_json(record_path, generation)
    return {"status": generation["status"], "nativeGeometryEligible": valid, "requiresReferenceRecheck": bool(drift),
            "raw": image_record, "measured": measured, "generationRecord": gen_file, "receipt": receipt_file}


def assemble(args):
    manifest_path = safe_path(args.manifest)
    require(manifest_path.is_relative_to(BATCH), "Assembly manifest must be batch-local")
    manifest = read_json(manifest_path)
    require(manifest.get("tileId") in TILES, "Assembly tile is outside batch")
    script = BATCH / "tools/assemble_tile.py"
    spec = importlib.util.spec_from_file_location("island_west_batch_assembler", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    old_argv = sys.argv[:]
    try:
        sys.argv = [str(script), "--manifest", str(manifest_path), "--output", str(output_path(args.output))]
        module.main()
    finally:
        sys.argv = old_argv
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare", help="Create layout-only guide/prompt/ref records; does not authorize generation")
    prep.add_argument("--tile", required=True, choices=sorted(TILES))
    prep.add_argument("--subrow", type=int, required=True)
    prep.add_argument("--subcol", type=int, required=True)
    prep.add_argument("--attempt", type=int, required=True)
    prep.add_argument("--prompt-file", help="Optional actual prompt copied into a fresh immutable attempt")
    prep.add_argument("--no-neighbor-contact", action="store_true")
    prep.add_argument("--geometry-references-only", action="store_true",
                      help="Submit only the target guide and optional adjacent contact; requires a matching --prompt-file")
    for side in ("north", "south", "west", "east"):
        prep.add_argument("--" + side, help="Explicit adjacent1254 PNG; never latest/glob selection")
        prep.add_argument("--" + side + "-record", help="Optional explicit neighbor coordinate evidence JSON")
    ing = sub.add_parser("ingest", help="Gate+byte-copy actual tool output; invalid native size remains preserved and rejected")
    ing.add_argument("--stem", required=True)
    ing.add_argument("--raw", required=True)
    ing.add_argument("--tool-result", required=True, help="Actual saved unmodified image_gen JSON result")
    ing.add_argument("--generated-at", help="Actual generation timestamp if known; omitted remains null")
    ing.add_argument("--precall-record", help="Optional exact ready precall record to pin in receipt and generation provenance")
    asm = sub.add_parser("assemble", help="Explicit4x4 pinned manifest to4096 native candidate+source NPZ+100pct QA")
    asm.add_argument("--manifest", required=True)
    asm.add_argument("--output", required=True)
    sub.add_parser("gate", help="Read-only allocated_root_reserved check; owner acknowledgement is not required")
    pre = sub.add_parser("precall", help="Save fresh allocation, input hash and current-coordinate conflict evidence before an actual AI call")
    pre.add_argument("--stem", required=True)
    pre.add_argument("--retry-reason", help="Required only when this batch already has another raw attempt for this coordinate")
    args = p.parse_args()
    result = {"prepare": prepare, "precall": precall, "ingest": ingest, "assemble": assemble}.get(args.command)
    value = result(args) if result else gate()
    if value is not None:
        print(json.dumps(value, ensure_ascii=False, indent=2))
        if args.command == "precall" and not value["ready"]:
            sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, StopIteration, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc), "formalAccepted": False}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
