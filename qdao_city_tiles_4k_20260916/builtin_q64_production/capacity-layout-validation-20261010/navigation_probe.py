"""Conservative point-connectivity probe on manually annotated visible ground.

Uses only NumPy/Pillow and the unchanged analyze.raster/components helpers.
No artwork, annotation, client asset or hidden doorway is changed. This is not
Unity navigation, an actor simulation, circulation validation or a load test.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import json
import math
import hashlib
import sys
import numpy as np
from analyze import raster, components

ROOT = Path(__file__).resolve().parent
MAIN_SIDES = (300, 400, 500, 600, 700, 1000)
RADII = (("collision_reference", 0.38), ("shadow_reference", 1.45))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disk_offsets(radius):
    """All integer lattice offsets in a closed Euclidean disk, not samples."""
    radius = int(radius)
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    return [(dx, dy) for dy in range(-radius, radius + 1)
            for dx in range(-radius, radius + 1)
            if dx * dx + dy * dy <= radius * radius]


def erode_disk(mask, radius):
    """Exact discrete-disk erosion; outside the image is always blocked."""
    mask = np.asarray(mask, dtype=bool)
    h, w = mask.shape
    radius = int(radius)
    padded = np.pad(mask, radius, constant_values=False)
    result = mask.copy()
    for dx, dy in disk_offsets(radius):
        result &= padded[radius + dy:radius + dy + h,
                         radius + dx:radius + dx + w]
    return result


def brute_erosion(mask, radius):
    h, w = mask.shape
    out = np.zeros_like(mask, dtype=bool)
    for y in range(h):
        for x in range(w):
            out[y, x] = all(0 <= x + dx < w and 0 <= y + dy < h
                            and mask[y + dy, x + dx]
                            for dx, dy in disk_offsets(radius))
    return out


def self_tests():
    checks = []
    assert len(disk_offsets(2)) == 13 and len(disk_offsets(3)) == 29
    checks.append("closed integer disks contain all 13/29 offsets at radii 2/3")
    mask = np.ones((25, 25), dtype=bool)
    mask[12, 12] = False
    eroded = erode_disk(mask, 2)
    assert not eroded[13, 13] and not eroded[12, 14]
    assert eroded[13, 14]  # sqrt(5) lies outside disk radius 2, inside square 2.
    assert not eroded[1, 10] and eroded[2, 10]
    checks.append("round-corner clearance differs from square erosion; exterior blocked")
    corridor = np.zeros((31, 65), dtype=bool)
    corridor[5:26, 2:23] = True
    corridor[5:26, 42:63] = True
    corridor[14:17, 22:43] = True
    labels1, _ = components(erode_disk(corridor, 1))
    labels2, _ = components(erode_disk(corridor, 2))
    assert labels1[15, 12] == labels1[15, 52] != 0
    assert labels2[15, 12] != labels2[15, 52]
    assert labels2[15, 12] != 0 and labels2[15, 52] != 0
    checks.append("three-pixel corridor passes radius 1 and disconnects radius 2")
    labels, sizes = components(np.eye(2, dtype=bool))
    assert len(sizes) == 2 and labels[0, 0] != labels[1, 1]
    checks.append("diagonal contact does not create a four-neighbour path")
    rng = np.random.default_rng(20261010)
    for probability in (0.25, 0.75, 1.0):
        mask = rng.random((13, 17)) < probability
        for radius in range(4):
            assert np.array_equal(erode_disk(mask, radius), brute_erosion(mask, radius))
    checks.append("vectorised erosion equals exhaustive reference on 12 small masks/radii")
    assert math.ceil(0.38 * 1254 / 1000) == 1
    checks.append("positive subpixel collision radius is conservatively rounded up, never zero")
    return {"passed": True, "checks": checks}


def component_geometry(labels, sizes):
    n = len(sizes)
    if n == 0:
        return []
    h, w = labels.shape
    ys, xs = np.nonzero(labels)
    ids = labels[ys, xs]
    minx = np.full(n + 1, w, dtype=np.int32)
    miny = np.full(n + 1, h, dtype=np.int32)
    maxx = np.full(n + 1, -1, dtype=np.int32)
    maxy = np.full(n + 1, -1, dtype=np.int32)
    np.minimum.at(minx, ids, xs)
    np.minimum.at(miny, ids, ys)
    np.maximum.at(maxx, ids, xs)
    np.maximum.at(maxy, ids, ys)
    return [{"id": i, "pixels": int(size),
             "box": [int(minx[i]), int(miny[i]), int(maxx[i]), int(maxy[i])]}
            for i, size in enumerate(sizes, 1)]


def nearest_point(coords, x, y):
    if not len(coords):
        return None
    distance2 = (coords[:, 0] - x) ** 2 + (coords[:, 1] - y) ** 2
    index = int(np.argmin(distance2))
    return {"point": coords[index].astype(int).tolist(),
            "distancePixels": math.sqrt(float(distance2[index]))}


def block_samples(mask, point, radius):
    x, y = point
    h, w = mask.shape
    blocked = []
    for dx, dy in disk_offsets(radius):
        xx, yy = x + dx, y + dy
        if not (0 <= xx < w and 0 <= yy < h) or not mask[yy, xx]:
            blocked.append([xx, yy])
    if len(blocked) > 12:
        indices = np.linspace(0, len(blocked) - 1, 12).astype(int)
        samples = [blocked[i] for i in indices]
    else:
        samples = blocked
    return {"blockedFootprintPixelCount": len(blocked),
            "sampleBlockedPoints": samples,
            "box": [x - radius, y - radius, x + radius, y + radius]}


def uncertainty_regions(annotation):
    regions = []
    for area in annotation.get("uncertainAreas", []):
        regions.append({"id": area["id"],
                        "box": area.get("box", area.get("approxBox")),
                        "candidatePortalEndpoints": area.get("candidatePortalEndpoints", []),
                        "reason": area.get("issue", area.get("description", "")),
                        "status": "unknown_not_filled"})
    return regions


def run_map(path):
    source_bytes = path.read_bytes()
    annotation = json.loads(source_bytes.decode("utf-8-sig"))
    assert digest(Path(annotation["imagePath"])) == annotation["imageSha256"]
    mask = raster(annotation)
    h, w = mask.shape
    assert (h, w) == (1254, 1254), "Probe expects the current 1254 square annotations"
    base_labels, base_sizes = components(mask)
    base_largest = int(np.argmax(base_sizes)) + 1 if base_sizes else 0
    cache = {}
    scenarios = []
    for main_side in MAIN_SIDES:
        side = main_side * (1 if annotation["map"] == "main" else math.sqrt(0.75))
        world_per_pixel = side / w
        for name, radius_world in RADII:
            requested_radius = radius_world / world_per_pixel
            effective_radius = math.ceil(requested_radius)
            if effective_radius not in cache:
                eroded = erode_disk(mask, effective_radius)
                labels, sizes = components(eroded)
                largest_id = int(np.argmax(sizes)) + 1 if sizes else 0
                yy, xx = np.where(labels == largest_id) if largest_id else ([], [])
                largest_coords = np.column_stack((xx, yy)).astype(np.int32)
                cache[effective_radius] = (eroded, labels, sizes, largest_id,
                                           largest_coords, component_geometry(labels, sizes))
            eroded, labels, sizes, largest_id, coords, geometry = cache[effective_radius]
            anchors = []
            for anchor in annotation["anchors"]:
                x, y = map(int, anchor["point"])
                in_bounds = 0 <= x < w and 0 <= y < h
                original_id = int(base_labels[y, x]) if in_bounds else 0
                current_id = int(labels[y, x]) if in_bounds else 0
                if not in_bounds or original_id == 0:
                    status = "anchor_outside_visible_ground"
                elif current_id == 0:
                    status = "anchor_blocked_after_clearance"
                elif current_id == largest_id:
                    status = "reachable_in_largest_visible_component"
                else:
                    status = "disconnected_visible_component"
                nearest = nearest_point(coords, x, y) if current_id != largest_id else None
                if nearest:
                    nearest["distanceWorld"] = nearest["distancePixels"] * world_per_pixel
                    nearest["meaning"] = "nearest raster point only; not a traversable straight-line path"
                anchors.append({**anchor, "status": status,
                    "originalComponent": original_id,
                    "originallyInLargestVisibleComponent": original_id == base_largest,
                    "componentAfterClearance": current_id,
                    "lostLargestConnectivityAfterClearance": original_id == base_largest and current_id != largest_id,
                    "clearanceBlockage": block_samples(mask, (x, y), effective_radius) if current_id == 0 else None,
                    "nearestLargestPoint": nearest,
                    "physicalDoorOrPortalVerified": False})
            status_counts = dict(Counter(a["status"] for a in anchors))
            largest_size = sizes[largest_id - 1] if largest_id else 0
            scenarios.append({
                "mainWorldSide": main_side, "mapWorldSide": side,
                "radiusKind": name, "requestedRadiusWorld": radius_world,
                "requestedRadiusPixels": requested_radius,
                "effectiveRadiusPixels": effective_radius,
                "effectiveRadiusWorld": effective_radius * world_per_pixel,
                "extraConservativeRadiusWorld": effective_radius * world_per_pixel - radius_world,
                "diskOffsetCount": len(disk_offsets(effective_radius)),
                "availableCenterPixels": int(eroded.sum()),
                "availableCenterAreaWorld": int(eroded.sum()) * world_per_pixel ** 2,
                "componentCount": len(sizes), "largestComponentId": largest_id,
                "largestComponentPixels": int(largest_size),
                "largestComponentAreaWorld": int(largest_size) * world_per_pixel ** 2,
                "components": [{**g, "areaWorld": g["pixels"] * world_per_pixel ** 2}
                               for g in sorted(geometry, key=lambda g: g["pixels"], reverse=True)],
                "anchorStatusCounts": status_counts,
                "allAnchorsReachableInLargestVisibleComponent": all(a["status"] == "reachable_in_largest_visible_component" for a in anchors),
                "anchors": anchors,
                "unknownDoorwaysFilled": False,
                "runtimeNavigationValidated": False,
                "capacity5000Validated": False,
            })
    assert source_bytes == path.read_bytes(), "Annotation changed during this map probe"
    return {"map": annotation["map"], "annotationPath": str(path),
            "annotationSha256": hashlib.sha256(source_bytes).hexdigest(),
            "imagePath": annotation["imagePath"], "imageSha256": annotation["imageSha256"],
            "baseWalkablePixels": int(mask.sum()), "baseComponentCount": len(base_sizes),
            "uncertainRegions": uncertainty_regions(annotation), "scenarios": scenarios}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": "Exact integer-disk erosion of conservative manually annotated visible-ground raster, then four-neighbour anchor component membership.",
        "methodChinese": "人工可见地面掩码按完整离散圆盘保守腐蚀，再检查锚点的四邻域连通；仅作图像布局预检。",
        "radiusQuantization": "ceil(worldRadius * annotationWidth / mapWorldSide); all integer offsets dx^2+dy^2 <= ceilRadius^2 are checked; outside image blocked",
        "projectionLimitation": "uniform image-plane-to-world scaling is a scenario assumption, not a calibrated isometric ground-plane transform",
        "mainWorldSides": list(MAIN_SIDES), "villageIslandAreaRatioToMain": 0.75,
        "collisionReferenceRadiusWorld": 0.38, "shadowReferenceRadiusWorld": 1.45,
        "shadowRadiusIsActualCollision": False,
        "unknownDoorwaysFilled": False,
        "worldSizeApproved": False, "capacity5000Validated": False,
        "runtimeNavigationValidated": False, "runtimePerformanceValidated": False,
        "selfTests": self_tests(), "maps": [],
    }
    for mid in ("main", "village", "island"):
        print("probing " + mid, flush=True)
        result["maps"].append(run_map(ROOT / "maps" / (mid + ".json")))
    output = ROOT / "navigation-probe.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    compact = [{"map": m["map"], "scenarios": [{
        "mainSide": s["mainWorldSide"], "radius": s["radiusKind"],
        "effectiveRadiusPixels": s["effectiveRadiusPixels"],
        "largestAreaWorld": round(s["largestComponentAreaWorld"], 2),
        "anchorStatusCounts": s["anchorStatusCounts"]}
        for s in m["scenarios"]]} for m in result["maps"]]
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
