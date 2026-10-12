"""Measure unchanged exported sequences; metrics are review aids, not playback approval."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SPECS = {"hit": (6, 40), "attack": (12, 30), "cast": (16, 45)}

def load_frame(path):
    with Image.open(path) as source:
        image = np.asarray(source.convert("RGBA"), dtype=np.float32) / 255.0
    alpha = image[:, :, 3]
    visible = alpha > 0.25
    ys, xs = np.nonzero(visible)
    weights = alpha[ys, xs]
    info = {
        "file": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "solidAlphaBBox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
        "alphaWeightedCentroid": [round(float(np.average(xs, weights=weights)), 2), round(float(np.average(ys, weights=weights)), 2)],
        "alphaEdgeMax": float(max(alpha[0].max(), alpha[-1].max(), alpha[:, 0].max(), alpha[:, -1].max())),
    }
    premultiplied = image.copy()
    premultiplied[:, :, :3] *= alpha[:, :, None]
    return info, premultiplied, visible

def pair_metrics(a, b):
    info_a, pixels_a, mask_a = a
    info_b, pixels_b, mask_b = b
    union = mask_a | mask_b
    intersection = mask_a & mask_b
    delta = np.abs(pixels_b - pixels_a)
    return {
        "from": info_a["file"], "to": info_b["file"],
        "silhouetteIoU": round(float(intersection.sum() / union.sum()), 4),
        "premultipliedRGBAAbsoluteMeanOnVisibleUnion": round(float(delta[union].mean()), 5),
        "alphaCentroidDistancePx": round(float(np.linalg.norm(np.array(info_a["alphaWeightedCentroid"]) - np.array(info_b["alphaWeightedCentroid"]))), 2),
    }

def main():
    groups = []
    all_sequences = {}
    for action, (count, duration) in SPECS.items():
        for direction in ("E", "W"):
            sequence = [load_frame(ROOT / "runtime" / action / direction / f"{index:02}.png") for index in range(1, count + 1)]
            pairs = [pair_metrics(a, b) for a, b in zip(sequence, sequence[1:])]
            closure = pair_metrics(sequence[-1], sequence[0])
            median = float(np.median([pair["premultipliedRGBAAbsoluteMeanOnVisibleUnion"] for pair in pairs]))
            for pair in pairs + [closure]:
                pair["differenceToGroupMedianRatio"] = round(pair["premultipliedRGBAAbsoluteMeanOnVisibleUnion"] / median, 3) if median else None
            group = {"id": f"{action}-{direction}", "frameDurationMs": duration,
                     "frames": [entry[0] for entry in sequence], "adjacentPairs": pairs,
                     "lastToFirst": closure, "medianAdjacentDifference": median}
            groups.append(group)
            all_sequences[(action, direction)] = sequence
    transitions = []
    for direction in ("E", "W"):
        for source in SPECS:
            for target in SPECS:
                if source != target:
                    transitions.append(pair_metrics(all_sequences[(source, direction)][-1], all_sequences[(target, direction)][0]))
    result = {"checkedAt": datetime.now(timezone.utc).isoformat(), "method": "Static analysis of exact 1024 RGBA exported pixels: alpha>0.25 silhouette IoU, premultiplied RGBA mean absolute difference, alpha-weighted centroid, adjacent/last-to-first/cross-action transitions. No image modifications or alignment applied.",
              "limits": "Metrics locate changes; they neither prove unnatural motion nor replace actual playback. Cloth/light differences contribute heavily. No automatic pass/fail thresholds or anatomical classifications.",
              "groups": groups, "crossActionTransitions": transitions,
              "playbackStatus": "not-verified-browser-policy-blocked"}
    (ROOT / "records" / "sequence-continuity-metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps([{ "group": group["id"], "largestAdjacentChange": max(group["adjacentPairs"], key=lambda pair: pair["premultipliedRGBAAbsoluteMeanOnVisibleUnion"]), "lastToFirst": group["lastToFirst"] } for group in groups], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
