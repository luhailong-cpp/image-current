"""Join row four by source-pixel selection only; no drawing or synthesis."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


ZONE = Path(__file__).resolve().parent
QA = ZONE / "qa"
STEMS = [f"r03_c03_s04_{c:02d}_a01" for c in range(1, 5)]
SIZE, STRIDE, OVERLAP = 1254, 1024, 230


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hard_path(error: np.ndarray) -> np.ndarray:
    cumulative = error[0].copy()
    parent = np.zeros(error.shape, dtype=np.int8)
    offsets = np.array([-1, 0, 1], dtype=np.int8)
    for y in range(1, error.shape[0]):
        candidates = np.stack([
            np.concatenate(([np.inf], cumulative[:-1])),
            cumulative,
            np.concatenate((cumulative[1:], [np.inf])),
        ])
        which = np.argmin(candidates, axis=0)
        parent[y] = offsets[which]
        cumulative = candidates[which, np.arange(OVERLAP)] + error[y]
    path = np.empty(error.shape[0], dtype=np.int32)
    path[-1] = int(np.argmin(cumulative))
    for y in range(error.shape[0] - 1, 0, -1):
        path[y - 1] = path[y] + int(parent[y, path[y]])
    assert np.max(np.abs(np.diff(path))) <= 1
    return path


def save(name: str, image: Image.Image, box=None) -> dict:
    if box is not None:
        image = image.crop(box)
    path = QA / name
    image.save(path)
    return {"path": str(path), "sha256": digest(path), "dimensions": list(image.size), "rowCropBoxHalfOpen": box}


def main() -> None:
    QA.mkdir(exist_ok=True)
    arrays, sources = [], []
    for i, stem in enumerate(STEMS):
        path = ZONE / "native" / f"{stem}.png"
        guide_path = ZONE / "guides" / f"{stem}.layout-with-native.png"
        input_path = ZONE / "guides" / f"{stem}.input.json"
        info = json.loads(input_path.read_text(encoding="utf-8-sig"))
        assert info["globalBox"] == [8077 + i * STRIDE, 11149, 9331 + i * STRIDE, 12403]
        assert info["inputs"][0]["sha256"] == digest(guide_path)
        with Image.open(path) as image:
            assert image.size == (SIZE, SIZE)
            assert image.mode in ("RGB", "RGBA")
            if image.mode == "RGBA":
                assert image.getextrema()[3] == (255, 255)
            arrays.append(np.asarray(image.convert("RGB")).copy())
            sources.append({
                "stem": stem, "path": str(path), "sha256": digest(path),
                "dimensions": list(image.size), "originalMode": image.mode,
                "rowOrigin": [i * STRIDE, 0], "globalBox": info["globalBox"],
                "inputRecord": {"path": str(input_path), "sha256": digest(input_path)},
                "guide": {"path": str(guide_path), "sha256": digest(guide_path), "role": "layout-only; inspected, never included in output pixels"},
            })
    row = np.empty((SIZE, SIZE + 3 * STRIDE, 3), dtype=np.uint8)
    row[:, :SIZE] = arrays[0]
    joins = []
    for i in range(3):
        left, right = arrays[i:i + 2]
        delta = left[:, STRIDE:].astype(np.float64) - right[:, :OVERLAP].astype(np.float64)
        error = np.mean(delta * delta, axis=2)
        path = hard_path(error)
        for y, overlap_x in enumerate(path):
            global_split = (i + 1) * STRIDE + int(overlap_x)
            row[y, global_split:(i + 1) * STRIDE + SIZE] = right[y, int(overlap_x):]
        selected = error[np.arange(SIZE), path]
        joins.append({
            "leftSource": sources[i]["stem"], "rightSource": sources[i + 1]["stem"],
            "overlapRowBoxHalfOpen": [(i + 1) * STRIDE, 0, (i + 1) * STRIDE + OVERLAP, SIZE],
            "seamPath": {"index": "zero-based y; x values inside 230px overlap; row x=(joinIndex+1)*1024+xByY[y]", "xByY": path.tolist()},
            "statistics": {
                "overlapMeanAbsRgbDifference": float(np.abs(delta).mean()),
                "overlapP95AbsRgbDifference": float(np.percentile(np.abs(delta), 95)),
                "pathMeanSquaredRgbDifference": float(selected.mean()),
                "straightMeanSquaredRgbDifference": float(error[:, OVERLAP // 2].mean()),
                "overlapPathXMinMax": [int(path.min()), int(path.max())],
                "seamCropPathXMinMax": [int(path.min()) + 125, int(path.max()) + 125],
            },
        })
    for y in range(SIZE):
        cutoffs = [0] + [(i + 1) * STRIDE + joins[i]["seamPath"]["xByY"][y] for i in range(3)] + [SIZE + 3 * STRIDE]
        for i in range(4):
            begin, end = cutoffs[i:i + 2]
            assert np.array_equal(row[y, begin:end], arrays[i][y, begin - i * STRIDE:end - i * STRIDE])
    image = Image.fromarray(row)
    row_output = save("row4_native_hard_minerror_4326x1254.png", image)
    for i, join in enumerate(joins):
        join["seam100pct"] = save(
            f"row4_s04_{i + 1:02d}_to_s04_{i + 2:02d}_hard_minerror_seam100pct.png",
            image, (899 + i * STRIDE, 0, 1379 + i * STRIDE, SIZE),
        )
    record = {
        "schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "operation": "mechanical native row-four minimum-error hard seam",
        "status": "candidate_pending_visual_review", "isAiGeneration": False,
        "newModelOrQualityClaim": None, "sources": sources,
        "globalBox": [8077, 11149, 12403, 12403], "outputDimensions": [4326, 1254],
        "method": {
            "cost": "mean squared difference of unmodified source RGB values at identical overlap coordinates",
            "optimizer": "top-to-bottom dynamic programming with adjacent-row x step -1, 0 or +1",
            "selection": "left source before seam, right source on/after seam; no blending",
            "tieBreak": "argmin first match; predecessor -1, 0, +1; leftmost terminal on ties",
            "overlapPixels": OVERLAP, "registration": False, "resizing": False,
            "feathering": False, "colorCorrection": False, "pixelSynthesis": False,
            "allOutputPixelsExactlyMatchSelectedSourceAsserted": True,
        },
        "joins": joins, "rowOutput": row_output,
        "limits": [
            "Only bottom native row is composed, not a complete 4096-square tile.",
            "Upper overlap with middle row remains unverified; no formal acceptance.",
            "Numerical seam scores do not prove visual geometry continuity.",
        ],
    }
    record_path = QA / "row4_native_hard_minerror.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(record_path), "rowOutput": row_output, "joins": [{k: v for k, v in join.items() if k != "seamPath"} for join in joins]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
