#!/usr/bin/env python3
"""Mechanical preparation and assembly of independently refined city patches.

Only guide images may be enlarged. This script does not generate artwork.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "layout-source-native.png"
PIPELINE = ROOT / "seam_helpers.py"
GRID = 6
CORE = 1024
HALO = 115
OVERLAP = HALO * 2
PATCH = CORE + OVERLAP
MASTER = GRID * CORE


def output_path(relative: str) -> Path:
    path = (ROOT / relative).resolve()
    if path != ROOT and ROOT not in path.parents:
        raise ValueError(f"Output escapes the task directory: {relative}")
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(relative: str, data: dict) -> None:
    destination = output_path(relative)
    text = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    json.loads(text)
    destination.write_text(text, encoding="utf-8")


def entries():
    for row in range(1, GRID + 1):
        for column in range(1, GRID + 1):
            yield row, column, f"city_r{row:02d}_c{column:02d}.png"


def open_rgb(path: Path) -> Image.Image:
    with Image.open(path) as image:
        image.load()
        return image.convert("RGB")


def save_png(image: Image.Image, relative: str) -> dict:
    path = output_path(relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", compress_level=6)
    with Image.open(path) as saved:
        saved.load()
        if saved.format != "PNG" or saved.mode != "RGB" or saved.size != image.size:
            raise RuntimeError(f"PNG round-trip metadata failed: {path}")
    return {"file": relative, "width": image.width, "height": image.height,
            "sha256": sha256(path)}


def prepare() -> None:
    for relative in ("guides", "refined", "prompts", "Tiles", "qa"):
        output_path(relative).mkdir(parents=True, exist_ok=True)
    source = open_rgb(SOURCE)
    if source.size != (1254, 1254):
        raise ValueError(f"Expected the authorized 1254x1254 source, got {source.size}")
    guide = source.resize((MASTER, MASTER), Image.Resampling.LANCZOS)
    padded = np.pad(np.asarray(guide), ((HALO, HALO), (HALO, HALO), (0, 0)), mode="reflect")
    records = []
    for row, column, name in entries():
        x, y = (column - 1) * CORE, (row - 1) * CORE
        patch = Image.fromarray(padded[y:y + PATCH, x:x + PATCH])
        record = save_png(patch, f"guides/{name}")
        record.update({"row": row, "column": column,
                       "coreBoundsInMaster": {"x": x, "y": y, "width": CORE, "height": CORE},
                       "guideBoundsInPaddedLayout": {"x": x, "y": y, "width": PATCH, "height": PATCH},
                       "promptFile": f"prompts/{Path(name).stem}.txt",
                       "refinedFile": f"refined/{name}"})
        records.append(record)
    layout = save_png(guide, "layout-guide-6144.png")
    write_json("prepare-manifest.json", {
        "schemaVersion": 1,
        "preparedAtUtc": datetime.now(timezone.utc).isoformat(),
        "source": {"file": str(SOURCE), "width": source.width, "height": source.height, "sha256": sha256(SOURCE)},
        "grid": {"rows": GRID, "columns": GRID, "order": "row-major", "origin": "top-left"},
        "masterSize": MASTER, "coreSize": CORE, "patchSize": PATCH,
        "contextPerSide": HALO, "adjacentOverlap": OVERLAP,
        "outerPadding": "reflect", "guideResampling": "Lanczos; layout reference only",
        "layoutGuide": layout, "guideArtUpscaled": True,
        "finalArtworkCreated": False, "runtimeIntegration": False,
        "guides": records,
    })
    print(f"Prepared {len(records)} layout-only guides: {PATCH}x{PATCH}, core {CORE}, halo {HALO}, adjacent overlap {OVERLAP}.")
    print(f"Guide folder: {output_path('guides')}")


def load_prepare_manifest() -> dict:
    metadata = json.loads(output_path("prepare-manifest.json").read_text(encoding="utf-8-sig"))
    expected = {"masterSize": MASTER, "coreSize": CORE, "patchSize": PATCH,
                "contextPerSide": HALO, "adjacentOverlap": OVERLAP, "outerPadding": "reflect"}
    for key, value in expected.items():
        if metadata.get(key) != value:
            raise ValueError(f"Preparation parameter mismatch: {key}")
    if metadata.get("source", {}).get("sha256") != sha256(SOURCE):
        raise ValueError("Authorized layout source has changed since preparation.")
    guides = metadata.get("guides", [])
    expected_names = [f"guides/{name}" for _, _, name in entries()]
    if [entry.get("file") for entry in guides] != expected_names:
        raise ValueError("Guide list is not the exact row-major patch set.")
    for record in guides:
        guide = output_path(record["file"])
        if sha256(guide) != record["sha256"]:
            raise ValueError(f"Guide changed after preparation: {guide.name}")
        with Image.open(guide) as image:
            if image.size != (PATCH, PATCH) or image.mode != "RGB":
                raise ValueError(f"Unexpected guide dimensions/mode: {guide.name}")
    return metadata


def load_seam_pipeline():
    import importlib.util
    # Importing the approved external helper must not write outside this output directory.
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("approved_tianyong_seam_pipeline", PIPELINE)
        if spec is None or spec.loader is None:
            raise RuntimeError("Cannot load approved seam helper.")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = previous


def inspect_refinements() -> list[dict]:
    expected_names = {name for _, _, name in entries()}
    actual_names = {path.name for path in output_path("refined").glob("*.png")}
    if actual_names != expected_names:
        raise ValueError(f"Expected exactly {GRID * GRID} refined PNGs; "
                         f"missing={sorted(expected_names - actual_names)}, "
                         f"extra={sorted(actual_names - expected_names)}")
    records = []
    for row, column, name in entries():
        path = output_path(f"refined/{name}")
        prompt_relative = f"prompts/{Path(name).stem}.txt"
        prompt_path = output_path(prompt_relative)
        if not prompt_path.is_file():
            raise ValueError(f"Missing prompt provenance: {prompt_relative}")
        prompt = prompt_path.read_text(encoding="utf-8-sig").strip()
        if len(prompt) < 200 or prompt.lower() in ("undefined", "null", "none"):
            raise ValueError(f"Prompt must be nonempty: {prompt_relative}")
        with Image.open(path) as native:
            native.load()
            width, height = native.size
            if native.format != "PNG" or width != height or min(width, height) < PATCH:
                raise ValueError(f"Refined image must be a square PNG >= {PATCH}px; "
                                 f"{name} is {native.format} {width}x{height}. Final-art enlargement is forbidden.")
            if "A" in native.getbands() and native.getchannel("A").getextrema() != (255, 255):
                raise ValueError(f"Refined image has transparency: {name}")
            if native.size == (PATCH, PATCH):
                if np.array_equal(np.asarray(native.convert("RGB")), np.asarray(open_rgb(output_path(f"guides/{name}")))):
                    raise ValueError(f"Refined file is the enlarged layout guide, not new artwork: {name}")
        records.append({
            "id": Path(name).stem, "row": row, "column": column,
            "file": f"refined/{name}", "nativeWidth": width, "nativeHeight": height,
            "nativeSha256": sha256(path), "workingWidth": PATCH, "workingHeight": PATCH,
            "downsampled": width > PATCH, "upscaled": False,
            "promptFile": prompt_relative, "promptSha256": sha256(prompt_path),
            "promptNonempty": True, "promptCharacters": len(prompt),
        })
    return records


def seam_diagnostics(pixels: np.ndarray) -> dict:
    result = {"vertical": [], "horizontal": [],
              "interpretation": "Numeric boundary deltas are diagnostic only; they do not prove visually seamless artwork."}
    sample = pixels.astype(np.int16)
    for axis_name, array in (("vertical", sample), ("horizontal", np.transpose(sample, (1, 0, 2)))):
        for boundary in range(CORE, MASTER, CORE):
            delta = float(np.abs(array[:, boundary] - array[:, boundary - 1]).mean())
            local = float(np.abs(np.diff(array[:, boundary - 8:boundary + 8], axis=1)).mean())
            result[axis_name].append({"coordinate": boundary, "boundaryMeanAbsoluteDelta": round(delta, 6),
                                      "nearbyMeanAbsoluteDelta": round(local, 6)})
    return result


def assemble() -> None:
    preparation = load_prepare_manifest()
    refinements = inspect_refinements()
    helpers = load_seam_pipeline()
    stitched_master = None
    color_records = []
    for row in range(1, GRID + 1):
        stitched_row = None
        for column in range(1, GRID + 1):
            name = f"city_r{row:02d}_c{column:02d}.png"
            raw = open_rgb(output_path(f"refined/{name}"))
            if raw.size != (PATCH, PATCH):
                # Preflight has already rejected any source smaller than this target.
                raw = raw.resize((PATCH, PATCH), Image.Resampling.LANCZOS)
            guide = open_rgb(output_path(f"guides/{name}"))
            matched = helpers._match_color(raw, guide)
            raw_array = np.asarray(raw, dtype=np.float32)
            shift = np.clip(np.asarray(matched, dtype=np.float32) - raw_array, -16.0, 16.0) * 0.25
            patch = np.uint8(np.clip(np.rint(raw_array + shift), 0, 255))
            color_records.append({"id": Path(name).stem,
                                  "meanAbsoluteChannelShift": round(float(np.abs(shift).mean()), 6),
                                  "maximumAbsoluteChannelShift": round(float(np.abs(shift).max()), 6)})
            stitched_row = patch.copy() if stitched_row is None else helpers._append_with_minimum_seam(stitched_row, patch, OVERLAP)
        if stitched_master is None:
            stitched_master = stitched_row
        else:
            stitched_master = np.transpose(helpers._append_with_minimum_seam(
                np.transpose(stitched_master, (1, 0, 2)),
                np.transpose(stitched_row, (1, 0, 2)), OVERLAP), (1, 0, 2))
        print(f"Assembled row {row}/{GRID}.", flush=True)
    padded_size = MASTER + OVERLAP
    if stitched_master is None or stitched_master.shape != (padded_size, padded_size, 3):
        raise RuntimeError(f"Unexpected padded assembly dimensions: {getattr(stitched_master, 'shape', None)}")
    final_pixels = np.ascontiguousarray(stitched_master[HALO:HALO + MASTER, HALO:HALO + MASTER])
    master = Image.fromarray(final_pixels)
    del stitched_master
    master_record = save_png(master, "tianyong_city_master_6144.png")
    master_record["decodedRgbSha256"] = hashlib.sha256(final_pixels.tobytes()).hexdigest()
    preview_record = save_png(master.resize((2048, 2048), Image.Resampling.LANCZOS), "tianyong_city_master_preview_2048.png")
    tile_records = []
    for row, column, name in entries():
        x, y = (column - 1) * CORE, (row - 1) * CORE
        record = save_png(master.crop((x, y, x + CORE, y + CORE)), f"Tiles/{name}")
        record.update({"row": row, "column": column, "pixelBounds": {"x": x, "y": y, "width": CORE, "height": CORE}})
        tile_records.append(record)
    qa_records = []
    crop_size = min(1024, MASTER)
    positions = [0, (MASTER - crop_size) // 2, MASTER - crop_size]
    for qa_row, y in enumerate(positions, 1):
        for qa_column, x in enumerate(positions, 1):
            record = save_png(master.crop((x, y, x + crop_size, y + crop_size)),
                              f"qa/native_100pct_r{qa_row:02d}_c{qa_column:02d}.png")
            record.update({"pixelBounds": {"x": x, "y": y, "width": crop_size, "height": crop_size},
                           "resampled": False, "scale": 1.0})
            qa_records.append(record)
    manifest = {
        "schemaVersion": 1, "assembledAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "assembled; mechanical verification only; visual review remains separate",
        "sourceLayout": preparation["source"],
        "grid": {"rows": GRID, "columns": GRID, "order": "row-major", "origin": "top-left"},
        "masterSize": {"width": MASTER, "height": MASTER}, "coreSize": CORE,
        "patchSize": PATCH, "contextPerSide": HALO, "adjacentOverlap": OVERLAP,
        "guideArtUpscaled": True, "finalArtUpscaled": False, "runtimeIntegration": False,
        "model": None, "modelExposure": "The built-in image generation tool did not expose a model identifier.",
        "provenanceLimit": "Native dimensions and hashes are measured from supplied generated PNGs; this script does not make image-generation calls.",
        "composition": {"method": "minimum-error seam with narrow feathering", "outerCropPerSide": HALO,
                        "helpersFile": str(PIPELINE), "helpersSha256": sha256(PIPELINE),
                        "helpers": ["_match_color", "_append_with_minimum_seam"],
                        "colorTreatment": "25% of the existing statistics-based match, with pre-blend per-channel shifts capped at 16/255; maximum final shift 4/255.",
                        "guidePixelsCompositedIntoFinal": False,
                        "sourceUpsampling": "Only the layout guide is enlarged. Refined patches are never enlarged; larger patches are downsampled.",
                        "additionalSharpening": False},
        "refinements": refinements, "colorAdjustments": color_records,
        "master": master_record, "preview": preview_record, "tiles": tile_records,
        "nativeScaleQaCrops": qa_records, "seamDiagnostics": seam_diagnostics(final_pixels),
        "verification": {"jsonValid": True, "promptsNonempty": True,
                         "refinedMinimumNativeSize": PATCH, "tileReassemblyPixelsEqualMaster": False},
    }
    write_json("manifest.json", manifest)
    verify()
    print(f"Delivered {MASTER}x{MASTER} master, {GRID * GRID} lossless tiles, and 9 unscaled QA crops.")


def verify_file_record(record: dict) -> Image.Image:
    path = output_path(record["file"])
    if sha256(path) != record["sha256"]:
        raise ValueError(f"Output hash mismatch: {record['file']}")
    with Image.open(path) as image:
        image.load()
        if image.format != "PNG" or image.mode != "RGB" or image.size != (record["width"], record["height"]):
            raise ValueError(f"Output format/size mismatch: {record['file']}")
        return image.copy()


def verify() -> None:
    load_prepare_manifest()
    manifest = json.loads(output_path("manifest.json").read_text(encoding="utf-8-sig"))
    if manifest.get("finalArtUpscaled") is not False or manifest.get("runtimeIntegration") is not False:
        raise ValueError("Manifest must disclose no final-art enlargement and no runtime integration.")
    if manifest.get("masterSize") != {"width": MASTER, "height": MASTER}:
        raise ValueError("Manifest master dimensions mismatch.")
    current_refinements = inspect_refinements()
    if current_refinements != manifest.get("refinements"):
        raise ValueError("Refined source/provenance changed after assembly.")
    master = verify_file_record(manifest["master"])
    if master.size != (MASTER, MASTER):
        raise ValueError("Master size mismatch.")
    master_pixels = np.asarray(master)
    master_rgb_sha = hashlib.sha256(master_pixels.tobytes()).hexdigest()
    if master_rgb_sha != manifest["master"]["decodedRgbSha256"]:
        raise ValueError("Master decoded RGB hash mismatch.")
    expected_tiles = [f"Tiles/{name}" for _, _, name in entries()]
    if [record.get("file") for record in manifest.get("tiles", [])] != expected_tiles:
        raise ValueError("Manifest tiles are not the exact row-major set.")
    actual_tile_names = {path.name for path in output_path("Tiles").glob("*.png")}
    if actual_tile_names != {name for _, _, name in entries()}:
        raise ValueError("Tile folder is not the exact expected PNG set.")
    reassembled = np.zeros_like(master_pixels)
    for (row, column, _), record in zip(entries(), manifest["tiles"]):
        tile = verify_file_record(record)
        x, y = (column - 1) * CORE, (row - 1) * CORE
        expected_bounds = {"x": x, "y": y, "width": CORE, "height": CORE}
        if tile.size != (CORE, CORE) or record.get("pixelBounds") != expected_bounds:
            raise ValueError("Tile bounds/dimensions mismatch.")
        reassembled[y:y + CORE, x:x + CORE] = np.asarray(tile)
    if not np.array_equal(master_pixels, reassembled):
        raise ValueError("Tiles do not reassemble to the exact master pixels.")
    preview = verify_file_record(manifest["preview"])
    if preview.size != (2048, 2048):
        raise ValueError("Preview size mismatch.")
    expected_preview = np.asarray(master.resize((2048, 2048), Image.Resampling.LANCZOS))
    if not np.array_equal(np.asarray(preview), expected_preview):
        raise ValueError("Preview does not match the prescribed master downsample.")
    if len(manifest.get("nativeScaleQaCrops", [])) != 9:
        raise ValueError("Expected nine unscaled QA crops.")
    for record in manifest["nativeScaleQaCrops"]:
        image = verify_file_record(record)
        bounds = record["pixelBounds"]
        x, y, width, height = bounds["x"], bounds["y"], bounds["width"], bounds["height"]
        if record.get("resampled") is not False or record.get("scale") != 1.0:
            raise ValueError("QA crops must retain native scale.")
        if not np.array_equal(np.asarray(image), master_pixels[y:y + height, x:x + width]):
            raise ValueError("QA crop differs from the exact master pixels.")
    verification = {"verifiedAtUtc": datetime.now(timezone.utc).isoformat(),
                    "jsonValid": True, "promptsNonempty": True,
                    "rawNativeDimensionsAndHashesVerified": True,
                    "allFinalPatchesAtLeast1254": PATCH == 1254,
                    "finalArtUpscaled": False, "runtimeIntegration": False,
                    "tileCount": GRID * GRID, "masterWidth": MASTER, "masterHeight": MASTER,
                    "tileReassemblyPixelsEqualMaster": True,
                    "masterDecodedRgbSha256": master_rgb_sha,
                    "reassembledTilesDecodedRgbSha256": hashlib.sha256(reassembled.tobytes()).hexdigest(),
                    "previewPixelsMatchDownsample": True, "nativeScaleQaCropsMatchMaster": True}
    manifest["verification"] = verification
    write_json("manifest.json", manifest)
    write_json("verification.json", verification)
    print("Verification passed: sources/prompts, PNG sizes/hashes, exact tile reassembly, preview, and native QA crops.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "assemble", "verify"))
    args = parser.parse_args()
    {"prepare": prepare, "assemble": assemble, "verify": verify}[args.command]()


if __name__ == "__main__":
    main()
