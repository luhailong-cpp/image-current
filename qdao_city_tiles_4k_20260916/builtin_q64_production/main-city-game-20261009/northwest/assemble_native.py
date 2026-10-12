"""Mechanical native-pixel assembly for the northwest zone; no generation or acceptance.

Examples (run with a Python containing Pillow and NumPy):
  python assemble_native.py --preflight
  python assemble_native.py
  python assemble_native.py --method minimum-error
  python assemble_native.py --self-check

Default hard cutting exposes mismatched geometry. Missing cores stay transparent;
only all sixteen validated sources produce a complete 4096-square candidate.
Minimum-error cutting is optional, requires all sixteen sources, and never blends,
warps, resizes, blurs, or changes source colors. All formal acceptance counts are 0.
This script does not update progress.json or any shared/other-zone file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


ZONE = Path(__file__).resolve().parent
GRID, CORE, HALO = 4, 1024, 115
PATCH, OVERLAP, TILE = CORE + 2 * HALO, 2 * HALO, GRID * CORE
EXTENDED = TILE + 2 * HALO


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def within(path: Path, directory: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(directory.resolve())
    except ValueError as exc:
        raise ValueError(f"Path escapes permitted directory: {path}") from exc
    return resolved


def evidence_file(path: Path, tile_dir: Path) -> dict:
    path = within(path, tile_dir)
    if not path.is_file():
        raise ValueError(f"Missing provenance file: {path}")
    return {"file": str(path), "sha256": sha(path)}


def validate_tile(tile: str) -> tuple[Path, list[int]]:
    if not re.fullmatch(r"r\d{2}_c\d{2}", tile):
        raise ValueError("Use a tile name such as r05_c04")
    row, column = int(tile[1:3]), int(tile[5:7])
    if not (1 <= row <= 8 and 1 <= column <= 8):
        raise ValueError("Only northwest rows 1-8 and columns 1-8 are permitted")
    tile_dir = within(ZONE / tile, ZONE)
    x, y = (column - 1) * TILE, (row - 1) * TILE
    box = [x, y, x + TILE, y + TILE]
    coordinates = read_json(tile_dir / "coordinates.json")
    if coordinates.get("tile") != tile or coordinates.get("tileWorldBox") != box:
        raise ValueError("coordinates.json does not match the requested tile")
    if coordinates.get("canvas") != [65536, 65536]:
        raise ValueError("Unexpected artwork canvas in coordinates.json")
    return tile_dir, box


def load_sources(tile_dir: Path, world_box: list[int]):
    arrays, sources, missing = {}, [], []
    coordinates = read_json(tile_dir / "coordinates.json")
    coordinate_entries = {entry["id"]: entry for entry in coordinates["patches"]}
    for row in range(GRID):
        for column in range(GRID):
            patch_id = f"s{row + 1:02d}_{column + 1:02d}"
            selection = read_json(tile_dir / "selection.json") if (tile_dir / "selection.json").exists() else {}
            path = within(Path(selection.get(patch_id, str(tile_dir / "native" / f"{patch_id}.png"))), tile_dir)
            if not path.exists():
                missing.append(patch_id)
                continue
            record_path = path.with_suffix(".png.generation.json")
            record_ref = evidence_file(record_path, tile_dir)
            record = read_json(record_path)
            native_hash = sha(path)
            if record.get("sha256", "").lower() != native_hash:
                raise ValueError(f"Native SHA-256 differs from its generation record: {patch_id}")
            if record.get("route") not in ("builtin", "builtin_image_gen"):
                raise ValueError(f"Unrecognized native generation route: {patch_id}")
            if record.get("resizedAfterGeneration") or record.get("finalArtUpscaled"):
                raise ValueError(f"Source is recorded as resized/upscaled: {patch_id}")
            recorded_path = Path(record["file"])
            if not recorded_path.is_absolute():
                recorded_path = tile_dir / recorded_path
            if within(recorded_path, tile_dir) != path:
                raise ValueError(f"Generation record names a different image: {patch_id}")
            with Image.open(path) as image:
                image.load()
                native_size, native_mode = list(image.size), image.mode
                if image.format != "PNG" or image.size != (PATCH, PATCH):
                    raise ValueError(f"Expected native {PATCH}x{PATCH} PNG, got {native_size}: {patch_id}")
                if [record.get("width"), record.get("height")] != native_size:
                    raise ValueError(f"Recorded dimensions disagree with PNG: {patch_id}")
                rgba = image.convert("RGBA")
                if rgba.getchannel("A").getextrema() != (255, 255):
                    raise ValueError(f"Ground source has transparent pixels: {patch_id}")
                pixels = np.asarray(rgba.convert("RGB")).copy()
            x = world_box[0] + column * CORE
            y = world_box[1] + row * CORE
            core_box = [x, y, x + CORE, y + CORE]
            context_box = [x - HALO, y - HALO, x + CORE + HALO, y + CORE + HALO]
            entry = coordinate_entries.get(patch_id, {})
            if (entry.get("coreWorldBox") != core_box
                    or entry.get("worldBoxWithHalo") != context_box
                    or entry.get("coreCrop") != [HALO, HALO, HALO + CORE, HALO + CORE]):
                raise ValueError(f"Patch coordinates disagree with native placement: {patch_id}")
            version_id = path.stem
            evidence = record.get("evidence", {})
            prompt = evidence_file(Path(record.get("prompt", str(tile_dir / "prompts" / f"{version_id}.txt"))), tile_dir)
            request = evidence_file(Path(evidence.get("request", str(tile_dir / "receipts" / f"{version_id}.request.json"))), tile_dir)
            receipt = evidence_file(Path(evidence.get("receipt", str(tile_dir / "receipts" / f"{version_id}.result.json"))), tile_dir)
            if not Path(prompt["file"]).read_text(encoding="utf-8-sig").strip():
                raise ValueError(f"Empty prompt: {patch_id}")
            arrays[row, column] = pixels
            sources.append({
                "id": patch_id, "row": row + 1, "column": column + 1,
                "file": str(path), "sha256": native_hash,
                "nativePixels": native_size, "nativeMode": native_mode,
                "coreCropLTRB": [HALO, HALO, HALO + CORE, HALO + CORE],
                "tileCorePasteXY": [column * CORE, row * CORE],
                "coreWorldBox": core_box, "worldBoxWithHalo": context_box,
                "generationRecord": record_ref, "prompt": prompt,
                "request": request, "receipt": receipt,
                "route": record["route"], "generatedAt": record.get("generatedAt"),
                "actualModel": record.get("actualModel"),
                "actualQuality": record.get("actualQuality"),
                "modelQualityEvidenceStatus": "copied from source record; assembly verifies no backend selector",
                "recordedReferences": record.get("references", []),
                "referenceVerification": "source record preserved; shared reference images not read by assembly",
                "sourceResampled": False,
            })
    return arrays, sources, missing


def hard_cut(arrays: dict) -> Image.Image:
    canvas = np.zeros((TILE, TILE, 4), dtype=np.uint8)
    for (row, column), pixels in arrays.items():
        x, y = column * CORE, row * CORE
        canvas[y:y + CORE, x:x + CORE, :3] = pixels[HALO:HALO + CORE, HALO:HALO + CORE]
        canvas[y:y + CORE, x:x + CORE, 3] = 255
    return Image.fromarray(canvas)


def minimum_vertical_seam(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    if left.shape != right.shape or left.ndim != 3 or left.shape[2] != 3:
        raise ValueError("Seam inputs must be equal RGB overlap strips")
    difference = left.astype(np.float32) - right.astype(np.float32)
    cost = np.mean(difference * difference, axis=2)
    height, width = cost.shape
    # A mild center penalty discourages edge-hugging but never changes source pixels.
    center = (width - 1) / 2
    typical = float(np.median(cost)) + 1
    cost += (np.abs(np.arange(width) - center) / max(center, 1)) ** 4 * typical * .16
    previous = cost[0].copy()
    backtrack = np.zeros((height, width), dtype=np.int8)
    for y in range(1, height):
        candidates = np.stack((np.r_[np.inf, previous[:-1]], previous,
                               np.r_[previous[1:], np.inf]))
        choice = np.argmin(candidates, axis=0)
        backtrack[y] = choice.astype(np.int8) - 1
        previous = cost[y] + np.take_along_axis(candidates, choice[None, :], axis=0)[0]
    seam = np.empty(height, dtype=np.int32)
    seam[-1] = int(np.argmin(previous))
    for y in range(height - 1, 0, -1):
        seam[y - 1] = seam[y] + int(backtrack[y, seam[y]])
    return seam


def append_with_minimum_seam(base, patch, overlap=OVERLAP):
    if base.shape[0] != patch.shape[0] or not (0 < overlap <= min(base.shape[1], patch.shape[1])):
        raise ValueError("Invalid overlap geometry")
    left, right = base[:, -overlap:], patch[:, :overlap]
    seam = minimum_vertical_seam(left, right)
    choose_right = np.arange(overlap)[None, :] >= seam[:, None]
    joined = np.where(choose_right[..., None], right, left)
    output = np.concatenate((base[:, :-overlap], joined, patch[:, overlap:]), axis=1)
    return output, seam


def minimum_error_assembly(arrays):
    if len(arrays) != GRID * GRID:
        raise ValueError("minimum-error requires sixteen complete sources; use hard for partials")
    strips, paths = [], []
    for row in range(GRID):
        strip = arrays[row, 0]
        for column in range(1, GRID):
            strip, seam = append_with_minimum_seam(strip, arrays[row, column])
            paths.append({"axis": "x", "patchRow": row + 1,
                          "nextPatchColumn": column + 1, "overlapPath": seam.tolist()})
        if strip.shape != (PATCH, EXTENDED, 3):
            raise AssertionError("Wrong row-strip dimensions")
        strips.append(strip)
    combined = strips[0].transpose(1, 0, 2)
    for row in range(1, GRID):
        combined, seam = append_with_minimum_seam(combined, strips[row].transpose(1, 0, 2))
        paths.append({"axis": "y", "nextPatchRow": row + 1, "overlapPath": seam.tolist()})
    combined = combined.transpose(1, 0, 2)
    if combined.shape != (EXTENDED, EXTENDED, 3):
        raise AssertionError("Wrong assembled dimensions")
    return Image.fromarray(combined[HALO:HALO + TILE, HALO:HALO + TILE].copy()), paths


def overlap_diagnostics(arrays):
    metrics = []
    for (row, column), pixels in sorted(arrays.items()):
        for axis, neighbor, first, second in [
            ("x", (row, column + 1), pixels[:, -OVERLAP:], None),
            ("y", (row + 1, column), pixels[-OVERLAP:, :], None),
        ]:
            if neighbor not in arrays:
                continue
            second = arrays[neighbor][:, :OVERLAP] if axis == "x" else arrays[neighbor][:OVERLAP, :]
            difference = np.abs(first.astype(np.int16) - second.astype(np.int16))
            metrics.append({"from": f"s{row + 1:02d}_{column + 1:02d}",
                            "to": f"s{neighbor[0] + 1:02d}_{neighbor[1] + 1:02d}",
                            "axis": axis, "overlapPixels": OVERLAP,
                            "meanAbsoluteDifference": float(difference.mean()),
                            "p95AbsoluteDifference": float(np.percentile(difference, 95)),
                            "diagnosticOnly": True, "visualVerdict": "not_reviewed"})
    return metrics


def save_png(image: Image.Image, path: Path) -> dict:
    path = within(path, ZONE)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.stem + ".writing.png")
    image.save(temporary, format="PNG", optimize=True)
    temporary.replace(path)
    with Image.open(path) as saved:
        saved.load()
        if saved.mode != image.mode or saved.size != image.size or saved.tobytes() != image.tobytes():
            raise AssertionError(f"Saved PNG pixel verification failed: {path}")
    return {"file": str(path), "sha256": sha(path), "pixels": list(image.size), "mode": image.mode}


def write_json(path: Path, value: dict):
    path = within(path, ZONE)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_qa(image: Image.Image, output_ref: dict, directory: Path):
    """24 full-seam segments and 9 junctions, all original-pixel scale."""
    records = []
    def crop(name, box, rotate=False):
        sample = image.crop(box)
        if rotate:
            sample = sample.transpose(Image.Transpose.ROTATE_90)
        entry = save_png(sample, directory / (name + ".png"))
        alpha = sample.convert("RGBA").getchannel("A")
        entry.update({"derivedFrom": output_ref, "cropLTRB": box,
                      "rotationCCW90": rotate, "sourceResampled": False,
                      "nativePixelScale": 1, "fullNativeCoverage": alpha.getextrema() == (255, 255),
                      "actuallyViewed": False, "visualVerdict": "pending", "formalAccepted": False})
        records.append(entry)
    for axis in ("x", "y"):
        for position in (CORE, 2 * CORE, 3 * CORE):
            for section in range(GRID):
                start = section * CORE
                box = ([position - 160, start, position + 160, start + CORE] if axis == "x"
                       else [start, position - 160, start + CORE, position + 160])
                crop(f"internal-{axis}{position}-segment{section + 1:02d}", box, axis == "x")
    for y in (CORE, 2 * CORE, 3 * CORE):
        for x in (CORE, 2 * CORE, 3 * CORE):
            crop(f"junction-x{x}-y{y}", [x - 160, y - 160, x + 160, y + 160])
    return records


def self_check():
    # In-memory only: prove exact hard-core placement and transparent missing area.
    source = np.zeros((PATCH, PATCH, 3), np.uint8)
    source[..., 0] = np.arange(PATCH, dtype=np.uint16)[None, :] % 256
    source[..., 1] = np.arange(PATCH, dtype=np.uint16)[:, None] % 256
    pixels = np.asarray(hard_cut({(1, 2): source}))
    assert np.array_equal(pixels[CORE:2 * CORE, 2 * CORE:3 * CORE, :3], source[HALO:HALO + CORE, HALO:HALO + CORE])
    assert np.count_nonzero(pixels[..., 3]) == CORE * CORE
    assert not pixels[:CORE].any()
    # Verify optional seam output uses only unmodified samples at the same location.
    left = np.arange(8 * 10 * 3, dtype=np.uint8).reshape(8, 10, 3)
    right = (255 - left).copy()
    joined, seam = append_with_minimum_seam(left, right, overlap=4)
    assert joined.shape == (8, 16, 3)
    assert np.array_equal(joined[:, :6], left[:, :6])
    assert np.array_equal(joined[:, 10:], right[:, 4:])
    overlap = joined[:, 6:10]
    assert np.all(np.all(overlap == left[:, -4:], axis=2) | np.all(overlap == right[:, :4], axis=2))
    assert np.all(np.abs(np.diff(seam)) <= 1)
    print(json.dumps({"selfCheck": "passed", "writes": 0, "productionSourcesRead": 0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tile", default="r05_c04")
    parser.add_argument("--method", choices=("hard", "minimum-error"), default="hard")
    parser.add_argument("--preflight", action="store_true", help="Validate sources and provenance without writing")
    parser.add_argument("--self-check", action="store_true", help="Run in-memory checks only; no production files read or written")
    args = parser.parse_args()
    if args.self_check:
        self_check()
        return
    tile_dir, world_box = validate_tile(args.tile)
    arrays, sources, missing = load_sources(tile_dir, world_box)
    count, complete = len(sources), not missing
    counts = {"generatedNativeCount": count, "complete4kCandidateCount": int(complete), "formalAcceptedCount": 0}
    if args.preflight:
        print(json.dumps({"status": "preflight_only", "sourcesValidated": count,
                          "complete4kCandidateCount": 0, "formalAcceptedCount": 0,
                          "wouldBeComplete": complete, "missing": missing, "writes": 0}, indent=2))
        return
    if not count:
        raise ValueError("No validated native sources; no empty preview will be written")
    if args.method == "minimum-error" and not complete:
        raise ValueError("minimum-error requires all sixteen sources; use --method hard for a transparent partial")
    image, paths = (minimum_error_assembly(arrays) if args.method == "minimum-error" else (hard_cut(arrays), []))
    if complete:
        if image.convert("RGBA").getchannel("A").getextrema() != (255, 255):
            raise AssertionError("Complete candidate contains unpainted pixels")
        image = image.convert("RGB")
    if image.size != (TILE, TILE):
        raise AssertionError("Candidate must be exactly 4096 square")
    script_ref = {"file": str(Path(__file__).resolve()), "sha256": sha(Path(__file__))}
    signature = hashlib.sha256(json.dumps({"sources": sources, "method": args.method,
                                           "script": script_ref}, sort_keys=True).encode()).hexdigest()[:12]
    status = "candidate_pending_internal_and_external_visual_review" if complete else "partial_not_complete"
    kind = "candidate" if complete else "partial"
    name = f"{args.tile}-{kind}-{args.method}-{signature}"
    output_ref = save_png(image, tile_dir / "candidate" / (name + ".png"))
    qa = write_qa(image, output_ref, tile_dir / "qa" / name)
    manifest = {
        "schemaVersion": 1, "createdAtUtc": now(), "tile": args.tile, "status": status,
        **counts, "missingNativePatches": missing, "tileWorldBox": world_box,
        "artCanvasPixels": [65536, 65536], "nativePixels": [PATCH, PATCH],
        "corePixels": CORE, "haloPixels": HALO, "internalOverlapPixels": OVERLAP,
        "grid": [GRID, GRID], "origin": "top-left", "coordinates": "half-open LTRB",
        "method": args.method, "sourceResampled": False, "sourceUpscaled": False,
        "colorMatching": False, "opticalFlow": False, "feathering": False,
        "partialPolicy": "Only generated 1024-square cores are opaque; missing cores are transparent and never counted complete",
        "hardCutPolicy": "Each source core [115,115,1139,1139) is pasted at ((column-1)*1024,(row-1)*1024)",
        "minimumErrorPolicy": "Optional binary source selection in 230px overlaps; rows then columns; outer crop [115,115,4211,4211); no interpolation",
        "seamPaths": paths, "seamPathCoordinates": "0-based within each 230px overlap; x joins indexed by native y; y joins indexed by extended x",
        "script": script_ref, "coordinatesRecord": evidence_file(tile_dir / "coordinates.json", tile_dir),
        "nativeSources": sources, "overlapDiagnostics": overlap_diagnostics(arrays),
        "output": output_ref, "qa": qa,
        "visualQA": {"status": "pending", "fullInternalSeams": 6, "nativeSeamSegments": 24,
                     "junctions": 9, "actuallyViewed": False,
                     "externalSeams": "not reviewed; real adjacent tile sources required"},
        "formalAccepted": False, "runtimeIntegration": False,
        "clientMappingValidated": False, "capacity5000Validated": False,
    }
    manifest_path = tile_dir / "candidate" / (name + ".assembly.json")
    write_json(manifest_path, manifest)
    write_json(tile_dir / "candidate" / (name + ".png.derivation.json"), {
        "schemaVersion": 1, "createdAtUtc": manifest["createdAtUtc"], "status": status,
        "operation": args.method + " native-pixel assembly; no resize, registration, color correction, or feathering",
        "output": output_ref, "assemblyManifest": evidence_file(manifest_path, tile_dir),
        "nativeSources": [{"file": s["file"], "sha256": s["sha256"], "nativePixels": s["nativePixels"]} for s in sources],
        **counts, "actualModel": None, "actualQuality": None,
        "modelQualityEvidence": "Derived image has no generation call; per-source values remain in assembly manifest",
    })
    print(json.dumps({"status": status, **counts, "output": output_ref,
                      "assemblyManifest": str(manifest_path), "qaFiles": len(qa),
                      "nextStep": "Review original-pixel internal seams and real external neighbors; no formal acceptance granted"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
