"""Join one explicit 2x2 neighborhood without changing native coordinates.

The four reviewed 4096 cores retain their own interiors. Original native halos
are reconstructed from each root assembly's archived ownership plane. Only the
230-pixel common strips are joined. This is source selection, never painting.

Each output also receives a .connected-projection.json record usable as
apply_native_tile_repair.py --base-record. The child pins connected-cluster.json;
the cluster lists child paths without pinning child hashes, avoiding a cycle.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

import numpy as np
from PIL import Image

import apply_native_tile_repair as repair
import assemble_tile as assembly

ZONE = Path(__file__).resolve().parent
CORE, HALO, PADDED, OVERLAP = 4096, 115, 4326, 230
CLUSTER, PADDED_CLUSTER = 8192, 8422
OPERATION = "same-coordinate connected 2x2 tile boundary selection"
PROJECTION_OPERATION = repair.CONNECTED_PROJECTION_OPERATION


def require(value, message):
    if not value:
        raise ValueError(message)


def pinned(value, base, role):
    return repair.pinned(value, base, role)


def reconstruct_padded(image_path, record_path, seen=None):
    """Verify the final core, then restore ONLY its original recorded halo."""
    core, proof = repair.validate_base(image_path, record_path, seen)
    root_info = pinned(proof["rootAssembly"], record_path.parent, "root assembly")
    root_path = Path(root_info["path"])
    root = repair.read_json(root_path)
    require(root.get("operation") == repair.ASSEMBLY_OPERATION, "Halo source must be a verified native assembly.")
    require(root["tileId"] == proof["tileId"], "Root assembly tile identity differs.")
    provenance = pinned(root["provenance"], root_path.parent, "root padded ownership")
    origin = repair.tile_origin(proof["tileId"])
    padded = np.empty((PADDED, PADDED, 3), dtype=np.uint8)
    sources = root["sources"]
    require(len(sources) == 16, "Root assembly must have exactly16 native cells.")
    counts = []
    with np.load(provenance["path"], allow_pickle=False) as archive:
        ids = archive["padded_source_id"]
        require(ids.shape == (PADDED, PADDED) and ids.dtype == np.uint8 and np.all(ids < 16), "Invalid padded source ownership.")
        expected_origins = np.array([[i % 4 * 1024, i // 4 * 1024] for i in range(16)], dtype=np.int32)
        require(np.array_equal(archive["padded_source_origins"], expected_origins), "Padded source origins differ from grid.")
        for index, source in enumerate(sources):
            row, col = divmod(index, 4)
            box = [origin[0] + col * 1024 - HALO, origin[1] + row * 1024 - HALO]
            box += [box[0] + 1254, box[1] + 1254]
            mask = archive[f"composite_source_{index:02d}_native_mask"] if source.get("kind") == "nativeComposite" else None
            raw, _ = repair.assembly_source(source, root_path.parent, box, index, f"{proof['tileId']}_s{row+1:02d}_{col+1:02d}", mask)
            ys, xs = np.nonzero(ids == index)
            require(xs.size > 0, "An archived padded cell contributes no pixels.")
            sx, sy = xs - col * 1024, ys - row * 1024
            require(sx.min() >= 0 and sy.min() >= 0 and sx.max() < 1254 and sy.max() < 1254, "Padded selection leaves its native footprint.")
            padded[ys, xs] = raw[sy, sx]
            counts.append({"sourceId": index, "pixelCount": int(xs.size)})
    expected_counts = {i["sourceId"]: i["pixelCount"] for i in root["paddedContributions"]}
    require(expected_counts == {i["sourceId"]: i["pixelCount"] for i in counts}, "Archived padded counts differ.")
    # Accepted repairs remain exact. Their unselected pixels never leak to halo.
    padded[HALO:HALO+CORE, HALO:HALO+CORE] = core
    info = {"tileId": proof["tileId"], "tileOrigin": origin,
            "image": repair.file_info(image_path), "record": repair.file_info(record_path),
            "rootAssembly": root_info, "rootPaddedProvenance": provenance,
            "coreValidation": proof, "paddedDimensions": [PADDED, PADDED],
            "globalPaddedBox": [origin[0]-HALO, origin[1]-HALO, origin[0]+CORE+HALO, origin[1]+CORE+HALO],
            "haloRule": "Original root assembly ownership outside current4096 core; exact verified final candidate inside core.",
            "originalPaddedCounts": counts}
    return padded, info


def join_pair(first, second, first_ids, second_ids, axis):
    """Combine same-coordinate strips; later source starts at the recorded path."""
    require(axis in (0, 1), "Axis must be0 or1.")
    if axis == 1:
        require(first.shape == second.shape == (PADDED, PADDED, 3), "Horizontal pair must contain padded tile squares.")
        delta = first[:, CORE:].astype(np.float64) - second[:, :OVERLAP].astype(np.float64)
        path, stats = assembly.minimum_path(np.mean(delta * delta, axis=2))
        pixels = np.empty((PADDED, PADDED_CLUSTER, 3), dtype=np.uint8)
        labels = np.full((PADDED, PADDED_CLUSTER), 255, dtype=np.uint8)
        pixels[:, :PADDED], labels[:, :PADDED] = first, first_ids
        for y, start in enumerate(path):
            pixels[y, CORE+start:] = second[y, start:]
            labels[y, CORE+start:] = second_ids[y, start:]
    else:
        require(first.shape == second.shape == (PADDED, PADDED_CLUSTER, 3), "Vertical pair must contain complete padded rows.")
        delta = first[CORE:].astype(np.float64) - second[:OVERLAP].astype(np.float64)
        path, stats = assembly.minimum_path(np.mean(delta * delta, axis=2).T)
        pixels = np.empty((PADDED_CLUSTER, PADDED_CLUSTER, 3), dtype=np.uint8)
        labels = np.full((PADDED_CLUSTER, PADDED_CLUSTER), 255, dtype=np.uint8)
        pixels[:PADDED], labels[:PADDED] = first, first_ids
        for x, start in enumerate(path):
            pixels[CORE+start:, x] = second[start:, x]
            labels[CORE+start:, x] = second_ids[start:, x]
    require(not np.any(labels == 255), "Join left an unassigned coordinate.")
    return pixels, labels, {"axis": axis, "overlapPath": path.tolist(), "statistics": stats}


def compose(arrays):
    rows, row_ids, joins = [], [], []
    for row in range(2):
        index = row * 2
        pixels, labels, join = join_pair(arrays[index], arrays[index+1],
            np.full((PADDED, PADDED), index, np.uint8),
            np.full((PADDED, PADDED), index+1, np.uint8), 1)
        join["tileRowIndex"] = row
        rows.append(pixels)
        row_ids.append(labels)
        joins.append(join)
    pixels, labels, join = join_pair(rows[0], rows[1], row_ids[0], row_ids[1], 0)
    joins.append(join)
    return pixels[HALO:HALO+CLUSTER, HALO:HALO+CLUSTER].copy(), labels[HALO:HALO+CLUSTER, HALO:HALO+CLUSTER].copy(), joins


def verify_pixels(pixels, labels, arrays):
    require(pixels.shape == (CLUSTER, CLUSTER, 3) and labels.shape == (CLUSTER, CLUSTER), "Invalid connected dimensions.")
    require(labels.dtype == np.uint8 and np.all(labels < 4), "Invalid connected source plane.")
    contributions = []
    for index, raw in enumerate(arrays):
        ys, xs = np.nonzero(labels == index)
        require(xs.size > 0, "A declared tile contributes no pixels.")
        row, col = divmod(index, 2)
        sy, sx = ys + HALO - row * CORE, xs + HALO - col * CORE
        require(sx.min() >= 0 and sy.min() >= 0 and sx.max() < PADDED and sy.max() < PADDED, "Connected selection is outside source coordinates.")
        require(np.array_equal(pixels[ys, xs], raw[sy, sx]), "Connected output contains changed or misregistered pixels.")
        contributions.append({"sourceId": index, "pixelCount": int(xs.size)})
    preserved = []
    for index, raw in enumerate(arrays):
        row, col = divmod(index, 2)
        x0, x1 = (HALO if col else 0), (CORE if col else CORE-HALO)
        y0, y1 = (HALO if row else 0), (CORE if row else CORE-HALO)
        result = pixels[row*CORE+y0:row*CORE+y1, col*CORE+x0:col*CORE+x1]
        source = raw[HALO+y0:HALO+y1, HALO+x0:HALO+x1]
        require(np.array_equal(result, source), "Pixels away from internal115px boundary changed.")
        preserved.append({"sourceId": index, "unchangedTileBox": [x0,y0,x1,y1], "verifiedPixels": (x1-x0)*(y1-y0)})
    return {"pixelCount": CLUSTER*CLUSTER, "contributions": contributions, "preservedCoreRegions": preserved,
            "allOutputPixelsExactlyMatchSameCoordinateVerifiedPaddedSource": True,
            "guidePixelsUsed": False, "unassignedPixels": 0}


def save_png(path, pixels):
    return assembly.save_image(path, Image.fromarray(pixels))


def projection_box(index):
    require(type(index) is int and 0 <= index < 4, "Projection sourceId must be an integer from0 through3.")
    row, col = divmod(index, 2)
    return [col*CORE, row*CORE, (col+1)*CORE, (row+1)*CORE]


def projection_labels(joins, index):
    """Replay the recorded boundary paths for just one 4096-square output."""
    require(isinstance(joins, list) and len(joins) == 3, "Three ordered connected joins are required.")
    paths = []
    for number, item in enumerate(joins):
        require(item.get("axis") == (1 if number < 2 else 0), "Connected join axis/order differs.")
        if number < 2:
            require(item.get("tileRowIndex") == number, "Connected row index differs.")
        values = item.get("overlapPath")
        length = PADDED if number < 2 else PADDED_CLUSTER
        require(isinstance(values, list) and len(values) == length and all(type(v) is int for v in values), "Invalid connected seam path length/type.")
        path = np.asarray(values, dtype=np.int32)
        require(bool(np.all((path >= 0) & (path < OVERLAP))) and bool(np.all(np.abs(np.diff(path)) <= 1)), "Connected seam path leaves its overlap or is discontinuous.")
        paths.append(path)
    x0, y0, _, _ = projection_box(index)
    xs = np.arange(x0+HALO, x0+HALO+CORE)
    ys = np.arange(y0+HALO, y0+HALO+CORE)
    selected_row = ys[:, None] >= (CORE + paths[2][xs])[None, :]
    labels = np.empty((CORE, CORE), dtype=np.uint8)
    for row in range(2):
        local_y = ys - row*CORE
        rows_in_source = (local_y >= 0) & (local_y < PADDED)
        # Rows beyond this source's footprint are never selected; clip only
        # the temporary lookup, and independently reject an invalid selection.
        chosen = selected_row == row
        require(not bool(np.any(chosen[~rows_in_source])), "Join path selects a row outside its padded source.")
        starts = CORE + paths[row][np.clip(local_y, 0, PADDED-1)]
        selected_col = xs[None, :] >= starts[:, None]
        labels[chosen] = (row*2 + selected_col)[chosen]
    return labels


def verify_projection_pixels(pixels, labels, arrays, index):
    """Check every projected pixel against its globally aligned padded source."""
    require(pixels.shape == (CORE, CORE, 3) and pixels.dtype == np.uint8, "Invalid projected tile pixels.")
    require(labels.shape == (CORE, CORE) and labels.dtype == np.uint8 and bool(np.all(labels < 4)), "Invalid projected ownership plane.")
    require(len(arrays) == 4, "Four padded sources required.")
    x0, y0, _, _ = projection_box(index)
    contributions = []
    for source_id, raw in enumerate(arrays):
        require(raw.shape == (PADDED, PADDED, 3) and raw.dtype == np.uint8, "Invalid reconstructed padded source.")
        ys, xs = np.nonzero(labels == source_id)
        if xs.size == 0:
            continue
        row, col = divmod(source_id, 2)
        sx, sy = xs+x0+HALO-col*CORE, ys+y0+HALO-row*CORE
        require(sx.min() >= 0 and sy.min() >= 0 and sx.max() < PADDED and sy.max() < PADDED, "Projection selects a source outside its native footprint.")
        require(np.array_equal(pixels[ys, xs], raw[sy, sx]), "Projected tile differs from its same-coordinate native source.")
        contributions.append({"sourceId": source_id, "pixelCount": int(xs.size)})
    row, col = divmod(index, 2)
    bx0, bx1 = (HALO if col else 0), (CORE if col else CORE-HALO)
    by0, by1 = (HALO if row else 0), (CORE if row else CORE-HALO)
    require(np.array_equal(pixels[by0:by1, bx0:bx1], arrays[index][HALO+by0:HALO+by1, HALO+bx0:HALO+bx1]), "Projection changed pixels outside its internal boundary band.")
    require(sum(c["pixelCount"] for c in contributions) == CORE*CORE, "Projection coverage is incomplete.")
    return {"verifiedPixelCount": CORE*CORE, "contributions": contributions,
            "preservedTileBox": [bx0, by0, bx1, by1],
            "allPixelsExactlyMatchSameCoordinateVerifiedSource": True}


def validate_projection(pixels, record, record_path, seen):
    """Revalidate the projection through every input core, halo, and raw leaf.

    The cluster record deliberately does not hash these child records: each
    child pins the already-written cluster, so the evidence graph is acyclic.
    """
    require(record.get("operation") == PROJECTION_OPERATION and record.get("schemaVersion") == 1 and record.get("isAiGeneration") is False, "Unsupported connected projection record.")
    for key in ("registration", "resizing", "feathering", "colorCorrection", "pixelSynthesis"):
        require(record.get("method", {}).get(key) is False, f"Projection must forbid {key}.")
    cluster_info = pinned(record.get("cluster"), record_path.parent, "projection cluster")
    cluster_path = Path(cluster_info["path"])
    require(cluster_path.is_relative_to(ZONE), "Connected cluster provenance must remain in this zone.")
    require(cluster_path not in seen and len(seen) < 32, "Cyclic or excessive connected provenance chain.")
    next_seen = set(seen) | {cluster_path}
    cluster = repair.read_json(cluster_path)
    require(cluster.get("schemaVersion") == 1 and cluster.get("operation") == OPERATION and cluster.get("isAiGeneration") is False, "Unsupported connected cluster operation.")
    require(cluster.get("clusterDimensions") == [CLUSTER, CLUSTER], "Connected cluster dimensions differ.")
    for key in ("registration", "resizingFinalArt", "feathering", "colorCorrection", "pixelSynthesis"):
        require(cluster.get("method", {}).get(key) is False, f"Connected cluster must forbid {key}.")
    manifest_info = pinned(cluster.get("manifest"), cluster_path.parent, "connected manifest")
    manifest = repair.read_json(Path(manifest_info["path"]))
    require(manifest == cluster.get("manifestSnapshot") and manifest.get("schemaVersion") == 1, "Connected manifest snapshot differs.")
    matrix = manifest.get("tileMatrix")
    require(isinstance(matrix, list) and len(matrix) == 2 and all(isinstance(row, list) and len(row) == 2 for row in matrix), "Connected manifest needs an explicit2x2 matrix.")
    sources, outputs = cluster.get("sources"), cluster.get("outputs")
    require(isinstance(sources, list) and len(sources) == 4 and isinstance(outputs, list) and len(outputs) == 4, "Connected cluster must declare four sources and outputs.")
    index = record.get("sourceId")
    box = projection_box(index)
    require(record.get("clusterCropBox") == box and outputs[index].get("clusterCropBox") == box, "Projection crop differs from the exact4K grid.")
    origin = repair.tile_origin(sources[0].get("tileId"))
    require(cluster.get("clusterOrigin") == origin, "Connected cluster origin differs.")
    arrays, verified_sources = [], []
    for number, source in enumerate(sources):
        expected_origin = [origin[0]+number%2*CORE, origin[1]+number//2*CORE]
        require(source.get("sourceId") == number and source.get("tileOrigin") == expected_origin and repair.tile_origin(source.get("tileId")) == expected_origin, "Connected source identity or order differs.")
        entry = matrix[number//2][number%2]
        source_image = pinned(source.get("image"), cluster_path.parent, "connected source image")
        source_record = pinned(source.get("record"), cluster_path.parent, "connected source record")
        require(pinned(entry.get("image"), Path(manifest_info["path"]).parent, "manifest image") == source_image and pinned(entry.get("record"), Path(manifest_info["path"]).parent, "manifest record") == source_record, "Connected source differs from pinned manifest.")
        raw, verified = reconstruct_padded(Path(source_image["path"]), Path(source_record["path"]), next_seen)
        require(verified["tileId"] == source["tileId"] and verified["tileOrigin"] == expected_origin, "Verified source coordinates differ from cluster.")
        for key in ("rootAssembly", "rootPaddedProvenance"):
            require(pinned(source.get(key), cluster_path.parent, f"connected {key}") == verified[key], "Connected root provenance differs.")
        require(source.get("originalPaddedCounts") == verified["originalPaddedCounts"], "Connected halo ownership counts differ.")
        arrays.append(raw)
        verified_sources.append(verified)
    own_source = verified_sources[index]
    require(record.get("tileId") == outputs[index].get("tileId") == own_source["tileId"] and record.get("tileOrigin") == own_source["tileOrigin"], "Projection changed tile identity.")
    require(pinned(record.get("output"), record_path.parent, "projected output") == pinned(outputs[index].get("output"), cluster_path.parent, "cluster output"), "Projection output differs from cluster output.")
    for key in ("image", "record"):
        require(pinned(record.get("base", {}).get(key), record_path.parent, f"projection predecessor {key}") == own_source[key], "Projection predecessor is not its own input tile.")
    plane_info = pinned(cluster.get("sourceIndexPlane"), cluster_path.parent, "connected source plane")
    with np.load(plane_info["path"], allow_pickle=False) as archive:
        labels = archive["source_tile_id"]
        require(labels.shape == (CLUSTER, CLUSTER) and labels.dtype == np.uint8 and bool(np.all(labels < 4)), "Invalid connected ownership archive.")
        x0,y0,x1,y1 = box
        selected_labels = labels[y0:y1,x0:x1].copy()
    del labels
    require(np.array_equal(selected_labels, projection_labels(cluster.get("joins"), index)), "Projected ownership differs from recorded connected seam paths.")
    verification = verify_projection_pixels(pixels, selected_labels, arrays, index)
    require(record.get("coverageAssertions", {}).get("fullNativeCoverage") is True, "Projection does not affirm full native coverage.")
    roots, references = {}, {}
    for source in verified_sources:
        proof = source["coreValidation"]
        for root in proof.get("rootAssemblies", [{"assembly": proof["rootAssembly"], "originalRawSourceCount": proof["originalRawSourceCount"]}]):
            roots[root["assembly"]["sha256"]] = root
        for ref in proof.get("repairReferenceAvailability", []):
            references[json.dumps(ref, sort_keys=True)] = ref
    reference_values = list(references.values())
    own_proof = own_source["coreValidation"]
    return {**own_proof, "fullNativeCoverage": True, "verifiedPixelCount": CORE*CORE,
            "originalRawSourceCount": sum(root["originalRawSourceCount"] for root in roots.values()),
            "rootAssemblies": list(roots.values()),
            "connectedProjection": {"record": repair.file_info(record_path), "cluster": cluster_info,
                                    "sourceId": index, "sourceIndexPlane": plane_info, "verification": verification,
                                    "sourceImagesAndRecords": [{"image": s["image"], "record": s["record"],
                                                                "priorRepairCount": s["coreValidation"]["priorRepairCount"]} for s in verified_sources]},
            "repairReferenceAvailability": reference_values,
            "fullRepairReferenceAvailability": all(item["fullReferenceAvailability"] for item in reference_values)}


def make_projection_record(cluster_info, source, output, index):
    return {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
            "operation": PROJECTION_OPERATION, "isAiGeneration": False,
            "status": "candidate_pending_shared_boundary_visual_review",
            "tool": repair.file_info(Path(__file__).resolve()), "cluster": cluster_info,
            "sourceId": index, "tileId": source["tileId"], "tileOrigin": source["tileOrigin"],
            "base": {"image": source["image"], "record": source["record"]},
            "clusterCropBox": projection_box(index),
            "output": {**output, "dimensions": [CORE, CORE]},
            "method": {"registration": False, "resizing": False, "feathering": False,
                       "colorCorrection": False, "pixelSynthesis": False,
                       "coordinateRule": "Exact4096 projection; ownership and global source coordinates replay from pinned connected cluster."},
            "coverageAssertions": {"fullNativeCoverage": True, "tilePixelCount": CORE*CORE,
                                   "guidePixelsUsedAsFinalArt": False, "unassignedPixels": 0},
            "formalAcceptedCount": 0,
            "limits": ["Native provenance is revalidated from cluster input cores and root halos on each use.",
                       "This record permits subsequent explicit native repairs but grants no visual acceptance."]}


def build(manifest_path, output_dir):
    manifest = repair.read_json(manifest_path)
    require(manifest.get("schemaVersion") == 1, "Manifest schemaVersion must equal1.")
    matrix = manifest.get("tileMatrix")
    require(isinstance(matrix, list) and len(matrix) == 2 and all(isinstance(r, list) and len(r) == 2 for r in matrix), "Explicit2x2 tileMatrix required.")
    require(not output_dir.exists(), "Output directory exists; choose a fresh version.")
    assembly.writable(output_dir)
    arrays, sources = [], []
    for row in matrix:
        for item in row:
            image_info = pinned(item.get("image"), manifest_path.parent, "manifest tile image")
            record_info = pinned(item.get("record"), manifest_path.parent, "manifest tile record")
            pixels, source = reconstruct_padded(Path(image_info["path"]), Path(record_info["path"]))
            source["sourceId"] = len(sources)
            arrays.append(pixels)
            sources.append(source)
    origin = sources[0]["tileOrigin"]
    for index, source in enumerate(sources):
        require(source["tileOrigin"] == [origin[0]+index%2*CORE, origin[1]+index//2*CORE], "Input tiles are not ordered adjacent2x2 coordinates.")
    pixels, labels, joins = compose(arrays)
    proof = verify_pixels(pixels, labels, arrays)
    output_dir.mkdir(parents=True)
    archive_path = output_dir / "padded_source_tile_id.npz"
    with archive_path.open("xb") as handle:
        np.savez_compressed(handle, source_tile_id=labels)
    outputs = []
    for index, source in enumerate(sources):
        row, col = divmod(index,2)
        tile = pixels[row*CORE:(row+1)*CORE, col*CORE:(col+1)*CORE]
        outputs.append({"tileId": source["tileId"], "clusterCropBox": [col*CORE,row*CORE,(col+1)*CORE,(row+1)*CORE],
                        "projectionRecordPath": str(output_dir / f"{source['tileId']}_connected_4096.connected-projection.json"),
                        "output": save_png(output_dir / f"{source['tileId']}_connected_4096.png", tile)})
    qa = []
    for i in range(8):
        a,b=i*1024,(i+1)*1024
        qa.append({"axis": "left-right", "box": [CORE-240,a,CORE+240,b], "output": save_png(output_dir/f"shared_vertical_y{a:04d}-{b:04d}_100pct.png", pixels[a:b,CORE-240:CORE+240])})
        qa.append({"axis": "top-bottom", "box": [a,CORE-240,b,CORE+240], "output": save_png(output_dir/f"shared_horizontal_x{a:04d}-{b:04d}_100pct.png", pixels[CORE-240:CORE+240,a:b])})
    qa.append({"axis": "four-tile-junction", "box": [CORE-480,CORE-480,CORE+480,CORE+480], "output": save_png(output_dir/"four_tile_junction_100pct.png",pixels[CORE-480:CORE+480,CORE-480:CORE+480])})
    preview = assembly.save_image(output_dir/"PREVIEW_NOT_FOR_GAME_1536.png", Image.fromarray(pixels).resize((1536,1536), Image.Resampling.LANCZOS))
    record = {"schemaVersion":1, "createdAtUtc": datetime.now(timezone.utc).isoformat(), "operation": OPERATION, "isAiGeneration":False,
              "tool": repair.file_info(Path(__file__).resolve()), "manifest": repair.file_info(manifest_path), "manifestSnapshot":manifest,
              "status":"candidate_pending_full_shared_boundary_and_junction_visual_review", "clusterOrigin":origin,
              "clusterDimensions":[CLUSTER,CLUSTER], "sources":sources, "outputs":outputs,
              "sourceIndexPlane": repair.file_info(archive_path), "sourceIndexRule":"source padded x=cluster x+115-(sourceId%2)*4096; y=cluster y+115-(sourceId//2)*4096",
              "joins":joins, "verification":proof,
              "method":{"registration":False,"resizingFinalArt":False,"feathering":False,"colorCorrection":False,"pixelSynthesis":False,
                        "order":"join two padded tile rows left-to-right, then top-to-bottom, crop115perimeter, split into four4096 squares",
                        "boundaryWidthPerTile":115,"outsideInternalBoundaryPixelsPreserved":True},
              "qa":{"nativeScaleCrops":qa,"previewOnlyDownsampled":preview,"visualReviewPassed":False},
              "formalAcceptedCount":0,
              "limits":["Source selection does not prove visually continuous material, geometry, or navigation.","External perimeter of this neighborhood requires adjacent tile/zone review.","Historical reference availability is disclosed in source validation; pixels are never recreated to replace missing references."]}
    record_info = assembly.save_json(output_dir/"connected-cluster.json",record)
    projections = []
    for index, (source, output) in enumerate(zip(sources, outputs)):
        projection = make_projection_record(record_info, source, output["output"], index)
        projection_path = output_dir / f"{source['tileId']}_connected_4096.connected-projection.json"
        projections.append({"tileId": source["tileId"], "output": projection["output"],
                            "record": assembly.save_json(projection_path, projection)})
    print(json.dumps({"status":record["status"],"record":record_info,"outputs":outputs,
                      "repairableProjections":projections,"formalAcceptedCount":0},ensure_ascii=False,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir",required=True)
    args=parser.parse_args()
    build(Path(args.manifest).resolve(),Path(args.output_dir).resolve())


if __name__=="__main__":
    try:
        main()
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as error:
        print(json.dumps({"status":"failed","error":str(error),"candidateAccepted":False},ensure_ascii=False),file=sys.stderr)
        sys.exit(1)
