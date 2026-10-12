"""Mechanical, pixel-preserving native patch join; no drawing or image synthesis."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image


ZONE = Path(__file__).resolve().parent
QA = ZONE / "qa"
LEFT = ZONE / "native" / "r03_c03_s01_01_a04.png"
RIGHT = ZONE / "native" / "r03_c03_s01_02_a02.png"
STEM = "s01_01a04_to_s01_02a02_hard_minerror"
STRIDE = 1024


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    QA.mkdir(exist_ok=True)
    originals = [Image.open(path) for path in (LEFT, RIGHT)]
    if any(im.size != (1254, 1254) or im.mode not in ("RGB", "RGBA") for im in originals):
        raise ValueError("Expected two 1254-square RGB/RGBA native sources.")
    if any(im.mode == "RGBA" and im.getextrema()[3] != (255, 255) for im in originals):
        raise ValueError("Non-opaque alpha is outside this join's RGB cost contract.")
    left, right = [np.asarray(im.convert("RGB")) for im in originals]
    height, width, _ = left.shape
    overlap = width - STRIDE
    delta = left[:, STRIDE:].astype(np.float64) - right[:, :overlap].astype(np.float64)
    error = np.mean(delta * delta, axis=2)

    # Dynamic programming: every row picks one overlap column; adjacent rows
    # differ by at most one column. No registration or color operations.
    cumulative = error[0].copy()
    back = np.zeros((height, overlap), dtype=np.int8)
    offsets = np.array([-1, 0, 1], dtype=np.int8)
    for y in range(1, height):
        candidates = np.stack(
            (
                np.concatenate(([np.inf], cumulative[:-1])),
                cumulative,
                np.concatenate((cumulative[1:], [np.inf])),
            )
        )
        winner = np.argmin(candidates, axis=0)
        back[y] = offsets[winner]
        cumulative = candidates[winner, np.arange(overlap)] + error[y]
    path = np.empty(height, dtype=np.int32)
    path[-1] = int(np.argmin(cumulative))
    for y in range(height - 1, 0, -1):
        path[y - 1] = path[y] + int(back[y, path[y]])
    assert np.max(np.abs(np.diff(path))) <= 1

    output = np.empty((height, STRIDE + width, 3), dtype=np.uint8)
    for y, overlap_x in enumerate(path):
        split = STRIDE + int(overlap_x)
        output[y, :split] = left[y, :split]
        output[y, split:] = right[y, int(overlap_x):]
        # Exact source-pixel provenance, not a perceptual similarity check.
        assert np.array_equal(output[y, :split], left[y, :split])
        assert np.array_equal(output[y, split:], right[y, int(overlap_x):])
    combined = Image.fromarray(output)
    outputs = {}
    output_specs = {
        "combined": (f"{STEM}_2278x1254.png", None),
        "seam100pct": (f"{STEM}_seam100pct.png", (899, 0, 1379, 1254)),
        "detail_y535_650": (f"{STEM}_y535-650.png", (899, 535, 1379, 651)),
        "detail_y795_980": (f"{STEM}_y795-980.png", (899, 795, 1379, 981)),
    }
    for role, (name, box) in output_specs.items():
        dest = QA / name
        im = combined if box is None else combined.crop(box)
        im.save(dest)
        outputs[role] = {
            "path": str(dest),
            "dimensions": list(im.size),
            "sha256": sha256(dest),
            "combinedCropBoxHalfOpen": box,
        }

    selected_error = error[np.arange(height), path]
    straight_error = error[:, overlap // 2]
    segments = {}
    for name, start, stop in (("full", 0, height), ("y535_650", 535, 651), ("y795_980", 795, 981)):
        p = path[start:stop]
        segments[name] = {
            "yInclusive": [start, stop - 1],
            "overlapPathXMinMax": [int(p.min()), int(p.max())],
            "qaCropPathXMinMax": [int(p.min()) + 125, int(p.max()) + 125],
            "pathMeanSquaredRgbDifference": float(selected_error[start:stop].mean()),
            "straightMeanSquaredRgbDifference": float(straight_error[start:stop].mean()),
        }
    record = {
        "schemaVersion": 1,
        "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "operation": "mechanical native-source minimum-error hard seam",
        "status": "candidate_pending_visual_review",
        "isAiGeneration": False,
        "newModelOrQualityClaim": None,
        "sources": [
            {"role": role, "path": str(path), "sha256": sha256(path), "dimensions": list(im.size), "originalMode": im.mode}
            for role, path, im in zip(("left", "right"), (LEFT, RIGHT), originals)
        ],
        "placement": {"leftOrigin": [0, 0], "rightOrigin": [1024, 0], "overlapWidth": 230, "combinedDimensions": [2278, 1254]},
        "method": {
            "cost": "per-pixel mean squared difference of unmodified 8-bit RGB channels at matching overlap coordinates",
            "optimizer": "top-to-bottom dynamic programming minimizing summed cost; adjacent-row x step constrained to -1, 0 or +1",
            "boundaryRule": "At each row, left supplies combined x < 1024 + seam_x; right supplies x >= 1024 + seam_x.",
            "tieBreak": "numpy argmin first match, predecessor offsets ordered -1, 0, +1; terminal column leftmost on ties",
            "registration": False,
            "resizing": False,
            "feathering": False,
            "colorCorrection": False,
            "pixelSynthesis": False,
            "verifiedOutputPixelsExactlyMatchSelectedSource": True,
        },
        "seamPath": {"index": "zero-based y; values are zero-based x in 230-pixel overlap", "xByY": path.tolist()},
        "statistics": segments,
        "outputs": outputs,
        "limits": ["Numerical seam cost does not prove geometry continuity.", "This joins only two native patches, not a complete 4096 tile or an accepted external tile seam."],
    }
    record_path = QA / f"{STEM}.json"
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(record_path), "outputs": outputs, "statistics": segments}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
