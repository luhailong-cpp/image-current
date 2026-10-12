"""Joint native-pixel assembly of r05_c04/r05_c05/r06_c04/r06_c05.

  python assemble_2x2.py --preflight
  python assemble_2x2.py --self-check
  python assemble_2x2.py --all-seams
  python assemble_2x2.py --preflight --seam-overrides joint-qa/south-row-core-cut.json

All 64 selected native sources are required for assembly. Preflight is read-only
and reports missing sources. Output is one 8192-square RGB candidate, four exact
4096-square splits, an exact per-pixel source-index map, provenance, and native
seam QA crops. No selection, progress, acceptance, or source files are modified.
No scaling, interpolation, blending, feathering, warping, or recoloring is used.
Existing per-tile visual acceptance does not transfer to this new joint assembly.
Overrides are disabled unless --seam-overrides is supplied. Only an explicitly
configured vertical row/leftColumn seam can use a fixed core-center cut; all
other seams keep minimum-error selection. Horizontal overrides are not supported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

import assemble_native as native

ZONE = Path(__file__).resolve().parent
TILES = (("r05_c04", "r05_c05"), ("r06_c04", "r06_c05"))
GRID, CORE, HALO = 8, native.CORE, native.HALO
PATCH, OVERLAP, SIZE = native.PATCH, native.OVERLAP, 8192
WORLD_BOX = [12288, 16384, 20480, 24576]
OUTPUT_ROOT = ZONE / "joint-2x2-r05_c04-r06_c05"


def validate_override_specs(entries, grid=GRID, core=CORE, halo=HALO):
    """Validate zero-based local coordinates; never silently ignore a bad entry."""
    if not isinstance(entries, list):
        raise ValueError("overrides must be an array")
    normalized, seen, seen_ids = [], set(), set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or entry.get("axis") != "vertical":
            raise ValueError("Only vertical row/leftColumn overrides are supported")
        row, left = entry.get("row"), entry.get("leftColumn")
        if type(row) is not int or type(left) is not int or not (0 <= row < grid and 0 <= left < grid - 1):
            raise ValueError("Override row/leftColumn must be zero-based integers inside the joint grid")
        if "rightColumn" in entry and (type(entry["rightColumn"]) is not int or entry["rightColumn"] != left + 1):
            raise ValueError("rightColumn must be leftColumn + 1")
        if entry.get("mode") != "core-center":
            raise ValueError("Only the fixed core-center override mode is supported")
        if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            raise ValueError("Every override needs a nonempty reason")
        identifier = entry.get("id", f"vertical-r{row}-c{left}")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in seen_ids or (row, left) in seen:
            raise ValueError("Override IDs and row/leftColumn coordinates must be unique")
        expected = entry.get("expectedSourceSha256")
        if not isinstance(expected, dict) or set(expected) != {"left", "right"}:
            raise ValueError("Bind each override to expectedSourceSha256.left and .right")
        if any(not isinstance(v, str) or len(v) != 64 or any(c not in "0123456789abcdef" for c in v) for v in expected.values()):
            raise ValueError("Expected source hashes must be lowercase SHA-256 strings")
        world_x = WORLD_BOX[0] + (left + 1) * core
        if "worldSeamX" in entry and (type(entry["worldSeamX"]) is not int or entry["worldSeamX"] != world_x):
            raise ValueError("worldSeamX disagrees with row/leftColumn geometry")
        seen.add((row, left)); seen_ids.add(identifier)
        normalized.append({**entry, "id": identifier, "configurationEntryIndex": index,
                           "rightColumn": left + 1, "overlapCutX": halo,
                           "worldSeamX": world_x,
                           "worldFullNativeYRange": [WORLD_BOX[1] + row * core - halo, WORLD_BOX[1] + (row + 1) * core + halo],
                           "worldCoreYRange": [WORLD_BOX[1] + row * core, WORLD_BOX[1] + (row + 1) * core],
                           "leftNativeExclusiveStopX": core + halo, "rightNativeInclusiveStartX": halo,
                           "rowStripPathLength": core + 2 * halo,
                           "scope": "full native row strip before the unchanged minimum-error joins between rows"})
    return normalized


def load_seam_overrides(value):
    if value is None:
        return {"explicitlyEnabled": False, "configuration": None, "overrides": []}
    path = Path(value)
    path = native.within(path if path.is_absolute() else ZONE / path, ZONE)
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(data, dict) or data.get("schemaVersion") != 1 or data.get("coordinateSystem") != "joint-8x8-zero-based":
        raise ValueError("Unsupported seam override schema or coordinate system")
    entries = validate_override_specs(data.get("overrides"))
    configuration = {"file": str(path), "sha256": hashlib.sha256(raw).hexdigest()}
    for entry in entries:
        evidence = entry.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError("Every override needs evidence file/hash references")
        verified = []
        for ref in evidence:
            if not isinstance(ref, dict) or not isinstance(ref.get("file"), str):
                raise ValueError("Invalid override evidence reference")
            ref_path = Path(ref["file"])
            ref_path = native.within(ref_path if ref_path.is_absolute() else ZONE / ref_path, ZONE)
            if not ref_path.is_file() or native.sha(ref_path) != ref.get("sha256"):
                raise ValueError(f"Override evidence missing or changed: {ref_path}")
            verified.append({"file": str(ref_path), "sha256": ref["sha256"]})
        entry["evidence"] = verified
        entry["configuration"] = configuration
    return {"explicitlyEnabled": True, "configuration": configuration, "overrides": entries}


def bind_override_sources(overrides, sources):
    by_position = {(s["globalPatchRow"] - 1, s["globalPatchColumn"] - 1): s for s in sources}
    for entry in overrides["overrides"]:
        bound = {}
        for side, column in (("left", entry["leftColumn"]), ("right", entry["rightColumn"])):
            source = by_position.get((entry["row"], column))
            if source is None:
                bound[side] = {"status": "selected_source_missing"}
                continue
            if source["sha256"] != entry["expectedSourceSha256"][side]:
                raise ValueError(f"Override {entry['id']} does not match current {side} source; review and supply a new explicit configuration")
            bound[side] = {"status": "matched", "sourceIndex": source["sourceIndex"],
                           "file": source["file"], "sha256": source["sha256"],
                           "globalId": source["globalId"], "tile": source["tile"], "localPatchId": source["localPatchId"]}
        entry["boundSources"] = bound
    return overrides


def snapshot_selection(tile_dir):
    path = tile_dir / "selection.json"
    if not path.exists():
        return {"file": str(path), "exists": False, "sha256": None, "entries": {},
                "fallbackPolicy": "unlisted logical IDs use native/<logical-id>.png"}
    raw = path.read_bytes()
    selection = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(selection, dict):
        raise ValueError(f"Selection is not an object: {path}")
    return {"file": str(path), "exists": True,
            "sha256": hashlib.sha256(raw).hexdigest(), "entries": selection,
            "fallbackPolicy": "unlisted logical IDs use native/<logical-id>.png"}


def collect_sources():
    arrays, records, missing, tiles = {}, [], [], []
    for tile_row, names in enumerate(TILES):
        for tile_column, name in enumerate(names):
            tile_dir = native.within(ZONE / name, ZONE)
            before = snapshot_selection(tile_dir)
            coordinates_path = tile_dir / "coordinates.json"
            if not coordinates_path.exists():
                missing.extend(f"{name}/s{r:02d}_{c:02d}" for r in range(1, 5) for c in range(1, 5))
                tiles.append({"tile": name, "status": "not_initialized",
                              "selectionSnapshot": before})
                continue
            validated_dir, world_box = native.validate_tile(name)
            local_arrays, local_records, local_missing = native.load_sources(validated_dir, world_box)
            after = snapshot_selection(tile_dir)
            if before != after:
                raise RuntimeError(f"Selection changed while reading {name}; rerun to obtain a coherent snapshot")
            for source in local_records:
                row, column = source["row"] - 1, source["column"] - 1
                source_path = Path(source["file"]).resolve()
                value = before["entries"].get(source["id"], str(tile_dir / "native" / (source["id"] + ".png")))
                value_path = Path(value)
                selected = native.within(value_path if value_path.is_absolute() else tile_dir / value_path, tile_dir)
                if selected != source_path:
                    raise ValueError(f"Loaded source disagrees with selection snapshot: {name}/{source['id']}")
                if not (source_path.stem == source["id"] or source_path.stem.startswith(source["id"] + "_")):
                    raise ValueError(f"Selected source belongs to a different logical patch: {source_path}")
                global_row, global_column = tile_row * 4 + row, tile_column * 4 + column
                source_index = global_row * GRID + global_column + 1
                arrays[global_row, global_column] = local_arrays[row, column]
                records.append({
                    **source, "tile": name, "localPatchId": source["id"],
                    "globalId": f"g{global_row + 1:02d}_{global_column + 1:02d}",
                    "globalPatchRow": global_row + 1, "globalPatchColumn": global_column + 1,
                    "jointCorePasteXY": [global_column * CORE, global_row * CORE],
                    "sourceIndex": source_index,
                    "selectionWasExplicit": source["id"] in before["entries"],
                })
            missing.extend(f"{name}/{pid}" for pid in local_missing)
            tiles.append({"tile": name, "tileWorldBox": world_box,
                          "coordinatesRecord": native.evidence_file(coordinates_path, tile_dir),
                          "selectionSnapshot": before,
                          "selectedSourcesValidated": len(local_records),
                          "missingNativePatches": local_missing})
    records.sort(key=lambda source: source["sourceIndex"])
    for tile in tiles:
        if snapshot_selection(ZONE / tile["tile"]) != tile["selectionSnapshot"]:
            raise RuntimeError(f"Selection changed during the four-tile read: {tile['tile']}; rerun")
    return arrays, records, missing, tiles


def append_labels(left, right, seam, overlap):
    if left.shape[0] != right.shape[0] or len(seam) != left.shape[0]:
        raise ValueError("Ownership strip dimensions disagree with the RGB seam")
    if np.any(seam < 0) or np.any(seam >= overlap):
        raise ValueError("Recorded seam escapes its overlap")
    choose_right = np.arange(overlap)[None, :] >= seam[:, None]
    joined = np.where(choose_right, right[:, :overlap], left[:, -overlap:])
    return np.concatenate((left[:, :-overlap], joined, right[:, overlap:]), axis=1)


def append_with_recorded_seam(base, patch, seam, overlap):
    if base.shape[0] != patch.shape[0] or seam.shape != (base.shape[0],):
        raise ValueError("Recorded seam dimensions disagree with native strips")
    if not (0 < overlap <= min(base.shape[1], patch.shape[1])) or np.any(seam < 0) or np.any(seam >= overlap):
        raise ValueError("Recorded seam escapes native overlap")
    left, right = base[:, -overlap:], patch[:, :overlap]
    choose_right = np.arange(overlap)[None, :] >= seam[:, None]
    return np.concatenate((base[:, :-overlap], np.where(choose_right[..., None], right, left), patch[:, overlap:]), axis=1)


def assemble_grid(arrays, grid=GRID, core=CORE, halo=HALO, overrides=None):
    """Use exactly the existing RGB binary-cut algorithm, with parallel labels."""
    patch, overlap = core + 2 * halo, 2 * halo
    extended, output_size = grid * core + 2 * halo, grid * core
    expected = {(r, c) for r in range(grid) for c in range(grid)}
    if set(arrays) != expected:
        raise ValueError(f"Joint assembly requires all {grid * grid} grid sources")
    override_list = validate_override_specs(overrides or [], grid, core, halo)
    override_map = {(entry["row"], entry["leftColumn"]): entry for entry in override_list}
    strips, label_strips, paths = [], [], []
    for row in range(grid):
        strip = arrays[row, 0]
        if strip.shape != (patch, patch, 3) or strip.dtype != np.uint8:
            raise ValueError("All sources must have matching native RGB uint8 dimensions")
        labels = np.full((patch, patch), row * grid + 1, np.uint8)
        for column in range(1, grid):
            incoming = arrays[row, column]
            if incoming.shape != (patch, patch, 3) or incoming.dtype != np.uint8:
                raise ValueError("All sources must have matching native RGB uint8 dimensions")
            override = override_map.get((row, column - 1))
            if override is None:
                strip, seam = native.append_with_minimum_seam(strip, incoming, overlap)
                metadata = {"policy": "minimum-error"}
            else:
                seam = np.full(patch, halo, dtype=np.int32)
                strip = append_with_recorded_seam(strip, incoming, seam, overlap)
                metadata = {"policy": "explicit-core-center-override", "override": override}
            incoming_labels = np.full((patch, patch), row * grid + column + 1, np.uint8)
            labels = append_labels(labels, incoming_labels, seam, overlap)
            paths.append({"axis": "x", "patchRow": row + 1, "nextPatchColumn": column + 1,
                          "overlapPath": seam.tolist(), **metadata})
        assert strip.shape == (patch, extended, 3)
        strips.append(strip)
        label_strips.append(labels)
    combined, ownership = strips[0].transpose(1, 0, 2), label_strips[0].T
    for row in range(1, grid):
        combined, seam = native.append_with_minimum_seam(combined, strips[row].transpose(1, 0, 2), overlap)
        ownership = append_labels(ownership, label_strips[row].T, seam, overlap)
        paths.append({"axis": "y", "nextPatchRow": row + 1, "overlapPath": seam.tolist(), "policy": "minimum-error"})
    combined, ownership = combined.transpose(1, 0, 2), ownership.T
    assert combined.shape == (extended, extended, 3)
    return (combined[halo:halo + output_size, halo:halo + output_size].copy(),
            ownership[halo:halo + output_size, halo:halo + output_size].copy(), paths)


def replay_recorded_paths(arrays, paths, grid=GRID, core=CORE, halo=HALO):
    """Reconstruct RGB from raw sources and serialized cuts, without optimization."""
    path_map = {}
    for record in paths:
        if record["axis"] == "x":
            key = ("x", record["patchRow"], record["nextPatchColumn"])
        elif record["axis"] == "y":
            key = ("y", record["nextPatchRow"])
        else:
            raise ValueError("Unknown recorded path axis")
        if key in path_map:
            raise ValueError("Duplicate recorded path")
        path_map[key] = np.asarray(record["overlapPath"], dtype=np.int32)
    if len(path_map) != grid * (grid - 1) + grid - 1:
        raise ValueError("Recorded path set is incomplete")
    strips = []
    for row in range(grid):
        strip = arrays[row, 0]
        for column in range(1, grid):
            strip = append_with_recorded_seam(strip, arrays[row, column], path_map["x", row + 1, column + 1], 2 * halo)
        strips.append(strip)
    pixels = strips[0].transpose(1, 0, 2)
    for row in range(1, grid):
        pixels = append_with_recorded_seam(pixels, strips[row].transpose(1, 0, 2), path_map["y", row + 1], 2 * halo)
    pixels = pixels.transpose(1, 0, 2)
    return pixels[halo:halo + grid * core, halo:halo + grid * core].copy()


def verify_exact_pixels(pixels, ownership, arrays, grid=GRID, core=CORE, halo=HALO):
    """Verify every output pixel equals the indexed source at its world position."""
    size, patch = grid * core, core + 2 * halo
    if pixels.shape != (size, size, 3) or ownership.shape != (size, size):
        raise AssertionError("Output or source-index dimensions are incorrect")
    if ownership.min() < 1 or ownership.max() > grid * grid:
        raise AssertionError("Output contains an invalid source index")
    counts, total = [], 0
    for row in range(grid):
        for column in range(grid):
            index = row * grid + column + 1
            x0, y0 = column * core - halo, row * core - halo
            left, top, right, bottom = max(0, x0), max(0, y0), min(size, x0 + patch), min(size, y0 + patch)
            mask = ownership[top:bottom, left:right] == index
            generated = arrays[row, column][top - y0:bottom - y0, left - x0:right - x0]
            assembled = pixels[top:bottom, left:right]
            if not np.array_equal(assembled[mask], generated[mask]):
                raise AssertionError(f"Pixel provenance mismatch for source {index}")
            count = int(np.count_nonzero(mask))
            total += count
            counts.append({"sourceIndex": index, "outputPixels": count})
    if total != size * size:
        raise AssertionError("An output source index names pixels outside its native world footprint")
    return {"status": "passed", "method": "all output RGB pixels compared to indexed native source at same world coordinate",
            "pixelsVerified": total, "pixelScale": 1, "sourceCounts": counts,
            "visualQA": False}


def qa_specs(all_seams=False, core=CORE, grid=GRID, half_width=160):
    """External tile joins have 16 segments and 13 distinct patch intersections."""
    boundary = grid // 2 * core
    positions = range(core, grid * core, core)
    specs = []
    for axis in ("x", "y"):
        for position in positions:
            if not all_seams and position != boundary:
                continue
            for section in range(grid):
                start = section * core
                box = ([position - half_width, start, position + half_width, start + core] if axis == "x"
                       else [start, position - half_width, start + core, position + half_width])
                specs.append({"name": f"seam-{axis}{position}-segment{section + 1:02d}",
                              "cropLTRB": box, "rotationCCW90": axis == "x", "kind": "seam_segment",
                              "scope": "between_tiles" if position == boundary else "within_tile"})
    for y in positions:
        for x in positions:
            if not all_seams and x != boundary and y != boundary:
                continue
            specs.append({"name": f"junction-x{x}-y{y}",
                          "cropLTRB": [x - half_width, y - half_width, x + half_width, y + half_width],
                          "rotationCCW90": False, "kind": "junction",
                          "scope": "four_tile_center" if x == y == boundary else
                                   ("on_tile_boundary" if x == boundary or y == boundary else "within_tile")})
    return specs


def write_qa(image, output_ref, directory, all_seams):
    qa = []
    for spec in qa_specs(all_seams):
        crop = image.crop(spec["cropLTRB"])
        if spec["rotationCCW90"]:
            crop = crop.transpose(Image.Transpose.ROTATE_90)
        ref = native.save_png(crop, directory / (spec["name"] + ".png"))
        qa.append({**spec, **ref, "derivedFrom": output_ref, "sourceResampled": False,
                   "nativePixelScale": 1, "actuallyViewed": False, "visualVerdict": "pending",
                   "formalAccepted": False})
    return qa


def script_evidence():
    return [{"file": str(p), "sha256": native.sha(p)}
            for p in (Path(__file__).resolve(), Path(native.__file__).resolve())]


def global_overlap_diagnostics(arrays):
    diagnostics = native.overlap_diagnostics(arrays)
    for entry in diagnostics:
        entry["fromGlobalId"] = "g" + entry.pop("from")[1:]
        entry["toGlobalId"] = "g" + entry.pop("to")[1:]
    return diagnostics


def reuse_verified(manifest_path):
    manifest = native.read_json(manifest_path)
    references = [manifest["output"], manifest["sourceIndexMap"], *manifest["splitTiles"], *manifest["qa"]]
    for ref in references:
        path = native.within(Path(ref["file"]), manifest_path.parent)
        if not path.is_file() or native.sha(path) != ref["sha256"]:
            raise ValueError(f"Existing output is incomplete or modified: {path}")
    manifest_ref = {"file": str(manifest_path), "sha256": native.sha(manifest_path)}
    for ref in [manifest["output"], *manifest["splitTiles"]]:
        derivation_path = Path(ref["file"]).with_suffix(".png.derivation.json")
        if not derivation_path.is_file():
            raise ValueError(f"Existing output lacks derivation evidence: {derivation_path}")
        derivation = native.read_json(derivation_path)
        if derivation.get("assemblyManifest") != manifest_ref or derivation.get("output") != ref:
            raise ValueError(f"Existing derivation disagrees with the assembly: {derivation_path}")
    return {"status": manifest["status"], "reusedExistingAssembly": True,
            "output": manifest["output"], "assemblyManifest": str(manifest_path),
            "splitTiles": manifest["splitTiles"], "qaFiles": len(manifest["qa"]),
            "pixelProvenanceVerification": manifest["pixelProvenanceVerification"]["status"],
            "formalAcceptedCount": 0, "writes": 0}


def build(arrays, sources, tiles, all_seams, overrides=None):
    overrides = overrides if overrides is not None else load_seam_overrides(None)
    scripts = script_evidence()
    identity = {"sources": sources, "tileSnapshots": tiles, "scripts": scripts,
                "allSeamsQA": all_seams, "method": "joint-8x8-minimum-error",
                "seamOverrides": overrides}
    signature = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:16]
    directory = native.within(OUTPUT_ROOT / signature, ZONE)
    manifest_path = directory / "joint-assembly.json"
    if manifest_path.exists():
        return reuse_verified(manifest_path)
    pixels, ownership, paths = assemble_grid(arrays, overrides=overrides["overrides"])
    verification = verify_exact_pixels(pixels, ownership, arrays)
    image = Image.fromarray(pixels)
    output = native.save_png(image, directory / "joint-8192.png")
    source_map = native.save_png(Image.fromarray(ownership), directory / "native-source-index.png")
    source_map["meaning"] = "grayscale value 1..64 identifies nativeSources[].sourceIndex; no palette or resampling"
    split_tiles = []
    for row, names in enumerate(TILES):
        for column, tile in enumerate(names):
            box = [column * 4096, row * 4096, (column + 1) * 4096, (row + 1) * 4096]
            ref = native.save_png(image.crop(box), directory / "tiles" / (tile + "-joint-4096.png"))
            ref.update({"tile": tile, "cropLTRB": box,
                        "tileWorldBox": [WORLD_BOX[0] + box[0], WORLD_BOX[1] + box[1],
                                         WORLD_BOX[0] + box[2], WORLD_BOX[1] + box[3]],
                        "operation": "exact integer crop from the one joint 8192 candidate",
                        "sourceResampled": False, "formalAccepted": False})
            split_tiles.append(ref)
    qa = write_qa(image, output, directory / "qa", all_seams)
    status = "joint_candidate_pending_visual_review"
    manifest = {
        "schemaVersion": 1, "createdAtUtc": native.now(), "status": status,
        "tileArrangement": [list(row) for row in TILES], "jointWorldBox": WORLD_BOX,
        "artCanvasPixels": [65536, 65536], "grid": [GRID, GRID], "pixels": [SIZE, SIZE],
        "nativePixels": [PATCH, PATCH], "corePixels": CORE, "haloPixels": HALO,
        "overlapPixels": OVERLAP, "origin": "top-left", "coordinates": "half-open LTRB",
        "method": "minimum-error binary source cuts except explicitly recorded fixed core-center vertical overrides; complete rows then all rows",
        "outerCropLTRB": [HALO, HALO, HALO + SIZE, HALO + SIZE],
        "sourceResampled": False, "sourceUpscaled": False, "colorMatching": False,
        "opticalFlow": False, "feathering": False, "blur": False,
        "seamPathCoordinates": "0-based position within each 230px overlap; x paths indexed by 1254 native y, y paths by 8422 extended x",
        "seamPaths": paths, "seamOverrides": overrides, "scripts": scripts, "tileSnapshots": tiles,
        "nativeSources": sources, "selectedNativeSourceCount": len(sources),
        "output": output, "sourceIndexMap": source_map, "splitTiles": split_tiles,
        "pixelProvenanceVerification": verification,
        "overlapDiagnostics": global_overlap_diagnostics(arrays),
        "qa": qa,
        "visualQA": {"status": "pending", "actuallyViewed": False,
                     "betweenTileSeamSegments": 16, "tileBoundaryJunctions": 13,
                     "fourTileCenterJunctionIncluded": True, "allInternalSeamsExported": all_seams,
                     "priorTileQAApplicable": False,
                     "note": "A global seam can differ from a former single-tile seam. Review these new outputs. Outer sides of the 2x2 region still require real neighbors."},
        "formalAccepted": False, "formalAcceptedCount": 0,
        "runtimeIntegration": False, "clientMappingValidated": False, "capacity5000Validated": False,
    }
    pending_manifest = directory / "joint-assembly.pending.json"
    native.write_json(pending_manifest, manifest)
    manifest_ref = {"file": str(manifest_path), "sha256": native.sha(pending_manifest)}
    derivation = {"schemaVersion": 1, "createdAtUtc": manifest["createdAtUtc"], "status": status,
                  "assemblyManifest": manifest_ref, "sourceResampled": False, "formalAccepted": False,
                  "actualModel": None, "actualQuality": None,
                  "modelQualityEvidence": "derived output has no generation call; native source evidence is preserved in the manifest"}
    native.write_json(Path(output["file"]).with_suffix(".png.derivation.json"),
                      {**derivation, "output": output,
                       "operation": "joint native pixel assembly; exact per-pixel origins in native-source-index.png"})
    for split in split_tiles:
        native.write_json(Path(split["file"]).with_suffix(".png.derivation.json"),
                          {**derivation, "output": split, "derivedFrom": output,
                           "operation": "exact integer crop", "cropLTRB": split["cropLTRB"]})
    pending_manifest.replace(manifest_path)
    return {"status": status, "output": output, "assemblyManifest": str(manifest_path),
            "splitTiles": split_tiles, "qaFiles": len(qa),
            "pixelProvenanceVerification": verification["status"], "pixelsVerified": verification["pixelsVerified"],
            "formalAcceptedCount": 0, "reusedExistingAssembly": False}


def self_check():
    grid, core, halo = 8, 12, 3
    rng = np.random.default_rng(8102026)
    arrays = {(r, c): rng.integers(0, 256, (core + 2 * halo, core + 2 * halo, 3), np.uint8)
              for r in range(grid) for c in range(grid)}
    pixels, owners, paths = assemble_grid(arrays, grid, core, halo)
    checked = verify_exact_pixels(pixels, owners, arrays, grid, core, halo)
    assert checked["pixelsVerified"] == 96 * 96
    assert len(paths) == grid * (grid - 1) + grid - 1
    for path in paths:
        seam = np.asarray(path["overlapPath"])
        assert np.all(np.abs(np.diff(seam)) <= 1)
        assert seam.min() >= 0 and seam.max() < 2 * halo
    assert np.array_equal(replay_recorded_paths(arrays, paths, grid, core, halo), pixels)
    spec = {"id": "self-check-center", "axis": "vertical", "row": 7, "leftColumn": 5,
            "mode": "core-center", "reason": "synthetic straight source-boundary test",
            "expectedSourceSha256": {"left": "0" * 64, "right": "1" * 64}}
    hard_pixels, hard_owners, hard_paths = assemble_grid(arrays, grid, core, halo, overrides=[spec])
    hard_checked = verify_exact_pixels(hard_pixels, hard_owners, arrays, grid, core, halo)
    assert hard_checked["pixelsVerified"] == grid * core * grid * core
    assert np.array_equal(replay_recorded_paths(arrays, hard_paths, grid, core, halo), hard_pixels)
    overridden = [p for p in hard_paths if p["policy"] == "explicit-core-center-override"]
    assert len(overridden) == 1 and overridden[0]["patchRow"] == 8 and overridden[0]["nextPatchColumn"] == 7
    assert overridden[0]["overlapPath"] == [halo] * (core + 2 * halo)
    for before, after in zip(paths, hard_paths):
        if after["policy"] == "explicit-core-center-override":
            continue
        assert after["policy"] == "minimum-error"
        if after["axis"] == "x":
            assert before["overlapPath"] == after["overlapPath"]
    # Test every native row of the two-source pair, including both halo ends.
    hard_pair = append_with_recorded_seam(arrays[7, 5], arrays[7, 6], np.full(core + 2 * halo, halo), 2 * halo)
    assert np.array_equal(hard_pair, np.concatenate((arrays[7, 5][:, :core + halo], arrays[7, 6][:, halo:]), axis=1))
    assert np.all(hard_owners[7 * core + halo:, 6 * core - 1] == 62)
    assert np.all(hard_owners[7 * core + halo:, 6 * core] == 63)
    bad_changes = [{"row": -1}, {"row": 8}, {"row": True}, {"row": 1.5},
                   {"leftColumn": -1}, {"leftColumn": 7}, {"leftColumn": False}, {"leftColumn": "5"},
                   {"rightColumn": 7}, {"axis": "horizontal"}, {"mode": "blend"},
                   {"worldSeamX": 1}, {"reason": ""}, {"expectedSourceSha256": {"left": "bad", "right": "1" * 64}}]
    invalid_count = 0
    for entries in [[{**spec, **change}] for change in bad_changes] + [[spec, spec]]:
        try:
            validate_override_specs(entries, grid, core, halo)
        except ValueError:
            invalid_count += 1
        else:
            raise AssertionError("Invalid or duplicate override was accepted")
    assert load_seam_overrides(None) == {"explicitlyEnabled": False, "configuration": None, "overrides": []}
    try:
        bind_override_sources({"overrides": validate_override_specs([spec], grid, core, halo)},
                              [{"globalPatchRow": 8, "globalPatchColumn": 6, "sha256": "f" * 64}])
    except ValueError:
        pass
    else:
        raise AssertionError("An override for a different source hash was accepted")
    # A deliberate pixel change must be detected independently of cut construction.
    corrupted = pixels.copy()
    corrupted[27, 31, 0] ^= 1
    try:
        verify_exact_pixels(corrupted, owners, arrays, grid, core, halo)
    except AssertionError:
        pass
    else:
        raise AssertionError("Provenance verifier failed to detect an altered pixel")
    wrong_owner = owners.copy()
    wrong_owner[0, 0] = 64
    try:
        verify_exact_pixels(pixels, wrong_owner, arrays, grid, core, halo)
    except AssertionError:
        pass
    else:
        raise AssertionError("Provenance verifier accepted an impossible source position")
    external, full = qa_specs(False), qa_specs(True)
    assert len(external) == 29 and len(full) == 161
    assert sum(s["scope"] == "four_tile_center" for s in external) == 1
    assert sum(s["kind"] == "seam_segment" for s in external) == 16
    # Exact quadrant crops cover the joint output once, with no inserted seam pixels.
    reconstructed = np.concatenate(
        [np.concatenate([pixels[r * 48:(r + 1) * 48, c * 48:(c + 1) * 48] for c in range(2)], axis=1)
         for r in range(2)], axis=0)
    assert np.array_equal(reconstructed, pixels)
    return {"selfCheck": "passed", "syntheticSources": 64, "syntheticPixelsVerified": 9216,
            "overrideSyntheticPixelsVerified": hard_checked["pixelsVerified"],
            "recordedPathReplay": "pixel-identical for default and overridden assemblies",
            "fixedCutFullNativePair": "exact left[:, :core+halo] plus right[:, halo:]",
            "onlyConfiguredVerticalCutChanged": True, "invalidOverrideCasesRejected": invalid_count,
            "changedSourceHashRejected": True, "defaultOverridesDisabled": True,
            "corruptedPixelDetected": True, "impossibleSourceIndexDetected": True,
            "externalQAFileCount": 29, "allSeamsQAFileCount": 161, "writes": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--preflight", action="store_true", help="Read-only validation; report missing sources and selection snapshots")
    parser.add_argument("--all-seams", action="store_true", help="Export all 112 seam segments and 49 junctions, including the 29 required between-tile views")
    parser.add_argument("--self-check", action="store_true", help="Small in-memory algorithm/provenance tests; no production sources or writes")
    parser.add_argument("--seam-overrides", help="Explicit override JSON path; relative paths resolve under this northwest directory; no default is auto-loaded")
    args = parser.parse_args()
    if args.self_check:
        result = self_check()
    else:
        overrides = load_seam_overrides(args.seam_overrides)
        arrays, sources, missing, tiles = collect_sources()
        overrides = bind_override_sources(overrides, sources)
        if args.preflight:
            result = {"status": "preflight_only", "sourcesValidated": len(sources),
                      "expectedSources": GRID * GRID, "wouldBeComplete": not missing,
                      "missing": missing, "tileSnapshots": tiles, "writes": 0,
                      "formalAcceptedCount": 0, "seamOverrides": overrides}
        elif missing:
            raise ValueError("64 selected native sources required; missing: " + ", ".join(missing))
        else:
            result = build(arrays, sources, tiles, args.all_seams, overrides)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

