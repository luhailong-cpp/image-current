"""Four-boundary hard source selection for the optional upper-beam repair."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


ZONE = Path(__file__).resolve().parent
QA = ZONE / "qa"
BASE_ROW = QA / "row1_current_native_hard_minerror_4326x1254.png"
BASE_CROP = ZONE / "guides" / "r03_c03_repair_upper_beam_a01.native-crop.png"
REPAIR = ZONE / "native" / "r03_c03_repair_upper_beam_a01.png"
CORE = (553, 190, 668, 415)
ROI = (330, 80, 900, 570)
ORIGIN = (627, 0)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def info(path: Path) -> dict:
    return {"path": str(path), "sha256": sha(path)}


def read_rgb(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        assert image.mode in ("RGB", "RGBA")
        if image.mode == "RGBA":
            assert image.getextrema()[3] == (255, 255)
        return np.asarray(image.convert("RGB")).copy()


def dp_path(error: np.ndarray) -> tuple[np.ndarray, dict]:
    length, choices = error.shape
    cumulative = error[0].copy()
    parent = np.zeros(error.shape, dtype=np.int8)
    offsets = np.array([-1, 0, 1], dtype=np.int8)
    for index in range(1, length):
        options = np.stack([
            np.concatenate(([np.inf], cumulative[:-1])),
            cumulative,
            np.concatenate((cumulative[1:], [np.inf])),
        ])
        winner = np.argmin(options, axis=0)
        parent[index] = offsets[winner]
        cumulative = options[winner, np.arange(choices)] + error[index]
    path = np.empty(length, dtype=np.int32)
    path[-1] = int(np.argmin(cumulative))
    for index in range(length - 1, 0, -1):
        path[index - 1] = path[index] + int(parent[index, path[index]])
    assert np.max(np.abs(np.diff(path))) <= 1
    return path, {"pathMeanSquaredRgbDifference": float(error[np.arange(length), path].mean()), "pathMinMax": [int(path.min()), int(path.max())]}


def save(name: str, pixels: np.ndarray, role: str, box=None) -> dict:
    image = Image.fromarray(pixels)
    if box is not None:
        image = image.crop(box)
    path = QA / name
    image.save(path)
    return {**info(path), "dimensions": list(image.size), "role": role, "localCropBoxHalfOpen": box}


def boundary_edges(mask: np.ndarray) -> tuple[list, np.ndarray]:
    # Endpoints straddle the old/new selection boundary, in source-local pixels.
    edges = []
    boundary = np.zeros(mask.shape, dtype=bool)
    for y, x in zip(*np.nonzero(mask[:, 1:] != mask[:, :-1])):
        edges.append([int(x), int(y), int(x + 1), int(y)])
        boundary[y, x:x + 2] = True
    for y, x in zip(*np.nonzero(mask[1:] != mask[:-1])):
        edges.append([int(x), int(y), int(x), int(y + 1)])
        boundary[y:y + 2, x] = True
    return edges, boundary


def statistics(mask: np.ndarray, delta: np.ndarray) -> dict:
    edges, boundary = boundary_edges(mask)
    values = np.abs(delta[boundary])
    return {"selectedNewPixelCount": int(mask.sum()), "boundaryEdgeCount": len(edges), "boundarySourceMismatchMeanAbsRgb": float(values.mean()), "boundarySourceMismatchP95AbsRgb": float(np.percentile(values, 95)), "boundarySourceMismatchMaxAbsRgb": float(values.max()), "statisticsDoNotCertifyVisualContinuity": True}


def main() -> None:
    base, repair, row = read_rgb(BASE_CROP), read_rgb(REPAIR), read_rgb(BASE_ROW)
    assert base.shape == repair.shape == (1254, 1254, 3)
    assert row.shape == (1254, 4326, 3)
    assert np.array_equal(base, row[:, ORIGIN[0]:ORIGIN[0] + 1254])
    derivation_path = BASE_CROP.with_suffix(BASE_CROP.suffix + ".derivation.json")
    derivation = json.loads(derivation_path.read_text(encoding="utf-8-sig"))
    assert derivation["sha256"] == sha(BASE_CROP)
    assert derivation["derivedFrom"]["sha256"] == sha(BASE_ROW)
    assert derivation["sourceCrop"] == [627, 0, 1881, 1254]
    assert derivation["defectLocalBox"] == list(CORE)
    generation_path = REPAIR.with_suffix(REPAIR.suffix + ".generation.json")
    generation = json.loads(generation_path.read_text(encoding="utf-8-sig"))
    assert generation["sha256"] == sha(REPAIR)
    delta = repair.astype(np.float64) - base.astype(np.float64)
    error = np.mean(delta * delta, axis=2)
    x0, y0, x1, y1 = ROI
    cx0, cy0, cx1, cy1 = CORE
    left, left_stats = dp_path(error[y0:y1, x0:cx0])
    right, right_stats = dp_path(error[y0:y1, cx1:x1])
    top, top_stats = dp_path(error[y0:cy0, x0:x1].T)
    bottom, bottom_stats = dp_path(error[cy1:y1, x0:x1].T)
    left += x0
    right += cx1
    top += y0
    bottom += cy1
    yy, xx = np.mgrid[y0:y1, x0:x1]
    mask = np.zeros((1254, 1254), dtype=bool)
    mask[y0:y1, x0:x1] = (xx >= left[:, None]) & (xx < right[:, None]) & (yy >= top[None, :]) & (yy < bottom[None, :])
    assert mask[cy0:cy1, cx0:cx1].all()
    assert not mask[:y0].any() and not mask[y1:].any() and not mask[:, :x0].any() and not mask[:, x1:].any()
    selected = np.where(mask[..., None], repair, base)
    assert np.array_equal(selected[mask], repair[mask])
    assert np.array_equal(selected[~mask], base[~mask])
    result = row.copy()
    result[:, ORIGIN[0]:ORIGIN[0] + 1254] = selected
    assert np.array_equal(result[:, :ORIGIN[0]], row[:, :ORIGIN[0]])
    assert np.array_equal(result[:, ORIGIN[0] + 1254:], row[:, ORIGIN[0] + 1254:])
    edges, boundary = boundary_edges(mask)
    by, bx = np.nonzero(boundary)
    full_boundary_box = (max(0, int(bx.min()) - 64), max(0, int(by.min()) - 64), min(1254, int(bx.max()) + 65), min(1254, int(by.max()) + 65))
    ys, xs = np.nonzero(mask)
    selected_box = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    rectangle_mask = np.zeros(mask.shape, dtype=bool)
    rectangle_mask[180:430, 530:710] = True
    rectangle = np.where(rectangle_mask[..., None], repair, base)
    outputs = {
        "trial2Row": save("row1_beam_repair_trial2.png", result, "candidate row with exact source-selected local repair"),
        "trial2Local": save("row1_beam_repair_trial2_local1254.png", selected, "1254-square native source-selected crop"),
        "sourceSelectionMask": save("row1_beam_repair_trial2_mask.png", mask.astype(np.uint8) * 255, "binary provenance, not game art; 255=new repair, 0=original crop"),
        "trial2AllBoundaries100pct": save("row1_beam_repair_trial2_all_boundaries100pct.png", selected, "all selection boundaries with 64px context, unscaled", full_boundary_box),
        "originalSameContext100pct": save("row1_beam_repair_original_all_boundaries100pct.png", base, "unaltered base at same comparison coordinates, unscaled", full_boundary_box),
        "rectangleSameContext100pct": save("row1_beam_repair_rectangle_all_boundaries100pct.png", rectangle, "reconstructed trial1 rectangle at same coordinates, unscaled", full_boundary_box),
        "trial2OriginalQaBox100pct": save("row1_beam_repair_trial2_100pct.png", selected, "same coordinates as root trial1 seam inspection crop", (423, 80, 813, 540)),
    }
    for name, box in (("right_upper_edge", (810, 265, 975, 390)), ("right_lower_edge", (735, 355, 885, 480))):
        dx0, dy0, dx1, dy1 = box
        paired = np.concatenate((base[dy0:dy1, dx0:dx1], selected[dy0:dy1, dx0:dx1]), axis=1)
        detail = save(f"row1_beam_repair_trial2_{name}_compare100pct.png", paired, "unscaled comparison; left=original, right=trial2; no separator or drawn pixels")
        detail["eachHalfLocalCropBoxHalfOpen"] = list(box)
        outputs[name] = detail
    record = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "status": "optional_material_repair_candidate_pending_visual_review", "isAiGeneration": False,
        "script": info(Path(__file__).resolve()), "baseRow": info(BASE_ROW), "baseCrop": info(BASE_CROP),
        "baseDerivationRecord": info(derivation_path), "baseAssemblyRecord": info(QA / "row1_current_native_hard_minerror.json"),
        "repair": {**info(REPAIR), "generationRecord": info(generation_path), "actualModel": generation.get("actualModel"), "actualQuality": generation.get("actualQuality")},
        "coordinates": {"localSourceDimensions": [1254, 1254], "localToRowOrigin": list(ORIGIN), "localToGlobalOrigin": derivation["globalBox"][:2], "sourceLocalToRowRule": "row=(localX+627,localY)", "sourceLocalToGlobalRule": "global=(localX+8704,localY+8077)", "protectedRepairCoreHalfOpen": list(CORE), "searchRoiHalfOpen": list(ROI), "selectedNewBoundingBoxHalfOpen": selected_box, "allBoundaryQaBoxHalfOpen": full_boundary_box},
        "method": {"cost": "per-pixel mean squared RGB source difference at unchanged coordinates", "optimizer": "four independent minimum-error dynamic-programming paths with consecutive coordinate step -1,0,+1; intersect their four half-planes into a binary selection mask", "claim": "each side is independently minimum-error in its search band; not a globally optimal closed contour", "tieBreak": "argmin first match; predecessor -1,0,+1; smallest terminal coordinate on ties", "registration": False, "resizing": False, "feathering": False, "colorCorrection": False, "pixelSynthesis": False},
        "paths": {
            "left": {"index": "local y=80+i", "value": "local x, new selection on/right of this path", "xByY": left.tolist(), "statisticsRelativeToBand": left_stats},
            "right": {"index": "local y=80+i", "value": "local x, new selection left of this path", "xByY": right.tolist(), "statisticsRelativeToBand": right_stats},
            "top": {"index": "local x=330+i", "value": "local y, new selection on/below this path", "yByX": top.tolist(), "statisticsRelativeToBand": top_stats},
            "bottom": {"index": "local x=330+i", "value": "local y, new selection above this path", "yByX": bottom.tolist(), "statisticsRelativeToBand": bottom_stats},
        },
        "actualBoundaryEdges": {"format": "[localX1,localY1,localX2,localY2]; endpoints straddle binary source selection", "edges": edges},
        "comparison": {"rectangleTrial1": statistics(rectangle_mask, delta), "fourBoundaryTrial2": statistics(mask, delta)},
        "sourceProvenanceAssertions": {"protectedCoreEntirelyNewRepair": True, "everySelectedPixelExactlyMatchesUnmodifiedRepair": True, "everyOtherPixelExactlyMatchesBase": True, "rowOutsideLocalCropUnchanged": True, "newRepairPixelCount": int(mask.sum()), "basePixelCountInCrop": int(mask.size - mask.sum())},
        "outputs": outputs,
        "limits": ["Optional material repair only, not structural or formal acceptance.", "Boundary source-error metrics cannot certify visual geometry; inspect all-boundaries 100% crop.", "Does not modify native images, assembler or progress."]
    }
    record_path = QA / "row1_beam_repair_trial2.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(record_path), "comparison": record["comparison"], "selectedNewBoundingBoxHalfOpen": selected_box, "outputs": outputs}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
