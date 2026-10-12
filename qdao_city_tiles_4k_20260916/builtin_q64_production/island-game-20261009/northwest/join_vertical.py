"""Pixel-preserving hard joins for the four native patches in column one."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


ZONE = Path(__file__).resolve().parent
QA = ZONE / "qa"
STEMS = ["r03_c03_s01_01_a04", "r03_c03_s02_01_a04", "r03_c03_s03_01_a01", "r03_c03_s04_01_a01"]
STRIDE, SIZE, OVERLAP = 1024, 1254, 230


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_image(name: str, pixels: np.ndarray, crop_box=None) -> dict:
    image = Image.fromarray(pixels)
    if crop_box is not None:
        image = image.crop(crop_box)
    path = QA / name
    image.save(path)
    return {"path": str(path), "sha256": digest(path), "dimensions": list(image.size), "cropBoxHalfOpen": crop_box}


def minimum_error_path(error_by_x: np.ndarray) -> np.ndarray:
    width, overlap = error_by_x.shape
    cumulative = error_by_x[0].copy()
    parent = np.zeros((width, overlap), dtype=np.int8)
    offsets = np.array([-1, 0, 1], dtype=np.int8)
    for x in range(1, width):
        candidates = np.stack([
            np.concatenate(([np.inf], cumulative[:-1])),
            cumulative,
            np.concatenate((cumulative[1:], [np.inf])),
        ])
        which = np.argmin(candidates, axis=0)
        parent[x] = offsets[which]
        cumulative = candidates[which, np.arange(overlap)] + error_by_x[x]
    path = np.empty(width, dtype=np.int32)
    path[-1] = int(np.argmin(cumulative))
    for x in range(width - 1, 0, -1):
        path[x - 1] = path[x] + int(parent[x, path[x]])
    assert np.max(np.abs(np.diff(path))) <= 1
    return path


def main() -> None:
    QA.mkdir(exist_ok=True)
    sources, arrays = [], []
    for stem in STEMS:
        path = ZONE / "native" / f"{stem}.png"
        with Image.open(path) as image:
            assert image.size == (SIZE, SIZE)
            assert image.mode in ("RGB", "RGBA")
            if image.mode == "RGBA":
                assert image.getextrema()[3] == (255, 255)
            arrays.append(np.asarray(image.convert("RGB")).copy())
            sources.append({"stem": stem, "path": str(path), "sha256": digest(path), "dimensions": list(image.size), "mode": image.mode})
    column = np.empty((SIZE + 3 * STRIDE, SIZE, 3), dtype=np.uint8)
    column[:SIZE] = arrays[0]
    joins = []
    for i in range(3):
        upper, lower = arrays[i:i + 2]
        delta = upper[STRIDE:].astype(np.float64) - lower[:OVERLAP].astype(np.float64)
        error = np.mean(delta * delta, axis=2).T
        path = minimum_error_path(error)
        pair = np.empty((SIZE + STRIDE, SIZE, 3), dtype=np.uint8)
        for x, overlap_y in enumerate(path):
            split = STRIDE + int(overlap_y)
            pair[:split, x] = upper[:split, x]
            pair[split:, x] = lower[int(overlap_y):, x]
            assert np.array_equal(pair[:split, x], upper[:split, x])
            assert np.array_equal(pair[split:, x], lower[int(overlap_y):, x])
            global_split = (i + 1) * STRIDE + int(overlap_y)
            column[global_split:(i + 1) * STRIDE + SIZE, x] = lower[int(overlap_y):, x]
        name = f"{STEMS[i]}_to_{STEMS[i + 1]}_vertical_hard_minerror"
        joined = save_image(f"{name}_1254x2278.png", pair)
        qa = save_image(f"{name}_seam100pct.png", pair, (0, 899, SIZE, 1379))
        selected = error[np.arange(SIZE), path]
        stats = {
            "overlapMeanAbsRgbDifference": float(np.abs(delta).mean()),
            "overlapP95AbsRgbDifference": float(np.percentile(np.abs(delta), 95)),
            "pathMeanSquaredRgbDifference": float(selected.mean()),
            "straightMeanSquaredRgbDifference": float(error[:, OVERLAP // 2].mean()),
            "overlapPathYMinMax": [int(path.min()), int(path.max())],
            "qaCropPathYMinMax": [int(path.min()) + 125, int(path.max()) + 125],
        }
        joins.append({
            "upperSource": sources[i], "lowerSource": sources[i + 1],
            "pairPlacement": {"upperOrigin": [0, 0], "lowerOrigin": [0, STRIDE]},
            "globalColumnLowerOrigin": [0, (i + 1) * STRIDE],
            "seamPath": {"index": "zero-based x; values are zero-based y inside the 230-row overlap", "yByX": path.tolist()},
            "statistics": stats,
            "outputs": {"combinedPair": joined, "seam100pct": qa},
        })
    # Verify the entire column is exactly the piecewise source selection.
    for x in range(SIZE):
        cutoffs = [0] + [(i + 1) * STRIDE + joins[i]["seamPath"]["yByX"][x] for i in range(3)] + [SIZE + 3 * STRIDE]
        for i in range(4):
            begin, end = cutoffs[i:i + 2]
            assert np.array_equal(column[begin:end, x], arrays[i][begin - i * STRIDE:end - i * STRIDE, x])
    column_out = save_image("first_column_native_hard_minerror_1254x4326.png", column)
    record = {
        "schemaVersion": 1,
        "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "operation": "mechanical vertical native-patch hard seam",
        "status": "candidate_pending_visual_review",
        "isAiGeneration": False,
        "newModelOrQualityClaim": None,
        "sources": sources,
        "sourcePlacementOrigins": [[0, i * STRIDE] for i in range(4)],
        "method": {
            "cost": "per-pixel mean squared difference of unmodified source RGB values at equal overlap coordinates",
            "optimizer": "left-to-right dynamic programming, adjacent-column y step -1, 0 or +1",
            "selection": "upper source above (1024 + seam_y), lower source on and below this boundary",
            "tieBreak": "argmin first match; predecessor -1, 0, +1; topmost terminal on ties",
            "overlapPixels": OVERLAP,
            "registration": False, "resizing": False, "feathering": False,
            "colorCorrection": False, "pixelSynthesis": False,
            "fullColumnExactSourceProvenanceAsserted": True,
        },
        "joins": joins,
        "columnOutput": column_out,
        "limits": ["Only the first native column is covered; this is not a completed 4096 square tile.", "Numerical seam scores are not a substitute for full-width native-resolution visual review."]
    }
    record_path = QA / "first_column_native_hard_minerror.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(record_path), "columnOutput": column_out, "joins": [{"upper": j["upperSource"]["stem"], "lower": j["lowerSource"]["stem"], "statistics": j["statistics"], "outputs": j["outputs"]} for j in joins]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
