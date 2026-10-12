"""Static foot-point capacity with an explicitly reserved connected path skeleton.

No source artwork, annotation, client or game configuration is changed. Grid
spacings and a three-world-unit corridor are experiment choices, not standards.
This script does not simulate moving players, render overlap, or MMO performance.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import deque
import hashlib
import json
import math
import sys
import numpy as np
from analyze import raster, components
from navigation_probe import erode_disk, disk_offsets

ROOT = Path(__file__).resolve().parent
MAIN_SIDES = (300, 400, 500, 600)
SPACINGS = (1.0, 1.5, 2.0, 2.5, 3.0)
COLLISION_RADIUS = 0.38
CORRIDOR_WIDTH = 3.0
MAX_PEOPLE = 5000
POSITION_SAMPLE_LIMIT = 500
CENTRAL_ANCHORS = {"main": "central_plaza", "village": "double_fish_plaza", "island": "central_plaza"}


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def dilate_disk(mask, radius):
    h, w = mask.shape
    radius = int(radius)
    padded = np.pad(mask, radius, constant_values=False)
    out = np.zeros_like(mask, dtype=bool)
    for dx, dy in disk_offsets(radius):
        out |= padded[radius + dy:radius + dy + h,
                      radius + dx:radius + dx + w]
    return out


def shortest_path_tree(mask, target):
    """Breadth-first tree over four-neighbour pixel centres; equal edge costs."""
    h, w = mask.shape
    x, y = map(int, target)
    if not (0 <= x < w and 0 <= y < h and mask[y, x]):
        raise ValueError("target is not in the chosen component")
    padded = np.pad(mask, 1).ravel()
    stride = w + 2
    seed = (y + 1) * stride + x + 1
    parents = np.full(padded.size, -1, dtype=np.int32)
    parents[seed] = seed
    queue = deque([seed])
    while queue:
        cur = queue.popleft()
        for nxt in (cur - 1, cur + 1, cur - stride, cur + stride):
            if padded[nxt] and parents[nxt] == -1:
                parents[nxt] = cur
                queue.append(nxt)
    return parents, seed, stride


def extract_path(parents, seed, stride, point):
    x, y = map(int, point)
    idx = (y + 1) * stride + x + 1
    if parents[idx] == -1:
        return []
    result = []
    while True:
        result.append([int(idx % stride - 1), int(idx // stride - 1)])
        if idx == seed:
            return result
        idx = int(parents[idx])


def compress_polyline(points):
    """Remove collinear interior vertices without changing the path geometry."""
    if len(points) < 3:
        return points
    result = [points[0]]
    previous = (points[1][0] - points[0][0], points[1][1] - points[0][1])
    for index in range(1, len(points) - 1):
        nxt = (points[index + 1][0] - points[index][0], points[index + 1][1] - points[index][1])
        if nxt != previous:
            result.append(points[index])
        previous = nxt
    result.append(points[-1])
    return result


def deficient_runs(path, width_clear):
    runs = []
    start = None
    for index in range(len(path) + 1):
        bad = index < len(path) and not width_clear[path[index][1], path[index][0]]
        if bad and start is None:
            start = index
        elif not bad and start is not None:
            section = path[start:index]
            runs.append({"fromPathIndex": start, "toPathIndex": index - 1,
                         "pointCount": len(section), "polyline": compress_polyline(section)})
            start = None
    return runs


def four_corner_membership(mask, points, require_all):
    """Conservative float-point sampling; points stay at exact world grid spacing.

    A retained point needs all four enclosing integer centres inside clearance.
    It is rejected if any corner touches the corridor exclusion envelope.
    """
    if not len(points):
        return np.empty(0, dtype=bool)
    h, w = mask.shape
    x0 = np.floor(points[:, 0]).astype(int)
    y0 = np.floor(points[:, 1]).astype(int)
    x1 = np.ceil(points[:, 0]).astype(int)
    y1 = np.ceil(points[:, 1]).astype(int)
    valid = (x0 >= 0) & (y0 >= 0) & (x1 < w) & (y1 < h)
    result = np.ones(len(points), dtype=bool) if require_all else np.zeros(len(points), dtype=bool)
    for xs, ys in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        values = np.zeros(len(points), dtype=bool)
        values[valid] = mask[ys[valid], xs[valid]]
        if require_all:
            result &= values
        else:
            result |= values
    if not require_all:
        result |= ~valid
    return result


def grid_experiment(allowed, corridor_exclusion, side, spacing):
    h, w = allowed.shape
    step = spacing * w / side
    phases = ((0.5, 0.5), (0.25, 0.25), (0.25, 0.75), (0.75, 0.25))
    trials = []
    winner = None
    for phase in phases:
        xs = np.arange(step * phase[0], w - 1, step)
        ys = np.arange(step * phase[1], h - 1, step)
        xx, yy = np.meshgrid(xs, ys)
        points = np.column_stack((xx.ravel(), yy.ravel()))
        raw_keep = four_corner_membership(allowed, points, True)
        raw = points[raw_keep]
        post = raw[~four_corner_membership(corridor_exclusion, raw, False)]
        trial = {"phase": list(phase), "rawCount": len(raw), "afterCorridorCount": len(post)}
        trials.append(trial)
        if winner is None or len(post) > len(winner[1]):
            winner = (trial, post)
    chosen, candidates = winner
    count = min(MAX_PEOPLE, len(candidates))
    rng = np.random.default_rng(5000)
    selected = candidates[rng.permutation(len(candidates))[:count]]
    if len(selected):
        selected = selected[np.argsort(selected[:, 1], kind="stable")]
    assert len(set(map(tuple, selected))) == len(selected)
    assert np.all(four_corner_membership(allowed, selected, True))
    assert not np.any(four_corner_membership(corridor_exclusion, selected, False))
    assert spacing >= 2 * COLLISION_RADIUS
    sample_indices = np.linspace(0, count - 1, min(POSITION_SAMPLE_LIMIT, count)).astype(int) if count else []
    sample = selected[sample_indices] if count else np.empty((0, 2))
    return {
        "requestedSpacingWorld": spacing, "actualGridSpacingWorld": spacing,
        "spacingIsExperimentNotStandard": True, "gridStepPixels": step,
        "chosenPhase": chosen["phase"], "phaseTrials": trials,
        "rawCount": chosen["rawCount"], "afterCorridorCount": len(candidates),
        "removedByCorridorCount": chosen["rawCount"] - len(candidates),
        "placedCount": count, "all5000FootPointsFit": count == 5000,
        "circleDiameterWorld": 2 * COLLISION_RADIUS,
        "gridCirclesGeometricallyNonoverlapping": True,
        "visualSpritesOrNamesNonoverlappingValidated": False,
        "placedPositionsSample": np.round(sample, 4).tolist(),
        "sampleCount": len(sample), "sampleRepresentsTotalPlaced": count,
        "sampling": "up to 500 evenly indexed points from deterministic random subset sorted by y; counts use all candidates",
        "coordinateSystem": "1254 image-plane x/y, origin upper left; samples rounded only for display",
        "selectionSeed": 5000,
        "_fullPositionsForBrowser": np.round(selected, 4).tolist(),
    }


def self_tests():
    checks = []
    single = np.zeros((11, 11), dtype=bool)
    single[5, 5] = True
    dilated = dilate_disk(single, 2)
    assert dilated.sum() == 13 and not dilated[0, 0]
    assert dilated[6, 6] and not dilated[6, 7]
    checks.append("disk dilation covers exactly 13 radius-2 offsets and does not invent exterior strips")
    mask = np.zeros((13, 21), dtype=bool)
    mask[2:11, 2:19] = True
    mask[2:9, 10] = False
    parents, seed, stride = shortest_path_tree(mask, [4, 4])
    path = extract_path(parents, seed, stride, [16, 4])
    assert path[0] == [16, 4] and path[-1] == [4, 4]
    assert len(path) - 1 == 22
    assert all(mask[y, x] for x, y in path)
    assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(path, path[1:]))
    checks.append("four-neighbour shortest path detours around wall without cutting corners")
    narrow = np.zeros((15, 21), dtype=bool)
    narrow[6:9, 2:19] = True
    skeleton = np.zeros_like(narrow)
    skeleton[7, 3:18] = True
    reserve = dilate_disk(skeleton, 2) & narrow
    assert not np.any(reserve & ~narrow)
    assert np.any(skeleton & ~erode_disk(narrow, 2))
    checks.append("narrow corridor remains clipped to ground and is flagged deficient, never declared full width")
    sample_mask = np.ones((5, 5), dtype=bool)
    sample_mask[2, 2] = False
    assert not four_corner_membership(sample_mask, np.array([[1.5, 1.5]]), True)[0]
    checks.append("float foot point next to excluded corner is conservatively rejected")
    return {"passed": True, "checks": checks}


def run_map(path):
    input_bytes = path.read_bytes()
    annotation = json.loads(input_bytes.decode("utf-8-sig"))
    assert digest_bytes(Path(annotation["imagePath"]).read_bytes()) == annotation["imageSha256"]
    mask = raster(annotation)
    h, w = mask.shape
    assert h == w == 1254
    preferred = next(a for a in annotation["anchors"] if a["id"] == CENTRAL_ANCHORS[annotation["map"]])
    caches = {}
    scenarios = []
    for main_side in MAIN_SIDES:
        side = main_side * (1 if annotation["map"] == "main" else math.sqrt(0.75))
        world_per_pixel = side / w
        radius_px = math.ceil(COLLISION_RADIUS / world_per_pixel)
        corridor_radius_px = math.ceil((CORRIDOR_WIDTH / 2) / world_per_pixel)
        if radius_px not in caches:
            cleared = erode_disk(mask, radius_px)
            labels, sizes = components(cleared)
            largest_id = int(np.argmax(sizes)) + 1
            largest = labels == largest_id
            target = preferred["point"]
            target_reason = "existing central-plaza anchor"
            if not largest[target[1], target[0]]:
                yy, xx = np.where(largest)
                index = int(np.argmin((xx - np.mean(xx)) ** 2 + (yy - np.mean(yy)) ** 2))
                target = [int(xx[index]), int(yy[index])]
                target_reason = "nearest largest-component pixel to its centroid; central anchor unavailable"
            parents, seed, stride = shortest_path_tree(largest, target)
            paths = []
            unavailable = []
            skeleton = np.zeros_like(mask)
            for anchor in annotation["anchors"]:
                x, y = anchor["point"]
                if not largest[y, x]:
                    unavailable.append({**anchor, "status": "blocked_after_clearance" if labels[y, x] == 0 else "outside_largest_visible_component"})
                    continue
                points = extract_path(parents, seed, stride, anchor["point"])
                points_array = np.asarray(points)
                skeleton[points_array[:, 1], points_array[:, 0]] = True
                paths.append((anchor, points))
            caches[radius_px] = (largest, target, target_reason, paths, unavailable, skeleton)
        largest, target, target_reason, fallback_paths, unavailable, _ = caches[radius_px]
        width_clear = erode_disk(mask, corridor_radius_px)
        wide_tree = shortest_path_tree(width_clear, target) if width_clear[target[1], target[0]] else None
        paths = []
        skeleton = np.zeros_like(mask)
        for anchor, fallback in fallback_paths:
            ax, ay = anchor["point"]
            entry_branch = []
            wide_points = extract_path(*wide_tree, anchor["point"]) if wide_tree and width_clear[ay, ax] else []
            if wide_points:
                points = wide_points
                mode = "wide_clearance_shortest_path"
                entry_status = "entry_and_centre_in_same_full_width_component"
            else:
                points = fallback
                mode = "collision_clearance_fallback"
                if not width_clear[ay, ax]:
                    entry_status = "entry_point_outside_full_width_clearance_requires_local_review"
                elif not wide_tree:
                    entry_status = "central_target_outside_full_width_clearance_requires_review"
                else:
                    entry_status = "entry_and_centre_in_different_full_width_components"
                if wide_tree:
                    # Keep the original entry and a genuinely connected narrow
                    # branch; only switch to a wide trunk at an actual shared
                    # pixel. Never snap the entry or fill an occlusion.
                    for join_index, join in enumerate(fallback):
                        if not width_clear[join[1], join[0]]:
                            continue
                        trunk = extract_path(*wide_tree, join)
                        if trunk:
                            entry_branch = fallback[:join_index + 1]
                            points = entry_branch[:-1] + trunk
                            mode = "collision_entry_branch_then_wide_trunk"
                            break
            arr = np.asarray(points)
            skeleton[arr[:, 1], arr[:, 0]] = True
            paths.append((anchor, points, mode, entry_status, entry_branch))
        full_band = dilate_disk(skeleton, corridor_radius_px)
        reserved = full_band & mask
        exclusion = dilate_disk(reserved, radius_px)
        deficient_skeleton = skeleton & ~width_clear
        path_details = []
        for anchor, points, mode, entry_status, entry_branch in paths:
            runs = deficient_runs(points, width_clear)
            path_details.append({
                "anchorId": anchor["id"], "anchorLabel": anchor["label"],
                "from": anchor["point"], "to": target,
                "pathPixelCount": len(points), "pathLengthWorld": (len(points) - 1) * world_per_pixel,
                "polyline": compress_polyline(points),
                "polylineCompression": "collinear vertices removed; exact pixel-centre skeleton preserved",
                "routeSelection": mode,
                "wideAlternativeAvailable": mode == "wide_clearance_shortest_path",
                "wideTrunkAvailable": mode in ("wide_clearance_shortest_path", "collision_entry_branch_then_wide_trunk"),
                "entryConnectionStatus": entry_status,
                "entryBranchPolyline": compress_polyline(entry_branch),
                "entryBranchPixelCount": len(entry_branch),
                "fullRequestedWidthVerifiedOnVisibleRaster": len(runs) == 0,
                "widthDeficientPointCount": sum(r["pointCount"] for r in runs),
                "widthDeficientSegments": runs,
                "physicalDoorOrPortalVerified": False,
            })
        experiments = [grid_experiment(largest, exclusion, side, spacing) for spacing in SPACINGS]
        scenarios.append({
            "mainWorldSide": main_side, "mapWorldSide": side,
            "collisionRadiusWorld": COLLISION_RADIUS,
            "requestedCollisionRadiusPixels": COLLISION_RADIUS / world_per_pixel,
            "effectiveCollisionRadiusPixels": radius_px,
            "effectiveCollisionRadiusWorld": radius_px * world_per_pixel,
            "largestClearComponentPixels": int(largest.sum()),
            "largestClearComponentAreaWorld": int(largest.sum()) * world_per_pixel ** 2,
            "corridor": {
                "requestedTotalWidthWorld": CORRIDOR_WIDTH,
                "effectiveRadiusPixels": corridor_radius_px,
                "effectiveTotalWidthWorld": 2 * corridor_radius_px * world_per_pixel,
                "widthRule": "full radius disk must fit in original visible-ground mask at every skeleton pixel; narrow sections retain only existing ground and are flagged",
                "routeSelectionRule": "prefer full-width shortest path with unchanged endpoints; otherwise retain a real collision-clearance entry branch until its first actual join to the centre's wide component, then use the wide trunk; never snap or fill hidden ground",
                "widthFailureMeaning": "a fallback path may hug an obstacle because its unchanged entry lacks full-width access; no entry snapping is performed, and remaining local failures are review coordinates rather than automatic redraw recommendations",
                "target": target, "targetReason": target_reason,
                "reachableAnchorCount": len(paths), "unavailableAnchors": unavailable,
                "fullWidthRouteCount": sum(p[2] == "wide_clearance_shortest_path" for p in paths),
                "entryBranchReviewCount": sum(p[2] != "wide_clearance_shortest_path" for p in paths),
                "skeletonPixelCount": int(skeleton.sum()),
                "reservedVisiblePixels": int(reserved.sum()),
                "reservedVisibleAreaWorld": int(reserved.sum()) * world_per_pixel ** 2,
                "reservedPixelsInsideLargestClearComponent": int((reserved & largest).sum()),
                "clippedBandPixelCount": int((full_band & ~mask).sum()),
                "widthDeficientSkeletonPixelCount": int(deficient_skeleton.sum()),
                "allSkeletonPointsMeetRequestedWidthOnRaster": not bool(deficient_skeleton.any()),
                "continuousSkeletonForReachableAnchors": True,
                "allMapEntrancesConnected": len(unavailable) == 0,
                "standingFootprintBufferRadiusPixels": radius_px,
                "standingExclusionRule": "reserved ground is dilated by collision radius before excluding any candidate whose enclosing raster corners touch it",
                "paths": path_details,
                "unknownOcclusionsFilled": False,
            },
            "spacingExperiments": experiments,
            "capacity5000Validated": False,
            "worldSizeApproved": False,
            "runtimeNavigationValidated": False,
            "visualCrowdingValidated": False,
        })
    assert input_bytes == path.read_bytes(), "Annotation changed during population probe"
    return {"map": annotation["map"], "annotationPath": str(path),
            "annotationSha256": digest_bytes(input_bytes), "imagePath": annotation["imagePath"],
            "imageSha256": annotation["imageSha256"],
            "uncertainAreas": annotation.get("uncertainAreas", []), "scenarios": scenarios}


def browser_payload(result):
    """Share route geometry per map/scale; full points for requested default only."""
    payload = {k: v for k, v in result.items() if k != "maps"}
    payload["fullPositionScenario"] = {"mainWorldSide": 500, "spacing": 2.5}
    payload["otherScenariosUsePositionSamples"] = True
    payload["maps"] = []
    for item in result["maps"]:
        out = {"map": item["map"], "annotationSha256": item["annotationSha256"],
               "imageSha256": item["imageSha256"], "routeScenarios": [], "scenarios": []}
        for scale in item["scenarios"]:
            corridor = scale["corridor"]
            out["routeScenarios"].append({
                "mainWorldSide": scale["mainWorldSide"], "mapWorldSide": scale["mapWorldSide"],
                "target": corridor["target"],
                "requestedTotalWidthWorld": corridor["requestedTotalWidthWorld"],
                "effectiveRadiusPixels": corridor["effectiveRadiusPixels"],
                "standingFootprintBufferRadiusPixels": corridor["standingFootprintBufferRadiusPixels"],
                "routePolylines": [{"anchorId": p["anchorId"], "points": p["polyline"],
                                    "routeSelection": p["routeSelection"],
                                    "wideAlternativeAvailable": p["wideAlternativeAvailable"],
                                    "wideTrunkAvailable": p["wideTrunkAvailable"],
                                    "entryBranchPolyline": p["entryBranchPolyline"],
                                    "entryConnectionStatus": p["entryConnectionStatus"]}
                                   for p in corridor["paths"]],
                "unreachableAnchors": corridor["unavailableAnchors"],
                "narrowSpots": [{"anchorId": p["anchorId"], **run}
                                for p in corridor["paths"] for run in p["widthDeficientSegments"]],
                "fullWidthVerifiedOnRaster": corridor["allSkeletonPointsMeetRequestedWidthOnRaster"],
                "widthDeficientSkeletonPixelCount": corridor["widthDeficientSkeletonPixelCount"],
                "fullWidthRouteCount": corridor["fullWidthRouteCount"],
                "entryBranchReviewCount": corridor["entryBranchReviewCount"],
                "widthFailureMeaning": corridor["widthFailureMeaning"],
                "narrowSpotsAreAutomaticRedrawRecommendations": False,
                "physicalPortalsVerified": False,
            })
            for experiment in scale["spacingExperiments"]:
                is_full_default = scale["mainWorldSide"] == 500 and experiment["requestedSpacingWorld"] == 2.5
                full = experiment.pop("_fullPositionsForBrowser")
                positions = full if is_full_default else experiment["placedPositionsSample"]
                out["scenarios"].append({
                    "mainWorldSide": scale["mainWorldSide"], "mapWorldSide": scale["mapWorldSide"],
                    "spacing": experiment["requestedSpacingWorld"],
                    "routeScenarioMainWorldSide": scale["mainWorldSide"],
                    "counts": {"raw": experiment["rawCount"], "afterCorridor": experiment["afterCorridorCount"],
                               "placed": experiment["placedCount"], "required": MAX_PEOPLE,
                               "missing": MAX_PEOPLE - experiment["placedCount"]},
                    "positions": positions, "positionCount": len(positions),
                    "positionsAreSample": len(positions) < experiment["placedCount"],
                    "totalPlacedRepresented": experiment["placedCount"],
                    "all5000FootPointsFit": experiment["all5000FootPointsFit"],
                    "gridPhase": experiment["chosenPhase"], "gridStepPixels": experiment["gridStepPixels"],
                    "visualCrowdingValidated": False, "capacity5000Validated": False,
                })
        payload["maps"].append(out)
    return payload


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": "Static unique foot-point grids in the largest 0.38-radius-cleared visible component, excluding explicit shortest-path corridor bands plus foot-radius buffer.",
        "methodChinese": "最大可见净空组件内的唯一脚点格网，预留可达入口到中央广场的四邻域最短通路骨架及3世界单位带状区域，并额外避开脚底圆盘与通路的交叠。",
        "spacingsAreExperimentalChoicesNotStandards": True,
        "corridorWidthIsExperimentalChoiceNotStandard": True,
        "mainWorldSides": list(MAIN_SIDES), "villageIslandAreaRatioToMain": 0.75,
        "gridSpacingsWorld": list(SPACINGS), "requestedCorridorTotalWidthWorld": CORRIDOR_WIDTH,
        "actorCollisionRadiusWorld": COLLISION_RADIUS,
        "actorShadowDiameterReferenceWorld": 2.9,
        "visualWarning": "1-world-unit foot spacing exceeds a 0.76 collision-circle diameter but is much smaller than a 2.9 shadow diameter; nonoverlapping circles do not imply nonoverlapping sprites or names.",
        "clearanceQuantization": "ceil radius in pixels; float grid centres require all four enclosing integer centres in clearance and none in corridor exclusion",
        "projectionLimitation": "uniform image-plane scaling, not a calibrated ground-plane transformation",
        "worldSizeApproved": False, "capacity5000Validated": False,
        "runtimeNavigationValidated": False, "runtimePerformanceValidated": False,
        "visualCrowdingValidated": False, "selfTests": self_tests(), "maps": [],
    }
    for mid in ("main", "village", "island"):
        print("population probe " + mid, flush=True)
        result["maps"].append(run_map(ROOT / "maps" / (mid + ".json")))
    browser = browser_payload(result)
    (ROOT / "population-probe.json").write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    (ROOT / "population-probe.js").write_text("window.POPULATION_PROBE=" + json.dumps(browser, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    compact = [{"map": m["map"], "scenarios": [{"mainSide": s["mainWorldSide"],
        "corridorWidthFailures": s["corridor"]["widthDeficientSkeletonPixelCount"],
        "counts": [{"spacing": e["requestedSpacingWorld"], "raw": e["rawCount"],
                    "afterCorridor": e["afterCorridorCount"], "placed": e["placedCount"]}
                   for e in s["spacingExperiments"]]} for s in m["scenarios"]]}
               for m in result["maps"]]
    print(json.dumps(compact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
