"""Assemble explicitly selected native patches. No generation or geometric repair.

Manifest schema (paths are absolute or relative to the manifest directory):
{"schemaVersion": 1, "tileId": "r03_c03", "nativePixels": 1254,
 "corePixels": 1024, "haloPixels": 115,
 "patchMatrix": [[{"path": "...png", "generationRecord": "...json",
                   "sha256": "optional pinned source hash"}, ...], ...]}
patchMatrix MUST contain four rows of four explicit objects. No file discovery.
For a verified two-native-source composition, replace generationRecord with
nativeCompositeRecord, an explicit path to its pinned-source/mask record.
Output is a candidate requiring native-scale visual and external-edge review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


ZONE = Path(__file__).resolve().parent
NATIVE = ZONE / "native"
SIZE, CORE, HALO, OVERLAP = 1254, 1024, 115, 230
PADDED, TILE, UNSET = 4326, 4096, 255


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_from(value: str, base: Path) -> Path:
    require(isinstance(value, str) and bool(value.strip()), "An explicit nonempty path is required.")
    path = Path(value)
    return (path if path.is_absolute() else base / path).resolve()


def writable(path: Path) -> Path:
    path = path.resolve()
    require(path.is_relative_to(ZONE), f"Write outside zone forbidden: {path}")
    return path


def file_record(path: Path) -> dict:
    require(path.is_file(), f"Missing required file: {path}")
    return {"path": str(path), "sha256": digest(path)}


def save_json(path: Path, value: dict) -> dict:
    path = writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    return file_record(path)


def save_image(path: Path, image: Image.Image) -> dict:
    path = writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        image.save(handle, format="PNG")
    return {**file_record(path), "dimensions": list(image.size)}


def check_hash(actual: str, expected: str, role: str) -> None:
    require(isinstance(expected, str) and re.fullmatch(r"[a-fA-F0-9]{64}", expected) is not None, f"Invalid SHA256 for {role}.")
    require(actual == expected.lower(), f"Hash mismatch for {role}.")


def native_box(tile_id: str, row: int, col: int) -> list:
    match = re.fullmatch(r"r(\d{2})_c(\d{2})", tile_id)
    require(match is not None, "tileId must use rNN_cNN.")
    tile_row, tile_col = map(int, match.groups())
    require(tile_row > 0 and tile_col > 0, "Tile coordinates are one-based.")
    x = (tile_col - 1) * TILE + col * CORE - HALO
    y = (tile_row - 1) * TILE + row * CORE - HALO
    return [x, y, x + SIZE, y + SIZE]


def read_native_pixels(path: Path) -> tuple[np.ndarray, dict]:
    with Image.open(path) as image:
        require(image.size == (SIZE, SIZE), f"Measured native size must be {SIZE} square: {path}: {image.size}")
        require(image.format == "PNG", f"Source must actually be PNG: {path}")
        require(image.mode in ("RGB", "RGBA"), f"Unsupported source mode: {path}: {image.mode}")
        if image.mode == "RGBA":
            require(image.getextrema()[3] == (255, 255), f"Nonopaque alpha source cannot be flattened: {path}")
        return np.asarray(image.convert("RGB")).copy(), {"dimensions": list(image.size), "originalMode": image.mode}


def load_raw_source(source_path: Path, generation_path: Path, tile_id: str, row: int, col: int,
                    pinned_hash: str | None = None, generation_hash: str | None = None) -> tuple[dict, np.ndarray]:
    """The sole raw-input gate, also used for both leaves of a composite."""
    require(source_path.is_relative_to(NATIVE.resolve()), f"Raw pixels must come from this zone's native directory: {source_path}")
    require(re.fullmatch(fr"{tile_id}_s{row + 1:02d}_{col + 1:02d}_a\d+\.png", source_path.name) is not None, f"Source filename does not match its declared tile/subcell: {source_path.name}")
    source = file_record(source_path)
    if pinned_hash is not None:
        check_hash(source["sha256"], pinned_hash, f"native source {source_path}")
    generation_file = file_record(generation_path)
    if generation_hash is not None:
        check_hash(generation_file["sha256"], generation_hash, f"generation record {generation_path}")
    generation = json.loads(generation_path.read_text(encoding="utf-8-sig"))
    require(generation.get("sha256") == source["sha256"], f"Generation record source hash mismatch: {source_path}")
    require((generation.get("nativeWidth"), generation.get("nativeHeight")) == (SIZE, SIZE), f"Generation record native dimensions mismatch: {source_path}")
    require(generation.get("route") == "builtin", f"Generation source is not recorded as builtin: {source_path}")
    require(generation.get("resizedAfterGeneration") is False and generation.get("finalArtUpscaled") is False, f"Source record does not affirm unscaled native art: {source_path}")
    prompt = file_record(resolve_from(generation.get("prompt"), generation_path.parent))
    require(prompt["sha256"] == generation.get("promptSha256"), f"Prompt hash mismatch: {source_path}")
    receipt_path = resolve_from(generation.get("evidence", {}).get("receipt"), generation_path.parent)
    receipt = file_record(receipt_path)
    receipt_data = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    require(receipt_data.get("route") == "builtin" and receipt_data.get("tool") == generation.get("tool") == "image_gen.imagegen", f"Receipt route/tool does not match builtin generation: {source_path}")
    submitted_prompt = receipt_data.get("submitted", {}).get("promptFile")
    if submitted_prompt is not None:
        require(resolve_from(submitted_prompt, receipt_path.parent) == Path(prompt["path"]), f"Receipt prompt path mismatch: {source_path}")
    array, dimensions = read_native_pixels(source_path)
    source.update({
        **dimensions, "kind": "rawNative", "globalNativeBox": native_box(tile_id, row, col),
        "generationRecord": generation_file,
        "generationEvidence": {key: generation.get(key) for key in ("generatedAt", "tool", "route", "configSnapshot", "submittedParameters", "actualModel", "actualQuality", "unverifiedReason", "resizedAfterGeneration", "finalArtUpscaled", "status")},
        "prompt": prompt, "receipt": receipt,
    })
    return source, array


def pinned_record(value: dict, base: Path, role: str) -> dict:
    require(isinstance(value, dict), f"{role} must contain an explicit path and sha256.")
    record = file_record(resolve_from(value.get("path"), base))
    check_hash(record["sha256"], value.get("sha256"), role)
    return record


def read_binary_mask(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        require(image.format == "PNG" and image.mode == "L" and image.size == (SIZE, SIZE), "Composite mask must be a native-size grayscale L PNG.")
        mask = np.asarray(image).copy()
    require(set(np.unique(mask).tolist()) == {0, 255}, "Composite mask must contain only 0 and 255, with both raw sources used.")
    return mask


def load_composite(source_path: Path, record_path: Path, tile_id: str, row: int, col: int,
                   pinned_hash: str | None = None) -> tuple[dict, np.ndarray]:
    """Accept exactly two raw natives at identical local/global coordinates."""
    require(source_path.is_relative_to(ZONE) and not source_path.is_relative_to(NATIVE.resolve()), "A mechanical composite must remain in this zone, outside raw native/.")
    require(record_path.is_relative_to(ZONE), "Composite record must remain inside this zone.")
    source, record_file = file_record(source_path), file_record(record_path)
    if pinned_hash is not None:
        check_hash(source["sha256"], pinned_hash, "manifest composite")
    record = json.loads(record_path.read_text(encoding="utf-8-sig"))
    require(record.get("schemaVersion") == 1 and record.get("isAiGeneration") is False and record.get("rawNative") is False, "Composite must explicitly declare schema 1, isAiGeneration=false and rawNative=false.")
    for key in ("registration", "resizing", "feathering", "colorCorrection", "pixelSynthesis"):
        require(record.get(key) is False, f"Composite must explicitly forbid {key}.")
    expected_box = native_box(tile_id, row, col)
    coordinates = record.get("coordinateSystem", {})
    require(coordinates.get("sameGlobalNativeBox") == expected_box and coordinates.get("nativeSize") == [SIZE, SIZE], "Composite global/native coordinates do not match the manifest cell.")
    candidate = pinned_record(record.get("outputs", {}).get("candidate"), record_path.parent, "composite candidate")
    require(Path(candidate["path"]) == source_path and candidate["sha256"] == source["sha256"], "Composite record names a different candidate.")
    mask_file = pinned_record(record.get("outputs", {}).get("mask"), record_path.parent, "composite mask")
    require(Path(mask_file["path"]).is_relative_to(ZONE), "Composite mask must remain in this zone.")
    mask = read_binary_mask(Path(mask_file["path"]))
    leaves = record.get("sources")
    require(isinstance(leaves, list) and len(leaves) == 2, "Composite requires exactly two original raw native sources; recursive composites are forbidden.")
    raw_sources, raw_arrays, seen = [], [], set()
    for index, leaf in enumerate(leaves):
        require(isinstance(leaf, dict) and leaf.get("sourceId") == index and "nativeCompositeRecord" not in leaf, "Composite leaves must be raw sourceIds 0,1 in order.")
        raw_path = resolve_from(leaf.get("path"), record_path.parent)
        require(raw_path not in seen, "Composite raw source paths must be distinct.")
        seen.add(raw_path)
        check_hash(digest(raw_path), leaf.get("sha256"), f"composite leaf {index}")
        require(leaf.get("nativeSize") == [SIZE, SIZE], "Composite leaf must declare nativeSize1254 square.")
        gen_file = pinned_record(leaf.get("generationRecord"), record_path.parent, f"composite leaf {index} generation record")
        raw, array = load_raw_source(raw_path, Path(gen_file["path"]), tile_id, row, col, leaf["sha256"], gen_file["sha256"])
        # Exact attempt only. No fallback to another version or latest-file lookup.
        coordinate_path = ZONE / "guides" / f"{raw_path.stem}.input.json"
        coordinate_file = file_record(coordinate_path)
        coordinate_input = json.loads(coordinate_path.read_text(encoding="utf-8-sig"))
        require(coordinate_input.get("globalBox") == expected_box, f"Composite leaf coordinate input mismatch: {raw_path}")
        require(coordinate_input.get("coreBox") == [expected_box[0] + HALO, expected_box[1] + HALO, expected_box[0] + HALO + CORE, expected_box[1] + HALO + CORE], f"Composite leaf core coordinates mismatch: {raw_path}")
        raw.update({"compositeSourceId": index, "maskValue": index * 255, "coordinateInput": coordinate_file, "nativeInputPixelCount": int(np.count_nonzero(mask == index * 255))})
        raw_sources.append(raw)
        raw_arrays.append(array)
    array, dimensions = read_native_pixels(source_path)
    for index in range(2):
        selected = mask == index * 255
        require(np.array_equal(array[selected], raw_arrays[index][selected]), f"Composite pixels differ from raw source {index} at identical coordinates.")
    source.update({
        **dimensions, "kind": "nativeComposite", "globalNativeBox": expected_box,
        "nativeCompositeRecord": record_file,
        "nativeComposite": {
            "isAiGeneration": False, "rawNative": False, "sources": raw_sources,
            "mask": {**mask_file, "dimensions": [SIZE, SIZE], "valueMeaning": "0=raw source0;255=raw source1"},
            "sameCoordinateRule": "candidate local(x,y)=raw source local(x,y); both sources share globalNativeBox",
            "verifiedEveryPixelEqualsSelectedUnmodifiedRawSource": True,
            "sourceOperation": record.get("operation"), "sourceSelection": record.get("selection"),
            "acceptance": "numerical provenance only; no visual or formal acceptance",
        },
    })
    return source, array


def load_cell(entry: dict, base: Path, tile_id: str, row: int, col: int) -> tuple[dict, np.ndarray]:
    require(isinstance(entry, dict), f"patchMatrix[{row}][{col}] must be an explicit object.")
    raw, composite = "generationRecord" in entry, "nativeCompositeRecord" in entry
    require(raw != composite, "Each cell must specify exactly one of generationRecord or nativeCompositeRecord.")
    source_path = resolve_from(entry.get("path"), base)
    if raw:
        source, array = load_raw_source(source_path, resolve_from(entry["generationRecord"], base), tile_id, row, col, entry.get("sha256"))
    else:
        source, array = load_composite(source_path, resolve_from(entry["nativeCompositeRecord"], base), tile_id, row, col, entry.get("sha256"))
    source.update({"sourceId": row * 4 + col, "subrow": row + 1, "subcolumn": col + 1, "paddedOrigin": [col * CORE, row * CORE]})
    return source, array


def load_manifest(path: Path) -> tuple[dict, list, list]:
    require(path.is_file(), f"Manifest not found: {path}")
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    require(manifest.get("schemaVersion") == 1, "Manifest schemaVersion must be 1.")
    tile_id = manifest.get("tileId")
    require(isinstance(tile_id, str) and re.fullmatch(r"r\d{2}_c\d{2}", tile_id) is not None, "tileId must use rNN_cNN.")
    for field, value in (("nativePixels", SIZE), ("corePixels", CORE), ("haloPixels", HALO)):
        require(manifest.get(field) == value, f"Manifest {field} must explicitly equal {value}.")
    matrix = manifest.get("patchMatrix")
    require(isinstance(matrix, list) and len(matrix) == 4 and all(isinstance(row, list) and len(row) == 4 for row in matrix), "patchMatrix must explicitly contain exactly 4 rows x 4 sources; missing cells cannot be filled.")
    sources, arrays, seen = [], [], set()
    for row in range(4):
        for col in range(4):
            source, array = load_cell(matrix[row][col], path.parent, tile_id, row, col)
            source_path = Path(source["path"])
            require(source_path not in seen, f"Duplicate source: {source_path}")
            seen.add(source_path)
            sources.append(source)
            arrays.append(array)
    return manifest, sources, arrays


def minimum_path(error: np.ndarray) -> tuple[np.ndarray, dict]:
    length, overlap = error.shape
    require(overlap == OVERLAP, "Unexpected overlap in seam optimizer.")
    cumulative = error[0].copy()
    parent = np.zeros((length, overlap), dtype=np.int8)
    offsets = np.array([-1, 0, 1], dtype=np.int8)
    for index in range(1, length):
        choices = np.stack([
            np.concatenate(([np.inf], cumulative[:-1])), cumulative,
            np.concatenate((cumulative[1:], [np.inf])),
        ])
        winner = np.argmin(choices, axis=0)
        parent[index] = offsets[winner]
        cumulative = choices[winner, np.arange(overlap)] + error[index]
    path = np.empty(length, dtype=np.int32)
    path[-1] = int(np.argmin(cumulative))
    for index in range(length - 1, 0, -1):
        path[index - 1] = path[index] + int(parent[index, path[index]])
    require(int(np.max(np.abs(np.diff(path)))) <= 1, "Invalid seam step.")
    return path, {
        "overlapPathMinMax": [int(path.min()), int(path.max())],
        "pathMeanSquaredRgbDifference": float(error[np.arange(length), path].mean()),
        "straightMeanSquaredRgbDifference": float(error[:, overlap // 2].mean()),
    }


def assemble(arrays: list) -> tuple[np.ndarray, np.ndarray, list, list]:
    rows, labels, horizontal = [], [], []
    for row_index in range(4):
        row = np.empty((SIZE, PADDED, 3), dtype=np.uint8)
        ids = np.full((SIZE, PADDED), UNSET, dtype=np.uint8)
        row[:, :SIZE] = arrays[row_index * 4]
        ids[:, :SIZE] = row_index * 4
        for col_index in range(3):
            left, right = arrays[row_index * 4 + col_index:row_index * 4 + col_index + 2]
            delta = left[:, CORE:].astype(np.float64) - right[:, :OVERLAP].astype(np.float64)
            path, stats = minimum_path(np.mean(delta * delta, axis=2))
            right_origin = (col_index + 1) * CORE
            for y, overlap_x in enumerate(path):
                split = right_origin + int(overlap_x)
                row[y, split:right_origin + SIZE] = right[y, int(overlap_x):]
                ids[y, split:right_origin + SIZE] = row_index * 4 + col_index + 1
            horizontal.append({
                "subrow": row_index + 1, "leftSubcolumn": col_index + 1, "rightSubcolumn": col_index + 2,
                "paddedBoundaryOriginX": right_origin,
                "seamPath": {"index": "zero-based local row y", "values": "x inside 230px overlap; padded x=paddedBoundaryOriginX+xByY[y]", "xByY": path.tolist()},
                "statistics": stats,
            })
        require(not np.any(ids == UNSET), "Incomplete native coverage in an assembled row.")
        rows.append(row)
        labels.append(ids)
    padded = np.empty((PADDED, PADDED, 3), dtype=np.uint8)
    source_ids = np.full((PADDED, PADDED), UNSET, dtype=np.uint8)
    padded[:SIZE] = rows[0]
    source_ids[:SIZE] = labels[0]
    vertical = []
    for row_index in range(3):
        delta = rows[row_index][CORE:].astype(np.float64) - rows[row_index + 1][:OVERLAP].astype(np.float64)
        path, stats = minimum_path(np.mean(delta * delta, axis=2).T)
        lower_origin = (row_index + 1) * CORE
        for x, overlap_y in enumerate(path):
            split = lower_origin + int(overlap_y)
            padded[split:lower_origin + SIZE, x] = rows[row_index + 1][int(overlap_y):, x]
            source_ids[split:lower_origin + SIZE, x] = labels[row_index + 1][int(overlap_y):, x]
        vertical.append({
            "upperSubrow": row_index + 1, "lowerSubrow": row_index + 2,
            "paddedBoundaryOriginY": lower_origin,
            "seamPath": {"index": "zero-based padded x", "values": "y inside 230px overlap; padded y=paddedBoundaryOriginY+yByX[x]", "yByX": path.tolist()},
            "statistics": stats,
        })
    require(not np.any(source_ids == UNSET), "Incomplete native coverage in padded tile.")
    return padded, source_ids, horizontal, vertical


def verify_contributions(pixels: np.ndarray, source_ids: np.ndarray, arrays: list, offset: int) -> list:
    height, width = source_ids.shape
    require(pixels.shape == (height, width, 3), "Pixel/provenance plane shape mismatch.")
    require(np.all(source_ids < 16), "A pixel has no declared native source.")
    counts = np.bincount(source_ids.ravel(), minlength=16)
    require(int(counts.sum()) == height * width, "Source coverage count mismatch.")
    contributions = []
    for source_id, count in enumerate(counts):
        require(int(count) > 0, f"Source {source_id} contributes no pixels.")
        ys, xs = np.nonzero(source_ids == source_id)
        x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        row, col = divmod(source_id, 4)
        sx0, sy0 = x0 + offset - col * CORE, y0 + offset - row * CORE
        sx1, sy1 = x1 + offset - col * CORE, y1 + offset - row * CORE
        require(0 <= sx0 < sx1 <= SIZE and 0 <= sy0 < sy1 <= SIZE, f"Source {source_id} used outside native footprint.")
        mask = source_ids[y0:y1, x0:x1] == source_id
        require(np.array_equal(pixels[y0:y1, x0:x1][mask], arrays[source_id][sy0:sy1, sx0:sx1][mask]), f"Output pixels differ from source {source_id}.")
        contributions.append({
            "sourceId": source_id, "pixelCount": int(count),
            "outputBoundingBoxHalfOpen": [x0, y0, x1, y1],
            "nativeBoundingBoxHalfOpen": [sx0, sy0, sx1, sy1],
            "boundsContainOnlySelectedPixels": False,
            "exactSelectedPositions": "source-index plane value equals sourceId; bounding boxes are bounds, not solid ownership rectangles",
        })
    return contributions


def add_nested_contributions(contributions: list, source_ids: np.ndarray, sources: list,
                             masks: dict[int, np.ndarray], offset: int) -> None:
    """Trace composite cell ownership to each original native, even if cut away."""
    for contribution in contributions:
        source_id = contribution["sourceId"]
        if source_id not in masks:
            continue
        source = sources[source_id]
        x0, y0, x1, y1 = contribution["outputBoundingBoxHalfOpen"]
        sx0, sy0, sx1, sy1 = contribution["nativeBoundingBoxHalfOpen"]
        owned = source_ids[y0:y1, x0:x1] == source_id
        local_mask = masks[source_id][sy0:sy1, sx0:sx1]
        nested = []
        for leaf in source["nativeComposite"]["sources"]:
            ys, xs = np.nonzero(owned & (local_mask == leaf["maskValue"]))
            bounds = [int(xs.min()) + x0, int(ys.min()) + y0, int(xs.max()) + x0 + 1, int(ys.max()) + y0 + 1] if xs.size else None
            native_bounds = [int(xs.min()) + sx0, int(ys.min()) + sy0, int(xs.max()) + sx0 + 1, int(ys.max()) + sy0 + 1] if xs.size else None
            nested.append({
                "compositeSourceId": leaf["compositeSourceId"], "path": leaf["path"], "sha256": leaf["sha256"],
                "pixelCount": int(xs.size), "outputBoundingBoxHalfOpen": bounds,
                "nativeBoundingBoxHalfOpen": native_bounds, "boundsContainOnlySelectedPixels": False,
                "exactSelectedPositions": f"cell source-index plane == {source_id} AND composite_source_{source_id:02d}_native_mask[source y,source x] == {leaf['maskValue']}",
                "nativeCoordinateRule": f"source x=output x+{offset}-{source['paddedOrigin'][0]}; source y=output y+{offset}-{source['paddedOrigin'][1]}",
            })
        require(sum(leaf["pixelCount"] for leaf in nested) == contribution["pixelCount"], "Nested original-native contribution count mismatch.")
        contribution["originalNativeContributions"] = nested


def save_qa(qa_dir: Path, tile: Image.Image) -> dict:
    entries = []
    def crop(name: str, box: tuple, role: str) -> None:
        entries.append({**save_image(qa_dir / name, tile.crop(box)), "role": role, "tileCropBoxHalfOpen": list(box), "nativeScale100Percent": True})
    # Every left/right boundary is covered top-to-bottom by four overlapping
    # sections of the FINAL tile, so row-to-row seam changes are also visible.
    for row in range(4):
        y0, y1 = max(0, row * CORE - HALO), min(TILE, row * CORE + SIZE - HALO)
        for boundary in range(1, 4):
            x = boundary * CORE
            crop(f"left-right_r{row + 1:02d}_c{boundary:02d}-c{boundary + 1:02d}_100pct.png", (x - 240, y0, x + 240, y1), "full-height segment of final left/right native seam")
    # Each top/bottom boundary is covered over the full final width, without
    # resampling, in four contiguous 1024px sections.
    for boundary in range(1, 4):
        y = boundary * CORE
        for segment in range(4):
            x0, x1 = segment * CORE, (segment + 1) * CORE
            crop(f"top-bottom_r{boundary:02d}-r{boundary + 1:02d}_x{x0:04d}-{x1:04d}_100pct.png", (x0, y - 240, x1, y + 240), "full-width segment of final top/bottom native seam")
    for row in range(1, 4):
        for col in range(1, 4):
            x, y = col * CORE, row * CORE
            crop(f"junction_r{row:02d}-r{row + 1:02d}_c{col:02d}-c{col + 1:02d}_100pct.png", (x - 240, y - 240, x + 240, y + 240), "four-source intersection; native scale")
    preview = save_image(qa_dir / "preview_1024px_NOT_FOR_GAME.png", tile.resize((1024, 1024), Image.Resampling.LANCZOS))
    preview.update({"role": "downsampled inspection preview only, forbidden as game art or native seam evidence", "nativeScale100Percent": False})
    return {"status": "unreviewed", "preview": preview, "seamAndJunctionCrops": entries, "coverage": {"finalVerticalSeamBands": 3, "finalHorizontalSeamBands": 3, "eachBandFullyCoveredAt100Percent": True, "junctionCount": 9, "cropCount": len(entries)}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--manifest", required=True, help="Explicit 4x4 native patch JSON manifest; no glob/latest selection.")
    parser.add_argument("--output", required=True, help="Candidate PNG path, absolute or relative to this zone; all outputs remain inside zone.")
    args = parser.parse_args()
    manifest_path = Path(args.manifest).resolve()
    output_path = writable(resolve_from(args.output, ZONE))
    require(output_path.suffix.lower() == ".png", "--output must end with .png.")
    require(not output_path.is_relative_to(NATIVE.resolve()), "Candidate output must not overwrite/write inside native/.")
    manifest, sources, arrays = load_manifest(manifest_path)
    require(output_path != manifest_path, "Output must not overwrite the input manifest.")
    qa_dir = writable(ZONE / "qa" / f"assembly_{output_path.stem}")
    record_path = writable(output_path.with_suffix(".assembly.json"))
    require(not output_path.exists() and not record_path.exists() and not qa_dir.exists(), "Output version already exists; choose a fresh candidate name. Existing artifacts are never overwritten.")
    composite_masks = {}
    for source in sources:
        if source["kind"] == "nativeComposite":
            mask_file = source["nativeComposite"]["mask"]
            check_hash(digest(Path(mask_file["path"])), mask_file["sha256"], "composite mask before assembly")
            composite_masks[source["sourceId"]] = read_binary_mask(Path(mask_file["path"]))
    padded, padded_ids, horizontal, vertical = assemble(arrays)
    padded_contributions = verify_contributions(padded, padded_ids, arrays, 0)
    add_nested_contributions(padded_contributions, padded_ids, sources, composite_masks, 0)
    tile = padded[HALO:HALO + TILE, HALO:HALO + TILE]
    tile_ids = padded_ids[HALO:HALO + TILE, HALO:HALO + TILE]
    require(tile.shape == (TILE, TILE, 3), "Final crop must measure 4096x4096.")
    contributions = verify_contributions(tile, tile_ids, arrays, HALO)
    add_nested_contributions(contributions, tile_ids, sources, composite_masks, HALO)
    qa_dir.mkdir(parents=True, exist_ok=False)
    provenance_path = writable(qa_dir / "source_index_planes.npz")
    nested_planes = {f"composite_source_{source_id:02d}_native_mask": mask for source_id, mask in composite_masks.items()}
    with provenance_path.open("xb") as handle:
        np.savez_compressed(handle, padded_source_id=padded_ids, tile_source_id=tile_ids, padded_source_origins=np.array([s["paddedOrigin"] for s in sources], dtype=np.int32), **nested_planes)
    provenance = {**file_record(provenance_path), "format": "compressed numpy arrays, not game art", "planes": {"padded_source_id": [PADDED, PADDED], "tile_source_id": [TILE, TILE]}, "valueMeaning": "uint8 sourceId 0..15 as listed in sources; every position records the selected source", "nativeCoordinateRule": "For tile pixel (x,y) owned by sourceId: source x=x+115-(sourceId%4)*1024; source y=y+115-(sourceId//4)*1024. For padded pixels omit +115."}
    provenance["compositeNativeMasks"] = {name: {"dimensions": [SIZE, SIZE], "valueMeaning": "0=original raw source0;255=original raw source1; sample at the source local coordinate, only when the cell owns the output pixel"} for name in nested_planes}
    tile_image = Image.fromarray(tile)
    qa = save_qa(qa_dir, tile_image)
    qa_record = save_json(qa_dir / "qa_index.json", qa)
    # Write candidate art only after all native coverage/provenance checks.
    output = save_image(output_path, tile_image)
    record = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "operation": "mechanical 4x4 native-patch assembly", "isAiGeneration": False,
        "assembler": file_record(Path(__file__).resolve()),
        "status": "candidate_pending_full_native_visual_and_external_seam_review",
        "tileId": manifest["tileId"], "manifest": file_record(manifest_path),
        "manifestSnapshot": manifest, "sources": sources, "output": output,
        "geometry": {"nativePixels": SIZE, "corePixels": CORE, "haloPixels": HALO, "overlapPixels": OVERLAP, "rowDimensions": [PADDED, SIZE], "paddedDimensions": [PADDED, PADDED], "finalCropBoxHalfOpen": [HALO, HALO, HALO + TILE, HALO + TILE], "finalDimensions": [TILE, TILE]},
        "method": {"order": "four left-to-right native row assemblies, then top-to-bottom row assembly, then crop 115px perimeter", "cost": "mean squared unmodified RGB difference at identical overlapping coordinates", "optimizer": "dynamic programming, adjacent path-coordinate step -1/0/+1", "tieBreak": "argmin first match; predecessor -1,0,+1; smallest terminal coordinate on ties", "sourceSelection": "earlier source before seam; later source on/after seam", "registration": False, "resizingFinalArt": False, "feathering": False, "colorCorrection": False, "drawingOrPixelSynthesis": False, "previewOnlyDownsampling": True},
        "horizontalJoins": horizontal, "verticalJoins": vertical,
        "provenance": provenance, "paddedContributions": padded_contributions, "tileContributions": contributions,
        "coverageAssertions": {"fullNativeCoverage": True, "paddedPixelCount": PADDED * PADDED, "tilePixelCount": TILE * TILE, "sourceContributionSum": sum(c["pixelCount"] for c in contributions), "unassignedPixels": 0, "all16SourcesContribute": True, "allPaddedAndTilePixelsExactlyMatchUnmodifiedRecordedSourceCoordinates": True, "allCompositePixelsExactlyMatchUnmodifiedOriginalRawSourceCoordinates": True, "compositeCellCount": len(composite_masks), "nestedOriginalContributionSumsVerified": True, "guidePixelsUsed": False},
        "qa": qa_record, "formalAcceptedCount": 0,
        "limits": ["Numerical seam optimization and full native coverage do not prove visual continuity.", "All generated QA crops require native-scale visual review, including nine four-source junctions.", "External tile/zone edges remain unverified; this script never grants formal acceptance.", "World scale, navigation and capacity are not tested. No model/quality upgrade is claimed by mechanical processing."]
    }
    record_file = save_json(record_path, record)
    print(json.dumps({"status": record["status"], "output": output, "record": record_file, "qa": qa_record, "nativeSources": 16, "fullNativeCoverage": True, "formalAcceptedCount": 0}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "failed", "error": str(error), "candidateAccepted": False}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
