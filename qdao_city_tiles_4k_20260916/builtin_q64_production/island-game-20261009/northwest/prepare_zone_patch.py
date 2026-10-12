"""Prepare layout-only guides and exact native overlaps; never paint game art."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


ZONE = Path(__file__).resolve().parent
MAP_ROOT = ZONE.parent
CANVAS, TILE, CORE, HALO, NATIVE, OVERLAP = 57344, 4096, 1024, 115, 1254, 230
DIRECTIONS = ("left", "right", "top", "bottom")
OFFSETS = {"left": (-CORE, 0), "right": (CORE, 0), "top": (0, -CORE), "bottom": (0, CORE)}
STEM_PATTERN = re.compile(r"r(\d{2})_c(\d{2})_s(\d{2})_(\d{2})_(a\d{2,})")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_record(path: Path) -> dict:
    require(path.is_file(), f"Required file missing: {path}")
    return {"path": path.as_posix(), "sha256": sha(path)}


def image_record(path: Path, role: str) -> tuple[dict, Image.Image]:
    record = file_record(path)
    with Image.open(path) as source:
        require(source.mode in ("RGB", "RGBA"), f"Unsupported image mode: {path}: {source.mode}")
        if source.mode == "RGBA":
            require(source.getextrema()[3] == (255, 255), f"Nonopaque image cannot be flattened: {path}")
        image = source.convert("RGB")
        record.update({"role": role, "nativeSize": list(source.size), "originalMode": source.mode})
    return record, image


def geometry(tr: int, tc: int, sr: int, sc: int) -> dict:
    require(1 <= tr <= 14 and 1 <= tc <= 14 and 1 <= sr <= 4 and 1 <= sc <= 4, "Tile/subpatch coordinate outside map contract.")
    x, y = (tc - 1) * TILE + (sc - 1) * CORE, (tr - 1) * TILE + (sr - 1) * CORE
    return {"tile": f"r{tr:02d}_c{tc:02d}", "stem": f"r{tr:02d}_c{tc:02d}_s{sr:02d}_{sc:02d}", "coreBox": [x, y, x + CORE, y + CORE], "globalBox": [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO]}


def source_zone(contract: dict, tr: int, tc: int) -> Path:
    matches = [entry["id"] for entry in contract["zones"] if entry["rows"][0] <= tr <= entry["rows"][1] and entry["columns"][0] <= tc <= entry["columns"][1]]
    require(len(matches) == 1, f"No unique source zone for r{tr:02d}_c{tc:02d}.")
    return MAP_ROOT / matches[0]


def load_neighbor(stem: str, direction: str, target: dict, contract: dict) -> tuple[dict, Image.Image]:
    match = STEM_PATTERN.fullmatch(stem)
    require(match is not None, f"--{direction} requires an explicit rNN_cNN_sNN_NN_aNN stem, not a path/glob/latest selector.")
    tr, tc, sr, sc = map(int, match.groups()[:4])
    source_geometry = geometry(tr, tc, sr, sc)
    dx, dy = OFFSETS[direction]
    expected = [target["coreBox"][0] + dx, target["coreBox"][1] + dy]
    require(source_geometry["coreBox"][:2] == expected, f"--{direction} {stem} has global core origin {source_geometry['coreBox'][:2]}, expected {expected}; not the adjacent native slot.")
    owner = source_zone(contract, tr, tc)
    path = owner / "native" / f"{stem}.png"
    record, image = image_record(path, f"{direction} adjacent native; unchanged 230px overlap constrains continuity")
    require(image.size == (NATIVE, NATIVE), f"Measured native size differs from 1254 square: {stem}: {image.size}")
    generation_path = path.with_suffix(".png.generation.json")
    generation = read(generation_path)
    require(generation.get("sha256") == record["sha256"], f"Generation record hash mismatch: {stem}")
    require((generation.get("nativeWidth"), generation.get("nativeHeight")) == (NATIVE, NATIVE), f"Generation dimensions mismatch: {stem}")
    require(generation.get("route") == "builtin" and generation.get("resizedAfterGeneration") is False and generation.get("finalArtUpscaled") is False, f"Neighbor lacks builtin/unscaled evidence: {stem}")
    # Version-specific input is preferred. An exact unversioned patch coordinate
    # contract may substantiate that slot; this never chooses another art version.
    coordinate_path = owner / "guides" / f"{stem}.input.json"
    coordinate_basis = "exact version input record"
    if not coordinate_path.is_file():
        coordinate_path = owner / "guides" / f"{source_geometry['stem']}.input.json"
        coordinate_basis = "exact patch-slot coordinate contract; image version remains explicitly selected"
    if not coordinate_path.is_file() and "globalBox" in generation and "coreBox" in generation:
        coordinate_path = generation_path
        coordinate_basis = "exact selected source generation record with explicit native/core coordinates and verified source hash"
    require(coordinate_path.is_file(), f"No exact version or patch-slot coordinate record for {stem}; do not infer from an unrelated/latest version.")
    coordinate_record = read(coordinate_path)
    require(coordinate_record.get("globalBox") == source_geometry["globalBox"] and coordinate_record.get("coreBox") == source_geometry["coreBox"], f"Recorded global native/core box conflicts with stem: {stem}")
    a, b = target["globalBox"], source_geometry["globalBox"]
    common = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    expected_dimensions = [OVERLAP, NATIVE] if direction in ("left", "right") else [NATIVE, OVERLAP]
    require([common[2] - common[0], common[3] - common[1]] == expected_dimensions, f"Incorrect global overlap: {stem}")
    crop = [common[0] - b[0], common[1] - b[1], common[2] - b[0], common[3] - b[1]]
    destination = [common[0] - a[0], common[1] - a[1]]
    record.update({"stem": stem, "direction": direction, "sourceZone": owner.name, "globalBox": b, "coreBox": source_geometry["coreBox"], "globalOverlapBox": common, "sourceCrop": crop, "destination": destination, "targetLocalBox": [destination[0], destination[1], destination[0] + expected_dimensions[0], destination[1] + expected_dimensions[1]], "generationRecord": file_record(generation_path), "coordinateEvidence": {**file_record(coordinate_path), "basis": coordinate_basis}, "sameTile": source_geometry["tile"] == target["tile"], "resized": False})
    return record, image


def output_path(directory: Path, name: str) -> Path:
    path = (directory / name).resolve()
    require(path.is_relative_to(ZONE), f"Output outside zone forbidden: {path}")
    return path


def save_image_new(path: Path, image: Image.Image) -> dict:
    # Exclusive creation protects an already recorded version even if another
    # process creates it after preflight. No existing file is overwritten.
    with path.open("xb") as handle:
        image.save(handle, format="PNG")
    return {**file_record(path), "nativeSize": list(image.size)}


def write_json_new(path: Path, value) -> dict:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return file_record(path)


def prepare(args) -> dict:
    require(1 <= args.tile_row <= 7 and 1 <= args.tile_col <= 7, "Target tile row/col must be 1..7 in northwest zone.")
    require(re.fullmatch(r"a\d{2,}", args.attempt) is not None, "--attempt must be an explicit version such as a01; no automatic increment.")
    target = geometry(args.tile_row, args.tile_col, args.subrow, args.subcol)
    version = f"{target['stem']}_{args.attempt}"
    outdir = Path(args.output_dir) if args.output_dir else ZONE / "guides"
    outdir = (outdir if outdir.is_absolute() else ZONE / outdir).resolve()
    require(outdir.is_relative_to(ZONE), "--output-dir must remain inside this zone.")
    contract_path = MAP_ROOT / "production-contract.json"
    contract = read(contract_path)
    require(contract["artCanvasPixels"] == [CANVAS, CANVAS] and contract["formalTilePixels"] == [TILE, TILE], "Shared contract dimensions changed; recalculate before preparing.")
    references, layout = [], None
    for field, role in (("layoutReference", "sole current global layout; not final pixels"), ("detailStyleReference", "materials/architecture only; independent close-up, not coordinate crop"), ("primaryStyleReference", "primary approved Daoist Q painterly style only; do not copy UI/night lighting")):
        record, image = image_record(Path(contract[field]), role)
        if field == "layoutReference":
            require(record["sha256"] == contract["layoutSha256"] and image.size == (1254, 1254), "Locked layout identity/dimensions mismatch.")
            layout = image
        elif field == "detailStyleReference":
            require(record["sha256"] == contract["detailSha256"], "Locked detail identity mismatch.")
        references.append(record)
    neighbors, native_images = [], []
    for direction in DIRECTIONS:
        stem = getattr(args, direction)
        if stem:
            neighbor, native = load_neighbor(stem, direction, target, contract)
            neighbors.append(neighbor)
            native_images.append(native)
    names = {
        "guide": f"{version}.layout-with-native.png",
        "guideDerivation": f"{version}.layout-with-native.png.derivation.json",
        "input": f"{version}.input.json",
        "references": f"{version}.references.json",
    }
    if len(neighbors) > 1:
        names.update({"contact": f"{version}.native-reference-contact.png", "contactDerivation": f"{version}.native-reference-contact.png.derivation.json"})
    paths = {role: output_path(outdir, name) for role, name in names.items()}
    existing = [str(path) for path in paths.values() if path.exists()]
    require(not existing, f"Refuse overwrite of existing version files: {existing}")
    ref_box = [value * layout.width / CANVAS for value in target["globalBox"]]
    # Padding duplicates only overview border pixels. It prevents EXTENT's black
    # out-of-image fill; this guide is never a final native-art source.
    required_overhang = max(0.0, -ref_box[0], -ref_box[1], ref_box[2] - layout.width, ref_box[3] - layout.height)
    pad = int(math.ceil(required_overhang)) + 3
    padded = Image.fromarray(np.pad(np.asarray(layout), ((pad, pad), (pad, pad), (0, 0)), mode="edge"))
    guide = padded.transform((NATIVE, NATIVE), Image.Transform.EXTENT, tuple(value + pad for value in ref_box), Image.Resampling.BICUBIC)
    layout_guide = np.asarray(guide).copy()
    owner_plane = np.zeros((NATIVE, NATIVE), dtype=np.uint8)
    corner_conflicts = []
    for index, (neighbor, native) in enumerate(zip(neighbors, native_images), start=1):
        strip = native.crop(tuple(neighbor["sourceCrop"]))
        dx, dy = neighbor["destination"]
        sw, sh = strip.size
        current = np.asarray(guide)[dy:dy + sh, dx:dx + sw]
        previous = owner_plane[dy:dy + sh, dx:dx + sw]
        for prior_id in np.unique(previous):
            if prior_id == 0:
                continue
            region = previous == prior_id
            differences = np.abs(current.astype(np.float64) - np.asarray(strip).astype(np.float64))[region]
            corner_conflicts.append({"earlierDirection": neighbors[int(prior_id) - 1]["direction"], "laterDirection": neighbor["direction"], "overlappingPixelCount": int(region.sum()), "meanAbsRgbDifference": float(differences.mean()), "p95AbsRgbDifference": float(np.percentile(differences, 95)), "maxAbsRgbDifference": float(differences.max()), "guideWinner": neighbor["direction"], "bothUnmodifiedSourcesRetainedInFifthInput": len(neighbors) > 1, "geometryAcceptance": "unreviewed; do not blend or hide incompatible corners"})
        guide.paste(strip, (dx, dy))
        owner_plane[dy:dy + sh, dx:dx + sw] = index
    final_guide = np.asarray(guide)
    require(np.array_equal(final_guide[owner_plane == 0], layout_guide[owner_plane == 0]), "Layout-only pixels unexpectedly changed.")
    for index, (neighbor, native) in enumerate(zip(neighbors, native_images), start=1):
        x0, y0, x1, y1 = neighbor["targetLocalBox"]
        selected = owner_plane[y0:y1, x0:x1] == index
        require(np.array_equal(final_guide[y0:y1, x0:x1][selected], np.asarray(native.crop(tuple(neighbor["sourceCrop"])))[selected]), "Neighbor strip source-pixel assertion failed.")
    outdir.mkdir(parents=True, exist_ok=True)
    guide_record = save_image_new(paths["guide"], guide)
    guide_record.update({"role": "layout-only target guide with exact unresampled native neighbor strips; never final art", "derivedFrom": [references[0]] + neighbors})
    inputs = [guide_record] + references
    contact_record = None
    if len(neighbors) == 1:
        inputs.append(neighbors[0])
    elif len(neighbors) > 1:
        # Horizontal packing has no blank cells, drawn labels or resampling.
        contact_array = np.concatenate([np.asarray(image) for image in native_images], axis=1)
        contact_record = save_image_new(paths["contact"], Image.fromarray(contact_array))
        placements = [{"source": neighbor, "contactBoxHalfOpen": [i * NATIVE, 0, (i + 1) * NATIVE, NATIVE], "sourceCrop": [0, 0, NATIVE, NATIVE], "resized": False} for i, neighbor in enumerate(neighbors)]
        for index, native in enumerate(native_images):
            require(np.array_equal(contact_array[:, index * NATIVE:(index + 1) * NATIVE], np.asarray(native)), "Contact pixels differ from native.")
        contact_record.update({"role": "unresized native neighbor contact; panels from left: " + ", ".join(f"{i + 1}={neighbor['direction']}" for i, neighbor in enumerate(neighbors)), "derivedFrom": placements})
        write_json_new(paths["contactDerivation"], {"schemaVersion": 1, **contact_record, "operation": "horizontal concatenation of whole native inputs; no blank cells/labels/scaling", "isAiGeneration": False, "newModelOrQualityClaim": None, "allContactPixelsExactlyMatchSources": True})
        inputs.append(contact_record)
    require(len(inputs) <= 5, "Too many image references.")
    out_of_canvas = {"left": max(0, -target["globalBox"][0]), "top": max(0, -target["globalBox"][1]), "right": max(0, target["globalBox"][2] - CANVAS), "bottom": max(0, target["globalBox"][3] - CANVAS)}
    derivation = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "file": guide_record["path"], "sha256": guide_record["sha256"], "operation": "edge-extended floating-coordinate layout crop plus exact native neighbor overlap paste", "isAiGeneration": False,
        "newModelOrQualityClaim": None, "script": file_record(Path(__file__).resolve()), "contract": file_record(contract_path),
        "globalBox": target["globalBox"], "coreBox": target["coreBox"], "referenceBox": ref_box,
        "outputSize": [NATIVE, NATIVE], "coreLocalBoxHalfOpen": [HALO, HALO, HALO + CORE, HALO + CORE],
        "layout": references[0], "neighbors": neighbors, "guidePasteOrder": DIRECTIONS,
        "cornerConflicts": corner_conflicts, "cornerRule": "later explicit direction wins overlapping guide pixels; no blending; all complete neighbor originals remain separately inspectable in input 5",
        "layoutEdgeExtension": {"method": "edge-repeat pad of overview before bicubic EXTENT sampling", "overviewPadPixelsPerSide": pad, "outOfCanvasNativeHaloPixels": out_of_canvas, "anyOutOfCanvasHalo": any(out_of_canvas.values()), "coreWithinCanvas": True, "outOfCanvasHaloEntersFormalCore": False, "appliesOnlyToLayoutGuide": True, "blackFillUsed": False},
        "sourcePixelAssertions": {"everyVisibleNeighborPixelExactlyMatchesItsNativeSource": True, "neighborResizing": False, "neighborRegistration": False, "neighborFeathering": False, "neighborColorCorrection": False},
        "layoutPixelsForbiddenInFinal": True, "nativeGenerationPerformed": False,
    }
    guide_derivation = write_json_new(paths["guideDerivation"], derivation)
    record = {"schemaVersion": 1, **target, "versionStem": version, "attempt": args.attempt, "referenceBox": ref_box, "inputs": inputs, "neighbor": neighbors, "imageGenReferencedImagePaths": [entry["path"] for entry in inputs], "inputCount": len(inputs), "guideDerivation": guide_derivation, "cornerConflicts": corner_conflicts, "layoutPixelsForbiddenInFinal": True, "operation": derivation["operation"], "edgeExtension": derivation["layoutEdgeExtension"], "explicitSourcesOnly": True, "nativeGenerationPerformed": False, "progressModified": False, "workflowIngestCompatibility": "Pass this input.json or references.json as workflow.py ingest --refs; ingest itself is separate and not run by this tool."}
    reference_file = write_json_new(paths["references"], inputs)
    input_file = write_json_new(paths["input"], record)
    return {"status": "guide_prepared_not_game_art", "versionStem": version, "globalBox": target["globalBox"], "coreBox": target["coreBox"], "input": input_file, "references": reference_file, "guide": guide_record, "contact": contact_record, "inputCount": len(inputs), "edgeExtension": derivation["layoutEdgeExtension"], "cornerConflicts": corner_conflicts, "nativeGenerationPerformed": False, "progressModified": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tile-row", type=int, required=True)
    parser.add_argument("--tile-col", type=int, required=True)
    parser.add_argument("--subrow", type=int, required=True)
    parser.add_argument("--subcol", type=int, required=True)
    parser.add_argument("--attempt", required=True, help="Explicit aNN version; existing output versions are never overwritten.")
    for direction in DIRECTIONS:
        parser.add_argument(f"--{direction}", help=f"Explicit {direction} native stem, including attempt; no auto-selection.")
    parser.add_argument("--output-dir", help="Optional directory inside this zone, default guides/.")
    print(json.dumps(prepare(parser.parse_args()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"status": "failed", "error": str(error), "nativeGenerationPerformed": False, "progressModified": False}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
