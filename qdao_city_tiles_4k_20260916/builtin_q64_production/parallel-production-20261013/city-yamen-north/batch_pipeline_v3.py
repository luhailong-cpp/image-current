"""Local reference, receipt, and native assembly helpers; no network/image API calls."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import shutil
from PIL import Image

BATCH = Path(__file__).resolve().parent
BASE = BATCH.parent.parent
ROOT = BASE.parent.parent
TILES = {"r01_c04", "r01_c05", "r02_c04", "r02_c05"}
ALLOCATION = ROOT / "docs/MAP_PARALLEL_SPLIT_20261013.json"
WORKER = "01a1338b-73d0-75c1-aa57-8059e93e85a1"
OWNER = BASE / "main-city-game-20261009/northwest"
PLAN = BATCH / "preparation-coordinate-plan-v1.json"
BOUNDARIES = BATCH / "boundary-source-snapshot-v1.json"
CONTRACT = BASE / "main-city-game-20261009/production-contract.json"

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write_new(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2)

def next_path(directory, prefix, suffix=".json"):
    directory.mkdir(parents=True, exist_ok=True)
    for version in range(1, 10000):
        path = directory / f"{prefix}-v{version:03d}{suffix}"
        if not path.exists():
            return path
    raise RuntimeError("Version range exhausted")

def existing_image_refs(value, source_directory):
    """Resolve only actual files, not stale selected counts or historical claims."""
    found = []
    if isinstance(value, dict):
        for child in value.values():
            found.extend(existing_image_refs(child, source_directory))
    elif isinstance(value, list):
        for child in value:
            found.extend(existing_image_refs(child, source_directory))
    elif isinstance(value, str) and value.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        candidate = Path(value)
        options = [candidate] if candidate.is_absolute() else [source_directory / candidate, ROOT / candidate]
        for path in options:
            if path.is_file():
                found.append({"file": str(path.resolve()), "sha256": sha(path)})
                break
    return found

def is_published_active(value):
    if value in (None, False, "", [], {}):
        return False
    if isinstance(value, dict):
        if value.get("active") is False or value.get("inFlight") is False:
            return False
        if str(value.get("status", "")).lower() in ("completed", "complete", "cancelled", "canceled", "failed", "idle", "inactive", "done"):
            return False
    return True

def activity_refs(value, path=""):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            field = f"{path}.{key}" if path else key
            normalized = re.sub(r"[^a-z]", "", key.lower())
            if normalized.startswith(("active", "inflight", "currentlygenerating")) or normalized in ("currenttile", "generatingtile"):
                if not is_published_active(child):
                    continue
                text = json.dumps(child, ensure_ascii=False)
                for tile in sorted(set(re.findall(r"r\d{2}_c\d{2}", text)) & TILES):
                    found.append({"tile": tile, "field": field, "value": child})
            else:
                found.extend(activity_refs(child, field))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, (dict, list)):
                found.extend(activity_refs(child, f"{path}[{index}]"))
    return found

def gate(required=True, tile=None):
    if tile is not None and tile not in TILES:
        raise RuntimeError("Outside assigned batch")
    allocation = read(ALLOCATION)
    matches = [b for b in allocation.get("batches", []) if b.get("key") == "city-yamen-north"]
    batch = matches[0] if len(matches) == 1 else {}
    reserved = batch.get("tiles", [])
    valid = (allocation.get("status") == "allocated_root_reserved"
             and batch.get("status") == "allocated_root_reserved"
             and batch.get("worker") == WORKER
             and batch.get("map") == "main-city-game-20261009"
             and len(reserved) == len(TILES) and set(reserved) == TILES
             and bool(batch.get("outputDirectory"))
             and (ROOT / batch.get("outputDirectory", "")).resolve() == BATCH)
    progress_file = OWNER / "progress.json"
    progress = read(progress_file) if progress_file.is_file() else {}
    activity = activity_refs(progress, "progress")
    markers = []
    for marker in sorted(OWNER.glob("*.json")):
        stem = re.sub(r"[^a-z]", "", marker.stem.lower())
        if stem.startswith(("active", "inflight", "currentactivity")):
            value = read(marker)
            markers.append({"file": str(marker), "sha256": sha(marker)})
            activity.extend(activity_refs(value, str(marker)))
            # A dedicated in-flight marker may store a plain tile field.
            if stem.startswith(("active", "inflight")) and is_published_active(value):
                for target in sorted(set(re.findall(r"r\d{2}_c\d{2}", json.dumps(value))) & TILES):
                    activity.append({"tile": target, "field": str(marker), "value": value})
    checks = {}
    for target in sorted(TILES if tile is None else {tile}):
        directory = OWNER / target
        selection_file = directory / "selection.json"
        selection = read(selection_file) if selection_file.is_file() else {}
        selected_sources = existing_image_refs(selection, directory)
        native = [{"file": str(p), "sha256": sha(p)} for p in sorted((directory / "native").glob("*.png")) if p.is_file()]
        records = progress.get("tiles", [])
        if isinstance(records, dict):
            record = records.get(target, {})
        else:
            record = next((r for r in records if r.get("tile") == target), {})
        progress_sources = existing_image_refs(record, directory)
        progress_sources.extend(existing_image_refs([p for p in progress.get("nativeFiles", []) if target in str(p)], OWNER))
        hits = [a for a in activity if a["tile"] == target]
        conflict = bool(native or selected_sources or progress_sources or hits)
        checks[target] = {"actualConflict": conflict, "ready": valid and not conflict,
                          "originalOwnerNativeFiles": native, "effectiveSelectedSources": selected_sources,
                          "currentProgressSourceFiles": progress_sources, "activityHits": hits,
                          "selectionFile": str(selection_file),
                          "selectionSHA256": sha(selection_file) if selection_file.is_file() else None}
    result = {"file": str(ALLOCATION), "sha256": sha(ALLOCATION), "checkedAtUTC": now(),
              "allocationValid": valid, "allocationStatus": batch.get("status"), "worker": batch.get("worker"),
              "ownerAcknowledged": False, "ownerAcknowledgementRequiredAsGate": False,
              "allocationDoesNotProveOwnerAcknowledgement": True, "requestedTile": tile,
              "ready": valid and any(c["ready"] for c in checks.values()), "perTile": checks,
              "progressFile": str(progress_file), "progressSHA256": sha(progress_file) if progress_file.is_file() else None,
              "activityMarkers": markers, "scope": "Current published owner records and target files only; no unpublished in-flight inference"}
    conflicts = [t for t, c in checks.items() if c["actualConflict"]]
    if conflicts:
        evidence = next_path(BATCH / "conflicts", "allocation-conflict")
        write_new(evidence, result)
        result["conflictEvidenceFile"] = str(evidence)
    if required and not result["ready"]:
        raise RuntimeError(f"Allocation invalid or requested coordinate has real source/in-flight conflict: {json.dumps(result, ensure_ascii=False)}")
    return result

def selected(tile):
    if tile not in TILES:
        return {}
    files = sorted((BATCH / tile / "selection").glob("selection-v*.json"))
    # A dimensions-only legacy selection is not evidence of a visual pass.
    items = read(files[-1])["selected"] if files else {}
    return {patch: item for patch, item in items.items() if item.get("quickVisualPassed") is True}

def spec(tile, patch):
    if tile not in TILES:
        raise RuntimeError("Outside assigned batch")
    return next(p for p in read(PLAN)["patches"] if p["tile"] == tile and p["patch"] == patch)

def overlap(a, b):
    box = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    return box if box[0] < box[2] and box[1] < box[3] else None

def source_ref(file, world_box, expected=None, role="native_context"):
    file = Path(file)
    actual = sha(file)
    if expected and actual != expected:
        raise RuntimeError(f"Source drift: {file}")
    with Image.open(file) as image:
        pixels = list(image.size)
    if pixels != [world_box[2] - world_box[0], world_box[3] - world_box[1]]:
        raise RuntimeError(f"Source/world dimensions disagree: {file}")
    return {"file": str(file), "sha256": actual, "pixels": pixels, "worldBox": world_box, "role": role}

def prepare(tile, patch):
    p = spec(tile, patch)
    allocation_gate = gate(True, tile)
    contract = read(CONTRACT)
    layout = Path(contract["layoutReference"])
    if sha(layout) != contract["layoutSha256"]:
        raise RuntimeError("Approved layout hash changed")
    world = p["worldBoxWithHalo"]
    # Enlargement is a spatial guide only, never a production source or native output.
    with Image.open(layout) as image:
        w, h = image.size
        extent = (world[0] * w / 65536, world[1] * h / 65536, world[2] * w / 65536, world[3] * h / 65536)
        guide = image.convert("RGB").transform((1254, 1254), Image.Transform.EXTENT, extent, Image.Resampling.BICUBIC)
    refs = []
    boundary = read(BOUNDARIES)
    for source in boundary["sources"]:
        if source["role"] == "canonical_adopted_candidate_north_edge":
            if overlap(world, source["worldBox"]):
                refs.append(source_ref(source["file"], source["worldBox"], source["sha256"], "authoritative_current_adopted_neighbor"))
        elif source.get("tile") == p["southContinuationDependency"]["tile"] and source.get("patch") == p["southContinuationDependency"]["patch"]:
            coords = source.get("coordinates", source.get("expectedCoordinates", {}))
            wb = source.get("worldBoxWithHalo", coords.get("worldBoxWithHalo"))
            if wb:
                refs.insert(0, source_ref(source["file"], wb, source["sha256"], "current_selected_south_halo_context"))
    # Selected outputs inside this batch are one-to-one neighbor references.
    for owned in sorted(TILES):
        for item in selected(owned).values():
            wb = item["coordinates"]["worldBoxWithHalo"]
            if overlap(world, wb):
                refs.append(source_ref(item["file"], wb, item["sha256"], "selected_generated_batch_neighbor"))
    context_pastes = []
    for ref in refs:
        intersection = overlap(world, ref["worldBox"])
        if not intersection:
            continue
        x0, y0, x1, y1 = intersection
        crop = [x0 - ref["worldBox"][0], y0 - ref["worldBox"][1], x1 - ref["worldBox"][0], y1 - ref["worldBox"][1]]
        dest = [x0 - world[0], y0 - world[1]]
        with Image.open(ref["file"]) as image:
            guide.paste(image.convert("RGB").crop(crop), dest)
        context_pastes.append({"source": ref, "sourceCropLTRB": crop, "guidePasteXY": dest, "resampled": False})
    request_path = next_path(BATCH / "requests" / tile, patch)
    guide_path = request_path.with_suffix(".layout-and-native-reference.png")
    guide.save(guide_path)
    reference_paths = [str(guide_path)]
    # All available neighbor overlaps are already pasted in the guide at 1:1.
    # Do not attach a separate native crop whose composition could be copied.
    reference_paths.extend([str(layout), str(ROOT / "designs/mail-ui-v1/01-mail-event.png"), str(ROOT / "designs/team-ui-v2/team-ui-v2.png")])
    prompt = f"""Use case: stylized-concept.
Asset: one native map continuation patch, exactly 1254 by 1254 pixels, no border, no labels.
Edit image 1 as the STRICT composition target at identical scale and pixel alignment. This is tile {tile}, patch {patch}, world rectangle {world}; its central 1024 square is pixels [115,115,1139,1139]. Image 1 combines an explicitly enlarged low-resolution APPROVED LAYOUT GUIDE with sharp existing native neighbor overlap. It is only a geometry/context guide, not a finished output. Newly paint clean detailed art only where the guide is low resolution; do not simply enlarge or sharpen it. Preserve every sharp strip along the bottom, left, right or top as a hard boundary constraint at exactly the same coordinates. Continue roof tile columns and gold ridges directly out of those strips without bending, shifting or changing their pitch. Keep straight gold trim straight. Do not introduce any curl, scroll ornament, finial, flourish or other decoration absent from image 1. Do not import a decorative shape from another reference or fit a whole city/building into this tiny crop.
Input roles: image 1 is the strict local edit target and includes all available exact native neighbor overlap; image 2 is the whole-city image for approved layout only; images 3 and 4 are UI originals for hand-painted Daoist chibi material treatment only. These other images must never change image 1's local composition or add objects. Never copy UI, characters, text, ornaments or night scenery into this map.
Scene: approved daylight Daoist chibi city. In this northern yamen area retain the existing roof silhouette, teal/blue-green ceramic tile directions, warm gold ridges, existing pink/gold foliage and pale gray/blue-gray stone wall/ground where shown by the guide. Spring Festival details belong to the existing architecture. Sparse Lantern Festival/Mid-Autumn accents only where approved. Preserve exact positions; add no buildings, streets, towers, trees, props or signage absent from the guide. Trees remain against walls/buildings. Pure map artwork with readable forms, fine rounded hand-painted shading, consistent daylight; no photorealism, plastic toy sheen, noise or blur. No characters, UI, lettering, grid, arrows or watermark.
Output a newly rendered native 1254x1254 crop with enough real painted detail for a 1024x1024 core; do not resize an existing overview and do not change zoom or perspective. Adjacent native overlaps must keep identical edge positions and continue the same tile columns and material transitions. Output only the image."""
    request = {"schemaVersion": 3, "createdAtUTC": now(), "tile": tile, "patch": patch, "coordinates": p, "prompt": prompt, "referenced_image_paths": reference_paths, "transparent_background": False, "guide": {"file": str(guide_path), "sha256": sha(guide_path), "isEnlargedLayoutGuideOnly": True, "productionNativeSource": False, "layout": str(layout), "layoutSHA256": sha(layout), "nativeContextPastes": context_pastes}, "ownerGateAtPreparation": allocation_gate, "generationSubmitted": False, "requestedModelPreference": "free/included2.5 preferred; existing builtin2.0 allowed; no paid API", "actualModel": None}
    write_new(request_path, request)
    return {"request": str(request_path), "guide": str(guide_path), "nativeContexts": len(refs), "referencePaths": reference_paths, "ownerReady": request["ownerGateAtPreparation"]["ready"]}

def register(request_file, source):
    request = read(request_file)
    tile, patch = request["tile"], request["patch"]
    ack = gate(True, tile)
    p = spec(tile, patch)
    source = Path(source)
    with Image.open(source) as image:
        pixels, mode, fmt = list(image.size), image.mode, image.format
    destination = next_path(BATCH / tile / "native", patch, ".png")
    shutil.copyfile(source, destination)
    receipt = {"schemaVersion": 1, "createdAtUTC": now(), "tile": tile, "patch": patch, "file": str(destination), "sha256": sha(destination), "pixels": pixels, "mode": mode, "format": fmt, "hostOutputPath": str(source), "hostOutputSHA256": sha(source), "coordinates": p, "requestFile": str(request_file), "requestSHA256": sha(request_file), "route": "builtin_image_gen", "actualModel": None, "actualQuality": None, "modelEvidence": "Actual model/quality metadata not returned; not labeled2.5 or certified2.0", "resizedAfterGeneration": False, "nativeDimensionsMatchPlan": pixels == [1254, 1254], "usableGeometry": pixels == [1254, 1254] and mode in ("RGB", "RGBA"), "internalVisualReviewed": False, "formalAccepted": False, "ownerGate": ack}
    receipt.update(schemaVersion=3, quickVisualPassed=None, automaticallySelected=False,
                   selectionPolicy="Archive only. Explicit quick visual pass is required before selection or neighbor use.")
    write_new(destination.with_suffix(".png.generation.json"), receipt)
    return {"saved": str(destination), "pixels": pixels, "sha256": receipt["sha256"], "usableGeometry": receipt["usableGeometry"], "selected": False, "quickVisualPassed": None, "selectedCount": len(selected(tile))}

def select_source(tile, patch, source, quick_visual_passed=False):
    if quick_visual_passed is not True:
        raise RuntimeError("Selection requires explicit --quick-visual-passed after actual visual review; dimensions alone never qualify")
    coordinates = spec(tile, patch)
    allocation_gate = gate(True, tile)
    source = Path(source).resolve()
    if not source.is_relative_to((BATCH / tile / "native").resolve()):
        raise RuntimeError("Select only a registered original inside this tile's native directory")
    receipt_file = source.with_suffix(".png.generation.json")
    receipt = read(receipt_file)
    if (receipt.get("tile") != tile or receipt.get("patch") != patch
            or receipt.get("coordinates") != coordinates
            or Path(receipt.get("file", "")).resolve() != source
            or receipt.get("sha256") != sha(source)
            or receipt.get("usableGeometry") is not True):
        raise RuntimeError("Registered source provenance, coordinates or dimensions do not validate")
    with Image.open(source) as image:
        if image.size != (1254, 1254) or image.mode not in ("RGB", "RGBA"):
            raise RuntimeError("Registered source no longer has usable native geometry")
    review_file = next_path(BATCH / tile / "reviews", f"{patch}-quick-visual-pass")
    review = {"createdAtUTC": now(), "tile": tile, "patch": patch, "file": str(source),
              "sha256": sha(source), "generationReceipt": str(receipt_file),
              "generationReceiptSHA256": sha(receipt_file), "quickVisualPassed": True,
              "assertedBy": "Explicit operator --quick-visual-passed after actual layout and adjacent-boundary review",
              "internalTileQAComplete": False, "formalAccepted": False, "allocationGate": allocation_gate}
    write_new(review_file, review)
    current = selected(tile)
    current[patch] = {k: receipt[k] for k in ["tile", "patch", "file", "sha256", "pixels", "coordinates", "actualModel", "route"]}
    current[patch].update(quickVisualPassed=True, quickVisualReview=str(review_file), quickVisualReviewSHA256=sha(review_file))
    selection_file = next_path(BATCH / tile / "selection", "selection")
    write_new(selection_file, {"createdAtUTC": now(), "selected": current, "selectedCoreCount": len(current), "formalAccepted": False})
    return {"selected": str(source), "selectionFile": str(selection_file), "quickVisualPassed": True, "selectedCount": len(current), "formalAccepted": False}

def status():
    counts = {t: len(selected(t)) for t in sorted(TILES)}
    return {"ownerGate": gate(False), "selectedCoreCounts": counts, "selectedCoreCount": sum(counts.values()), "expectedCoreCount": 64, "completeSourceTiles": sum(c == 16 for c in counts.values()), "formalAcceptedCount": 0}

def assemble(tile):
    current = selected(tile)
    expected = {f"s{r:02d}_{c:02d}" for r in range(1, 5) for c in range(1, 5)}
    if set(current) != expected:
        raise RuntimeError("All16 native cores required; no placeholder assembly")
    canvas = Image.new("RGB", (4096, 4096))
    manifest = []
    for patch, item in sorted(current.items()):
        if sha(item["file"]) != item["sha256"]:
            raise RuntimeError("Selected source changed")
        p = spec(tile, patch)
        with Image.open(item["file"]) as image:
            if image.size != (1254, 1254):
                raise RuntimeError("Unexpected native dimensions")
            canvas.paste(image.convert("RGB").crop((115, 115, 1139, 1139)), p["corePasteXYInTile"])
        manifest.append(item)
    candidate = next_path(BATCH / tile / "candidate", f"{tile}-native-cores", ".png")
    canvas.save(candidate)
    write_new(candidate.with_suffix(".assembly.json"), {"createdAtUTC": now(), "tile": tile, "file": str(candidate), "sha256": sha(candidate), "pixels": [4096, 4096], "method": "Unresampled native1024 core crops pasted at exact coordinates; no blend, scale, inpaint or placeholder", "sources": manifest, "internalVisualReviewed": False, "formalAccepted": False, "singleGenerationNative4096": False, "finalArtUpscaled": False})
    qa = candidate.parent / (candidate.stem + "-qa-native100")
    qa.mkdir()
    crops = []
    for axis in ("x", "y"):
        for position in (1024, 2048, 3072):
            for segment in range(4):
                rectangle = [position-160, segment*1024, position+160, (segment+1)*1024] if axis == "x" else [segment*1024, position-160, (segment+1)*1024, position+160]
                file = qa / f"internal-{axis}{position}-segment{segment+1}.png"
                canvas.crop(rectangle).save(file)
                crops.append({"file": str(file), "sha256": sha(file), "cropLTRB": rectangle, "nativePixelScale": 1, "visualVerdict": "PENDING_ACTUAL_VIEW"})
    for x in (1024, 2048, 3072):
        for y in (1024, 2048, 3072):
            rectangle = [x-160, y-160, x+160, y+160]
            file = qa / f"junction-{x}-{y}.png"
            canvas.crop(rectangle).save(file)
            crops.append({"file": str(file), "sha256": sha(file), "cropLTRB": rectangle, "nativePixelScale": 1, "visualVerdict": "PENDING_ACTUAL_VIEW"})
    write_new(qa / "manifest.json", {"candidate": str(candidate), "candidateSHA256": sha(candidate), "crops": crops, "formalAccepted": False})
    return {"candidate": str(candidate), "sha256": sha(candidate), "native100Evidence": str(qa / "manifest.json"), "visualAcceptance": "not_granted"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["gate", "status", "prepare", "register", "select", "assemble"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--quick-visual-passed", action="store_true", help="Assert actual layout/adjacent-boundary visual review passed; required only for select")
    args = parser.parse_args()
    if args.action == "gate": result = gate(True, args.args[0] if args.args else None)
    elif args.action == "status": result = status()
    elif args.action == "prepare": result = prepare(*args.args)
    elif args.action == "register": result = register(*args.args)
    elif args.action == "select": result = select_source(*args.args, quick_visual_passed=args.quick_visual_passed)
    else: result = assemble(*args.args)
    print(json.dumps(result, ensure_ascii=False))
