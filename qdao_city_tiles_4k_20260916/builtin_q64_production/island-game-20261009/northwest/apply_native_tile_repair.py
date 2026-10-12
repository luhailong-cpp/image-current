"""Apply an explicitly chosen native repair/mask to a verified 4096 tile.

No mask generation, registration, resizing, blending or visual acceptance.
All paths are explicit. Relative CLI paths resolve against the current directory.
JSON reference paths resolve against the containing JSON's directory.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

import numpy as np
from PIL import Image
import historical_reference

ZONE = Path(__file__).resolve().parent
NATIVE = ZONE / "native"
SIZE, TILE, CORE, HALO = 1254, 4096, 1024, 115
ASSEMBLY_OPERATION = "mechanical 4x4 native-patch assembly"
REPAIR_OPERATION = "same-coordinate native repair over verified tile"
CONNECTED_PROJECTION_OPERATION = "same-coordinate projection of verified connected tile cluster"
CROSS_TILE_PROJECTION_OPERATION = "same-coordinate projection of one cross-tile native repair"


def require(value, message):
    if not value:
        raise ValueError(message)


def read_json(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(data, dict), f"Expected a JSON object: {path}")
    return data


def resolve(value, directory):
    require(isinstance(value, str) and bool(value.strip()), "An explicit path is required.")
    path = Path(value)
    return (path if path.is_absolute() else directory / path).resolve()


def file_info(path):
    require(path.is_file(), f"Missing required file: {path}")
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def pinned(value, directory, role):
    require(isinstance(value, dict), f"{role} must include path and sha256.")
    actual = file_info(resolve(value.get("path"), directory))
    expected = value.get("sha256")
    require(isinstance(expected, str) and re.fullmatch(r"[a-fA-F0-9]{64}", expected), f"Invalid hash: {role}")
    require(actual["sha256"] == expected.lower(), f"Hash mismatch: {role}")
    return actual


def read_pixels(path, size):
    with Image.open(path) as image:
        require(image.format == "PNG" and image.size == (size, size), f"Expected native {size}x{size} PNG: {path}")
        require(image.mode in ("RGB", "RGBA"), f"Unsupported pixel mode: {path}")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255, 255), f"Nonopaque source cannot be flattened: {path}")
        return np.asarray(image.convert("RGB")).copy()


def read_mask(path, require_selection=True):
    with Image.open(path) as image:
        require(image.format == "PNG" and image.mode == "L" and image.size == (SIZE, SIZE), "Mask must be an unscaled 1254x1254 grayscale L PNG.")
        mask = np.asarray(image).copy()
    require(set(np.unique(mask).tolist()).issubset({0, 255}), "Mask must contain only 0 and 255.")
    if require_selection:
        require(bool(np.any(mask == 255)), "Mask selects no repair pixels.")
    return mask


def tile_origin(tile_id):
    match = re.fullmatch(r"r(\d{2})_c(\d{2})", tile_id or "")
    require(match is not None, "tileId must use rNN_cNN.")
    row, col = map(int, match.groups())
    require(row > 0 and col > 0, "Tile coordinates are one-based.")
    return [(col - 1) * TILE, (row - 1) * TILE]


def validate_box(box):
    require(isinstance(box, (list, tuple)) and len(box) == 4 and all(type(v) is int for v in box), "cropBox must contain four integer coordinates.")
    x0, y0, x1, y1 = box
    require(0 <= x0 < x1 <= TILE and 0 <= y0 < y1 <= TILE and x1 - x0 == y1 - y0 == SIZE, "cropBox must be a 1254-square, fully inside the 4096 tile.")
    return list(box)


def load_raw(path, generation_path, pinned_metadata=None):
    """No subcell filename assumption: coordinates are proved by the edit input."""
    require(path.is_relative_to(NATIVE.resolve()), "Repair and original raw sources must remain in this zone's native/ directory.")
    image_info, gen_info = file_info(path), file_info(generation_path)
    generation = read_json(generation_path)
    require(generation.get("sha256") == image_info["sha256"], f"Generation source hash mismatch: {path}")
    require((generation.get("nativeWidth"), generation.get("nativeHeight")) == (SIZE, SIZE), f"Generation native dimensions mismatch: {path}")
    require(generation.get("route") == "builtin" and generation.get("tool") == "image_gen.imagegen", f"Source is not a recorded builtin native generation: {path}")
    require(generation.get("resizedAfterGeneration") is False and generation.get("finalArtUpscaled") is False, f"Source must affirm unscaled native pixels: {path}")
    if generation.get("file") is not None:
        require(resolve(generation["file"], generation_path.parent) == path, "Generation file path mismatch.")
    if generation.get("sourceOutputSha256") is not None:
        require(generation["sourceOutputSha256"] == image_info["sha256"], "Source output and native bytes differ.")
    prompt = file_info(resolve(generation.get("prompt"), generation_path.parent))
    require(prompt["sha256"] == generation.get("promptSha256"), "Generation prompt hash mismatch.")
    receipt_path = resolve(generation.get("evidence", {}).get("receipt"), generation_path.parent)
    receipt_info, receipt = file_info(receipt_path), read_json(receipt_path)
    require(receipt.get("route") == "builtin" and receipt.get("tool") == "image_gen.imagegen", "Receipt must confirm builtin image_gen.imagegen.")
    if receipt.get("submitted", {}).get("promptFile") is not None:
        require(resolve(receipt["submitted"]["promptFile"], receipt_path.parent) == Path(prompt["path"]), "Receipt prompt differs from generation prompt.")
    result = {**image_info, "generationRecord": gen_info, "prompt": prompt, "receipt": receipt_info, "dimensions": [SIZE, SIZE], "generationEvidence": {k: generation.get(k) for k in ("generatedAt", "tool", "route", "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "unverifiedReason", "resizedAfterGeneration", "finalArtUpscaled")}}
    if pinned_metadata is not None:
        for field in ("generationRecord", "prompt", "receipt"):
            item = pinned(pinned_metadata.get(field), generation_path.parent, f"recorded raw {field}")
            require(item == result[field], f"Recorded {field} no longer matches raw evidence.")
        require(pinned_metadata.get("sha256") == result["sha256"], "Recorded original raw hash mismatch.")
    return read_pixels(path, SIZE), result, generation


def assembly_source(source, directory, expected_box, source_id, cell_stem, archived_mask=None):
    image_info = pinned(source, directory, f"assembly source {source_id}")
    path = Path(image_info["path"])
    require(source.get("sourceId") == source_id and source.get("globalNativeBox") == expected_box, "Assembly source coordinates/ID mismatch.")
    if source.get("kind") == "rawNative":
        require(re.fullmatch(fr"{cell_stem}_a\d+\.png", path.name) is not None, "Assembly raw filename does not match its tile/subcell.")
        gen = pinned(source.get("generationRecord"), directory, "raw generation record")
        array, _, _ = load_raw(path, Path(gen["path"]), source)
        return array, 1
    require(source.get("kind") == "nativeComposite", "Unsupported assembly source kind.")
    require(path.is_relative_to(ZONE) and not path.is_relative_to(NATIVE), "Composite cannot masquerade as raw native.")
    pinned(source.get("nativeCompositeRecord"), directory, "native composite record")
    composite = source.get("nativeComposite", {})
    leaves = composite.get("sources")
    require(isinstance(leaves, list) and len(leaves) == 2, "Assembly composite must contain exactly two raw sources.")
    mask_info = pinned(composite.get("mask"), directory, "native composite mask")
    mask = read_mask(Path(mask_info["path"]))
    require(set(np.unique(mask).tolist()) == {0, 255}, "Assembly composite requires both raw sources.")
    require(archived_mask is not None and np.array_equal(archived_mask, mask), "Archived composite provenance mask differs from its recorded source mask.")
    array = read_pixels(path, SIZE)
    raw_paths = set()
    for index, leaf in enumerate(leaves):
        raw_info = pinned(leaf, directory, "composite original raw")
        require(raw_info["path"] not in raw_paths and leaf.get("kind") == "rawNative" and leaf.get("compositeSourceId") == index and leaf.get("maskValue") == index * 255, "Composite leaves must be distinct raw sources 0/1.")
        raw_paths.add(raw_info["path"])
        require(re.fullmatch(fr"{cell_stem}_a\d+\.png", Path(raw_info["path"]).name) is not None, "Composite original filename does not match its tile/subcell.")
        require(leaf.get("globalNativeBox") == expected_box, "Composite original global coordinates differ.")
        coordinate_info = pinned(leaf.get("coordinateInput"), directory, "original coordinate input")
        require(read_json(Path(coordinate_info["path"])).get("globalBox") == expected_box, "Original coordinate input does not match the global native frame.")
        gen = pinned(leaf.get("generationRecord"), directory, "composite original generation record")
        raw, _, _ = load_raw(Path(raw_info["path"]), Path(gen["path"]), leaf)
        selected = mask == index * 255
        require(np.array_equal(array[selected], raw[selected]), "Composite contains a pixel absent from the selected raw source at that coordinate.")
    return array, 2


def validate_assembly(pixels, record, record_path):
    require(record.get("schemaVersion") == 1 and record.get("isAiGeneration") is False, "Unsupported assembly record.")
    assertions = record.get("coverageAssertions", {})
    require(assertions.get("fullNativeCoverage") is True and assertions.get("tilePixelCount") == TILE * TILE and assertions.get("sourceContributionSum") == TILE * TILE and assertions.get("unassignedPixels") == 0 and assertions.get("guidePixelsUsed") is False, "Base assembly lacks complete native-coverage assertions.")
    method = record.get("method", {})
    for key in ("registration", "resizingFinalArt", "feathering", "colorCorrection", "drawingOrPixelSynthesis"):
        require(method.get(key) is False, f"Base assembly must forbid {key}.")
    manifest = pinned(record.get("manifest"), record_path.parent, "assembly manifest")
    require(read_json(Path(manifest["path"])) == record.get("manifestSnapshot"), "Assembly manifest snapshot mismatch.")
    provenance = pinned(record.get("provenance"), record_path.parent, "assembly source-index archive")
    sources = record.get("sources")
    require(isinstance(sources, list) and len(sources) == 16, "Base assembly must declare all 16 input cells.")
    origin = tile_origin(record.get("tileId"))
    native_count, contributions = 0, []
    with np.load(provenance["path"], allow_pickle=False) as archive:
        ids = archive["tile_source_id"]
        require(ids.shape == (TILE, TILE) and ids.dtype == np.uint8 and bool(np.all(ids < 16)), "Invalid or incomplete tile source-index plane.")
        expected_origins = np.array([[i % 4 * CORE, i // 4 * CORE] for i in range(16)], dtype=np.int32)
        require(np.array_equal(archive["padded_source_origins"], expected_origins), "Source-index origins do not match the assembly grid.")
        for index, source in enumerate(sources):
            row, col = divmod(index, 4)
            x = origin[0] + col * CORE - HALO
            y = origin[1] + row * CORE - HALO
            expected_box = [x, y, x + SIZE, y + SIZE]
            require(source.get("paddedOrigin") == [col * CORE, row * CORE], "Recorded source padded origin mismatch.")
            archived_mask = archive[f"composite_source_{index:02d}_native_mask"] if source.get("kind") == "nativeComposite" else None
            cell_stem = f"{record['tileId']}_s{row + 1:02d}_{col + 1:02d}"
            raw, count = assembly_source(source, record_path.parent, expected_box, index, cell_stem, archived_mask)
            native_count += count
            ys, xs = np.nonzero(ids == index)
            require(xs.size > 0, f"Base assembly cell {index} has no contribution.")
            sx, sy = xs + HALO - col * CORE, ys + HALO - row * CORE
            require(int(sx.min()) >= 0 and int(sy.min()) >= 0 and int(sx.max()) < SIZE and int(sy.max()) < SIZE, "Assembly source is used outside its native coordinates.")
            require(np.array_equal(pixels[ys, xs], raw[sy, sx]), f"Base pixels differ from native provenance at cell {index}.")
            contributions.append({"sourceId": index, "pixelCount": int(xs.size)})
    require(sum(c["pixelCount"] for c in contributions) == TILE * TILE, "Recomputed base coverage is incomplete.")
    recorded_counts = {c["sourceId"]: c["pixelCount"] for c in record.get("tileContributions", [])}
    require(recorded_counts == {c["sourceId"]: c["pixelCount"] for c in contributions}, "Assembly contribution counts do not match its source-index plane.")
    return {"tileId": record["tileId"], "tileOrigin": origin, "fullNativeCoverage": True, "verifiedPixelCount": TILE * TILE, "originalRawSourceCount": native_count, "rootAssembly": file_info(record_path), "rootProvenance": provenance, "originalCellContributions": contributions, "priorRepairCount": 0}


def verified_ancestor_chain(base_info, base_record_info, ancestor_image, ancestor_record):
    """Only explicit parent links qualify; a matching unrelated image does not."""
    current_image, current_record = base_info, base_record_info
    seen, chain = set(), []
    for _ in range(32):
        path = Path(current_record["path"])
        require(path not in seen, "Cycle in crop ancestor chain.")
        seen.add(path)
        require(pinned(current_record, path.parent, "ancestor-chain record") == current_record, "Ancestor record changed.")
        record = read_json(path)
        require(pinned(record.get("output"), path.parent, "ancestor-chain image") == current_image, "Ancestor-chain output identity mismatch.")
        chain.append({"image": current_image, "record": current_record})
        if current_image == ancestor_image and current_record == ancestor_record:
            return chain
        require(record.get("operation") in (REPAIR_OPERATION, CONNECTED_PROJECTION_OPERATION, CROSS_TILE_PROJECTION_OPERATION), "Edit crop source is not in the current base's recorded ancestry.")
        current_image = pinned(record.get("base", {}).get("image"), path.parent, "ancestor parent image")
        current_record = pinned(record.get("base", {}).get("record"), path.parent, "ancestor parent record")
    raise ValueError("Excessive crop ancestry depth.")


def compare_application_crop(crop, application_crop, mask=None):
    """An ancestor edit may only select coordinates unchanged in the current base."""
    require(crop.shape == application_crop.shape == (SIZE, SIZE, 3), "Application crop dimensions differ.")
    differences = np.any(crop != application_crop, axis=2)
    if mask is None:
        selected = np.ones((SIZE, SIZE), dtype=bool)
        mode = "strict_full_crop"
    else:
        require(mask.shape == (SIZE, SIZE) and mask.dtype == np.uint8 and set(np.unique(mask).tolist()).issubset({0, 255}), "Application comparison requires an explicit native binary mask.")
        selected = mask == 255
        require(bool(selected.any()), "Application comparison mask selects no pixels.")
        mode = "explicit_mask_selected_pixels"
    changed_selected = int(np.count_nonzero(differences & selected))
    if mask is None:
        require(changed_selected == 0, "Edit-target pixels do not equal the exact base crop.")
    else:
        require(changed_selected == 0, f"Selected edit-target pixels differ from current application base ({changed_selected} pixel(s)); ancestor repair would overlap a later change.")
    changed = int(np.count_nonzero(differences))
    return {"mode": mode, "cropPixelCount": SIZE * SIZE, "selectedPixelCount": int(np.count_nonzero(selected)), "differentPixelCount": changed, "differentSelectedPixelCount": changed_selected, "differentUnselectedPixelCount": int(np.count_nonzero(differences & ~selected)), "allDifferencesOutsideSelection": changed_selected == 0, "selectedPixelsExactlyMatchEditTarget": True, "differenceMaskPackedSha256": hashlib.sha256(np.packbits(differences).tobytes()).hexdigest(), "differenceMaskEncoding": "row-major pixel inequality, any RGB channel differs; numpy.packbits default big-bit order"}


def validate_edit_target(base_pixels, base_info, base_record_info, tile_id, box, input_path, mask=None, historical_generation=None):
    data = read_json(input_path)
    origin = tile_origin(tile_id)
    global_box = [box[0] + origin[0], box[1] + origin[1], box[2] + origin[0], box[3] + origin[1]]
    require(data.get("globalBox") == global_box, "Repair input globalBox must equal tile origin + cropBox.")
    if data.get("tileCropBox") is not None:
        require(data["tileCropBox"] == box, "Input tileCropBox differs from CLI cropBox.")
    if data.get("nativeSize") is not None:
        require(data["nativeSize"] == [SIZE, SIZE], "Input nativeSize must be 1254 square.")
    if data.get("tileId") is not None:
        require(data["tileId"] == tile_id, "Repair input tileId mismatch.")
    target = pinned(data.get("editTarget"), input_path.parent, "repair edit-target crop")
    derivation_info = pinned(data["editTarget"].get("derivationRecord"), input_path.parent, "edit-target derivation record")
    derivation = read_json(Path(derivation_info["path"]))
    require(derivation.get("operation") == "native-coordinate crop" and derivation.get("cropBox") == box, "Edit-target derivation must be the exact declared native-coordinate crop.")
    for flag in ("resizing", "registration", "feathering", "colorCorrection"):
        require(derivation.get(flag) is False, f"Edit-target crop must forbid {flag}.")
    if derivation.get("output") is not None:
        require(pinned(derivation["output"], Path(derivation_info["path"]).parent, "crop derivation output") == target, "Crop derivation identifies a different output.")
    ancestor = derivation.get("derivedFrom")
    require(isinstance(ancestor, dict), "Edit-target derivedFrom must identify one exact base tile.")
    parent_image = pinned(ancestor, Path(derivation_info["path"]).parent, "crop's base tile")
    parent_record = pinned(ancestor.get("assemblyRecord"), Path(derivation_info["path"]).parent, "crop's base provenance record")
    crop = read_pixels(Path(target["path"]), SIZE)
    x0, y0, x1, y1 = box
    ancestor_reuse = parent_image != base_info or parent_record != base_record_info
    chain = verified_ancestor_chain(base_info, base_record_info, parent_image, parent_record)
    ancestor_pixels = base_pixels
    if ancestor_reuse:
        ancestor_pixels, ancestor_proof = validate_base(Path(parent_image["path"]), Path(parent_record["path"]))
        require(ancestor_proof["tileId"] == tile_id, "Crop ancestor belongs to another tile.")
    require(np.array_equal(crop, ancestor_pixels[y0:y1, x0:x1]), "Edit target does not equal its recorded ancestor crop.")
    comparison = compare_application_crop(crop, base_pixels[y0:y1, x0:x1], mask)
    declared = data.get("inputs")
    require(isinstance(declared, list) and 1 <= len(declared) <= 5, "Repair input must declare its actual 1..5 image references.")
    refs = [historical_reference.reference(item, input_path.parent, historical_generation)[0] for item in declared]
    require(refs[0] == target, "First submitted input must be the exact base crop edit target.")
    return {"input": file_info(input_path), "editTarget": target, "cropDerivation": derivation_info, "globalBox": global_box, "references": refs, "cropSourceBase": {"image": parent_image, "record": parent_record}, "applicationBase": {"image": base_info, "record": base_record_info}, "ancestorCropReuse": ancestor_reuse, "cropExactlyMatchesRecordedSource": True, "cropExactlyMatchesSourceAndApplicationBase": comparison["differentPixelCount"] == 0, "applicationCropComparison": comparison, "verifiedBaseRecordChainToCropSource": chain}


def validate_crop_input(base_pixels, base_info, base_record_info, tile_id, box, input_path, generation, generation_directory, mask=None):
    result = validate_edit_target(base_pixels, base_info, base_record_info, tile_id, box, input_path, mask, generation)
    generated = generation.get("references")
    require(isinstance(generated, list) and len(generated) == len(result["references"]), "Repair generation must use the actual declared input list.")
    for index, (expected, item) in enumerate(zip(result["references"], generated)):
        require(historical_reference.reference(item, generation_directory, generation)[0] == expected, "Generation and input reference lists differ.")
    result['referenceAvailability'] = historical_reference.evidence(generation, generation_directory)
    return result


def validate_repair_source(base_pixels, base_info, base_record_info, tile_id, box, source_path, generation_path, input_path, mask=None):
    repair, source, generation = load_raw(source_path, generation_path)
    source.update(validate_crop_input(base_pixels, base_info, base_record_info, tile_id, box, input_path, generation, generation_path.parent, mask))
    return repair, source


def compose_pixels(base, repair, box, mask):
    validate_box(box)
    require(base.shape == (TILE, TILE, 3) and repair.shape == (SIZE, SIZE, 3) and mask.shape == (SIZE, SIZE), "Pixel dimensions do not match the repair contract.")
    require(base.dtype == repair.dtype == mask.dtype == np.uint8 and set(np.unique(mask).tolist()).issubset({0, 255}) and bool(np.any(mask == 255)), "Composition requires uint8 source pixels and explicit binary selection.")
    result = base.copy()
    x0, y0, x1, y1 = box
    selected = mask == 255
    result[y0:y1, x0:x1][selected] = repair[selected]
    # Independently assert the full preservation boundary and both interior cases.
    for current, original in ((result[:y0], base[:y0]), (result[y1:], base[y1:]), (result[y0:y1, :x0], base[y0:y1, :x0]), (result[y0:y1, x1:], base[y0:y1, x1:])):
        require(np.array_equal(current, original), "A pixel outside cropBox changed.")
    require(np.array_equal(result[y0:y1, x0:x1][~selected], base[y0:y1, x0:x1][~selected]), "A mask-zero base pixel changed.")
    require(np.array_equal(result[y0:y1, x0:x1][selected], repair[selected]), "A selected pixel differs from the same repair coordinate.")
    return result


def validate_base(image_path, record_path, seen=None):
    image_path, record_path = Path(image_path).resolve(), Path(record_path).resolve()
    seen = set() if seen is None else set(seen)
    require(record_path not in seen and len(seen) < 32, "Cyclic or excessive repair provenance chain.")
    seen.add(record_path)
    require(image_path.is_relative_to(ZONE) and record_path.is_relative_to(ZONE), "Base art and provenance must remain in this zone.")
    record = read_json(record_path)
    output = pinned(record.get("output"), record_path.parent, "base output")
    require(Path(output["path"]) == image_path and record["output"].get("dimensions") == [TILE, TILE], "Base record does not identify the supplied 4096 image.")
    pixels = read_pixels(image_path, TILE)
    if record.get("operation") == ASSEMBLY_OPERATION:
        return pixels, validate_assembly(pixels, record, record_path)
    if record.get("operation") == CONNECTED_PROJECTION_OPERATION:
        # The connected assembler itself imports this module. Defer this edge
        # until validation so both CLI entry points remain independently usable.
        import assemble_connected_tiles as connected
        return pixels, connected.validate_projection(pixels, record, record_path, seen)
    if record.get("operation") == CROSS_TILE_PROJECTION_OPERATION:
        import cross_tile_native_repair as cross
        return pixels, cross.validate_projection(pixels, record, record_path, seen)
    require(record.get("operation") == REPAIR_OPERATION and record.get("schemaVersion") == 1 and record.get("isAiGeneration") is False, "Unsupported base provenance operation.")
    for key in ("registration", "resizing", "feathering", "colorCorrection", "pixelSynthesis"):
        require(record.get("method", {}).get(key) is False, f"Prior repair must forbid {key}.")
    parent_image = pinned(record.get("base", {}).get("image"), record_path.parent, "prior repair base")
    parent_record = pinned(record.get("base", {}).get("record"), record_path.parent, "prior repair base record")
    parent, proof = validate_base(Path(parent_image["path"]), Path(parent_record["path"]), seen)
    require(record.get("tileId") == proof["tileId"], "Prior repair changed tile identity.")
    box = validate_box(record.get("cropBox"))
    source = record.get("repairSource", {})
    raw_info = pinned(source, record_path.parent, "prior raw repair")
    gen_info = pinned(source.get("generationRecord"), record_path.parent, "prior repair generation")
    input_info = pinned(source.get("input"), record_path.parent, "prior repair input")
    mask_info = pinned(record.get("mask"), record_path.parent, "prior explicit mask")
    mask = read_mask(Path(mask_info["path"]))
    repair, verified = validate_repair_source(parent, parent_image, parent_record, proof["tileId"], box, Path(raw_info["path"]), Path(gen_info["path"]), Path(input_info["path"]), mask)
    for key in ("prompt", "receipt", "editTarget", "cropDerivation"):
        require(pinned(source.get(key), record_path.parent, f"prior repair {key}") == verified[key], f"Prior repair {key} changed.")
    require(source.get("globalBox") == verified["globalBox"], "Prior repair source global coordinates differ from its input.")
    require(np.array_equal(pixels, compose_pixels(parent, repair, box, mask)), "Prior repaired tile differs from its exact source selection.")
    require(record.get("coverageAssertions", {}).get("fullNativeCoverage") is True, "Prior repair lacks full native coverage.")
    reference_evidence = proof.get('repairReferenceAvailability', []) + [verified['referenceAvailability']]
    proof = {**proof, "priorRepairCount": proof["priorRepairCount"] + 1,
             'repairReferenceAvailability': reference_evidence,
             'fullRepairReferenceAvailability': all(item['fullReferenceAvailability'] for item in reference_evidence)}
    return pixels, proof


def selection_record(mask, box, origin):
    ys, xs = np.nonzero(mask == 255)
    local = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    tile = [local[0] + box[0], local[1] + box[1], local[2] + box[0], local[3] + box[1]]
    return {"repairPixelCount": int(xs.size), "retainedBasePixelCount": TILE * TILE - int(xs.size), "repairLocalBoundingBoxHalfOpen": local, "tileBoundingBoxHalfOpen": tile, "globalBoundingBoxHalfOpen": [tile[0] + origin[0], tile[1] + origin[1], tile[2] + origin[0], tile[3] + origin[1]], "boundsContainOnlySelectedPixels": False, "exactSelectedPositions": "mask(x,y)==255 selects repair(x,y) at tile(x+cropBox[0],y+cropBox[1]); all other tile positions use the verified base unchanged"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "base-record", "source", "generation-record", "input", "mask", "output"):
        parser.add_argument("--" + name, required=name in ("base", "base-record"))
    parser.add_argument("--crop-box", nargs=4, type=int, metavar=("X0", "Y0", "X1", "Y1"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--validate-only", action="store_true", help="Verify all inputs and the in-memory result without writing art or records.")
    mode.add_argument("--validate-base-only", action="store_true", help="Revalidate existing tile coverage/provenance without a repair source or mask.")
    mode.add_argument("--validate-crop-only", action="store_true", help="Revalidate base and exact edit crop before generation; requires --input and --crop-box.")
    args = parser.parse_args()
    cwd = Path.cwd()
    base_path, record_path = resolve(args.base, cwd), resolve(args.base_record, cwd)
    base, proof = validate_base(base_path, record_path)
    if args.validate_base_only:
        print(json.dumps({"status": "base_native_coverage_reverified", "base": file_info(base_path), "proof": proof, "visualAcceptance": False}, ensure_ascii=False, indent=2))
        return
    if args.validate_crop_only:
        require(args.input is not None and args.crop_box is not None, "Crop preflight requires --input and --crop-box.")
        box = validate_box(args.crop_box)
        crop = validate_edit_target(base, file_info(base_path), file_info(record_path), proof["tileId"], box, resolve(args.input, cwd))
        print(json.dumps({"status": "native_edit_crop_verified_before_generation", "baseProof": proof, "editCrop": crop, "rawRepairVerified": False, "visualAcceptance": False}, ensure_ascii=False, indent=2))
        return
    for field in ("source", "generation_record", "input", "mask", "crop_box"):
        require(getattr(args, field) is not None, f"--{field.replace('_', '-')} is required for a repair.")
    require(args.validate_only or args.output is not None, "--output is required unless --validate-only is used.")
    box = validate_box(args.crop_box)
    base_info, base_record_info = file_info(base_path), file_info(record_path)
    mask_path = resolve(args.mask, cwd)
    mask_info, mask = file_info(mask_path), read_mask(mask_path)
    repair, source = validate_repair_source(base, base_info, base_record_info, proof["tileId"], box, resolve(args.source, cwd), resolve(args.generation_record, cwd), resolve(args.input, cwd), mask)
    result = compose_pixels(base, repair, box, mask)
    selection = selection_record(mask, box, proof["tileOrigin"])
    if args.validate_only:
        print(json.dumps({"status": "all_native_repair_inputs_verified_no_output", "baseProof": proof, "selection": selection, "editTargetCompatibility": {key: source[key] for key in ("cropSourceBase", "applicationBase", "ancestorCropReuse", "cropExactlyMatchesRecordedSource", "cropExactlyMatchesSourceAndApplicationBase", "applicationCropComparison", "verifiedBaseRecordChainToCropSource")}, "visualAcceptance": False}, ensure_ascii=False, indent=2))
        return
    output_path = resolve(args.output, cwd)
    require(output_path.is_relative_to(ZONE) and not output_path.is_relative_to(NATIVE) and output_path.suffix.lower() == ".png", "Output must be a PNG inside this zone, outside native/.")
    output_record = output_path.with_suffix(".native-repair.json")
    require(not output_path.exists() and not output_record.exists(), "Output version already exists; never overwrite art or provenance.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("xb") as handle:
        Image.fromarray(result).save(handle, format="PNG")
    record = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(), "operation": REPAIR_OPERATION, "isAiGeneration": False, "status": "candidate_pending_native_visual_and_boundary_review", "tool": file_info(Path(__file__).resolve()), "tileId": proof["tileId"], "tileOrigin": proof["tileOrigin"], "base": {"image": base_info, "record": base_record_info, "reverifiedProvenance": proof}, "repairSource": source, "cropBox": box, "mask": {**mask_info, "dimensions": [SIZE, SIZE], "valueMeaning": "0=retain base;255=copy repair at identical crop-local coordinates"}, "selection": selection, "output": {**file_info(output_path), "dimensions": [TILE, TILE]}, "method": {"registration": False, "resizing": False, "feathering": False, "colorCorrection": False, "pixelSynthesis": False, "maskWasGeneratedByThisTool": False, "coordinateRule": "repair local(x,y) maps to tile(x+cropBox[0],y+cropBox[1]) and global(tile x+tileOrigin[0],tile y+tileOrigin[1]); no offset beyond that declared crop origin"}, "coverageAssertions": {"fullNativeCoverage": True, "tilePixelCount": TILE * TILE, "allOutputPixelsExactlyMatchUnchangedBaseOrRawRepairAtDeclaredCoordinates": True, "baseCoverageRecomputedFromOriginalNatives": True, "editTargetExactlyEqualsBaseCrop": source["cropExactlyMatchesSourceAndApplicationBase"], "editTargetExactlyEqualsRecordedAncestorCrop": source["cropExactlyMatchesRecordedSource"], "selectedEditTargetPixelsExactlyEqualApplicationBase": source["applicationCropComparison"]["selectedPixelsExactlyMatchEditTarget"], "applicationBaseDifferencesConfinedOutsideMask": source["applicationCropComparison"]["allDifferencesOutsideSelection"], "guidePixelsUsedAsFinalArt": False, "unassignedPixels": 0}, "formalAcceptedCount": 0, "limits": ["Mask topology, object geometry, boundary continuity and material matching require independent native-scale visual review.", "This mechanical tool does not accept the image, choose a mask, repaint pixels, alter progress or run a tile assembler.", "The original source-index archive, prior repair records/masks and raw generation evidence remain necessary to reconstruct nested provenance.", "Actual model/quality are only as disclosed in the raw generation record; this operation is not a new AI generation."]}
    with output_record.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"status": record["status"], "output": record["output"], "record": file_info(output_record), "selection": selection, "visualAcceptance": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "failed", "error": str(error), "candidateAccepted": False}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
