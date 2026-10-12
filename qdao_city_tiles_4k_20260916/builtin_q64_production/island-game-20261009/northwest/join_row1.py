"""Compose current first-row native patches without modifying source pixels."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
from join_vertical import minimum_error_path

ZONE = Path(__file__).resolve().parent
QA = ZONE / "qa"
STEMS = ["r03_c03_s01_01_a04", "r03_c03_s01_02_a03", "r03_c03_s01_03_a03", "r03_c03_s01_04_a03"]
SIZE, STRIDE, OVERLAP = 1254, 1024, 230


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_image(name, pixels, box=None):
    image = Image.fromarray(pixels)
    if box is not None:
        image = image.crop(box)
    path = QA / name
    image.save(path)
    return {"path": str(path), "sha256": digest(path), "dimensions": list(image.size), "cropBoxHalfOpen": box}


def main():
    QA.mkdir(exist_ok=True)
    arrays, sources = [], []
    for stem in STEMS:
        path = ZONE / "native" / f"{stem}.png"
        with Image.open(path) as im:
            assert im.size == (SIZE, SIZE) and im.mode in ("RGB", "RGBA")
            if im.mode == "RGBA":
                assert im.getextrema()[3] == (255, 255)
            arrays.append(np.asarray(im.convert("RGB")).copy())
            sources.append({"stem": stem, "path": str(path), "sha256": digest(path), "dimensions": list(im.size), "mode": im.mode})
    row = np.empty((SIZE, SIZE + 3 * STRIDE, 3), dtype=np.uint8)
    row[:, :SIZE] = arrays[0]
    joins = []
    for i in range(3):
        left, right = arrays[i:i + 2]
        delta = left[:, STRIDE:].astype(np.float64) - right[:, :OVERLAP].astype(np.float64)
        error = np.mean(delta * delta, axis=2)
        path = minimum_error_path(error)
        pair = np.empty((SIZE, SIZE + STRIDE, 3), dtype=np.uint8)
        for y, overlap_x in enumerate(path):
            split = STRIDE + int(overlap_x)
            pair[y, :split] = left[y, :split]
            pair[y, split:] = right[y, int(overlap_x):]
            assert np.array_equal(pair[y, :split], left[y, :split])
            assert np.array_equal(pair[y, split:], right[y, int(overlap_x):])
            global_split = (i + 1) * STRIDE + int(overlap_x)
            row[y, global_split:(i + 1) * STRIDE + SIZE] = right[y, int(overlap_x):]
        name = f"{STEMS[i]}_to_{STEMS[i + 1]}_row1_hard_minerror"
        outputs = {
            "combinedPair": save_image(f"{name}_2278x1254.png", pair),
            "seam100pct": save_image(f"{name}_seam100pct.png", pair, (899, 0, 1379, SIZE)),
        }
        selected = error[np.arange(SIZE), path]
        joins.append({
            "leftSource": sources[i], "rightSource": sources[i + 1],
            "pairPlacementOrigins": [[0, 0], [STRIDE, 0]],
            "rowRightSourceOrigin": [(i + 1) * STRIDE, 0],
            "seamPath": {"index": "zero-based y, value zero-based overlap x", "xByY": path.tolist()},
            "statistics": {
                "overlapMAE": float(np.abs(delta).mean()),
                "overlapP95AbsoluteRgbDifference": float(np.percentile(np.abs(delta), 95)),
                "pathMSE": float(selected.mean()),
                "straightMSE": float(error[:, OVERLAP // 2].mean()),
                "overlapPathXMinMax": [int(path.min()), int(path.max())],
                "qaPathXMinMax": [125 + int(path.min()), 125 + int(path.max())],
            },
            "outputs": outputs,
        })
    for y in range(SIZE):
        cuts = [0] + [(i + 1) * STRIDE + joins[i]["seamPath"]["xByY"][y] for i in range(3)] + [SIZE + 3 * STRIDE]
        for i in range(4):
            begin, end = cuts[i:i + 2]
            assert np.array_equal(row[y, begin:end], arrays[i][y, begin - i * STRIDE:end - i * STRIDE])
    output = save_image("row1_current_native_hard_minerror_4326x1254.png", row)
    record = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "operation": "mechanical four-native first-row hard seam", "status": "candidate_pending_visual_review", "isAiGeneration": False,
        "sources": sources, "sourcePlacementOrigins": [[i * STRIDE, 0] for i in range(4)],
        "method": {
            "cost": "Mean squared difference of unmodified 8-bit RGB values at identical overlap coordinates",
            "optimizer": "Top-to-bottom dynamic programming, adjacent-row overlap-x step -1, 0 or +1",
            "selection": "Left source before 1024+path[y], right source at and after it",
            "tieBreak": "numpy first argmin; predecessor offsets -1,0,+1; leftmost final minimum",
            "overlapPixels": OVERLAP, "registration": False, "resizing": False, "feathering": False, "colorCorrection": False, "pixelSynthesis": False,
            "exactFullRowSourceProvenanceAsserted": True,
            "dpImplementation": {"path": str(ZONE / "join_vertical.py"), "sha256": digest(ZONE / "join_vertical.py")},
        },
        "joins": joins, "rowOutput": output,
        "limits": ["First row only; not a complete 4096-square tile.", "Visual seam and outer-edge acceptance are independent of these numeric scores."]
    }
    record_path = QA / "row1_current_native_hard_minerror.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(record_path), "rowOutput": output, "joins": [{"left": j["leftSource"]["stem"], "right": j["rightSource"]["stem"], "statistics": j["statistics"], "outputs": j["outputs"]} for j in joins]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
