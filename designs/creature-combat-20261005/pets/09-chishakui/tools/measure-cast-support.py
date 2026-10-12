#!/usr/bin/env python3
"""Read-only pixel landmarks for cast W; never edits sprites.

The indigo boot paint and bottom alpha band are image-space proxies, not bones,
foot pressure, or engine pivots. Silhouette/lighting changes can alter them.
Use alongside full-frame visual review; no automatic pass/fail is assigned.
"""
import argparse
import hashlib
import json
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ROIS = {"screenLeft": (250, 835, 510, 1000),
        "screenRight": (550, 835, 790, 1000)}

def components(mask):
    todo = mask.copy()
    height, width = todo.shape
    for y, x in zip(*np.nonzero(mask)):
        if not todo[y, x]:
            continue
        queue = deque([(int(x), int(y))])
        todo[y, x] = False
        points = []
        while queue:
            px, py = queue.popleft()
            points.append((px, py))
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = px + dx, py + dy
                if 0 <= nx < width and 0 <= ny < height and todo[ny, nx]:
                    todo[ny, nx] = False
                    queue.append((nx, ny))
        yield np.asarray(points)

def metric(frame_path):
    with Image.open(frame_path) as im:
        if im.size != (1024, 1024) or im.mode != "RGBA":
            raise ValueError(f"Expected 1024 RGBA: {frame_path}")
        rgba = np.asarray(im).astype(np.int16)
    result = {}
    for side, (x0, y0, x1, y1) in ROIS.items():
        roi = rgba[y0:y1, x0:x1]
        red, green, blue, alpha = [roi[:, :, i] for i in range(4)]
        # Fixed chromatic rule for the existing indigo paint; warm gold excluded.
        mask = ((alpha >= 128) & (blue - red >= 12)
                & (blue - green >= 5) & (red < 150))
        kept = []
        for pts in components(mask):
            # Reject tiny paint flecks and upper trouser/robe blue components.
            if (len(pts) >= 20 and int(pts[:, 1].max()) + y0 >= 900
                    and int(pts[:, 1].min()) > 0):
                kept.append(pts + np.array([x0, y0]))
        if not kept:
            raise ValueError(f"No boot paint found: {frame_path} {side}")
        pts = np.concatenate(kept)
        silhouette = roi[:, :, 3] >= 16
        sy, sx = np.nonzero(silhouette)
        bottom = int(sy.max())
        band = sy >= bottom - 5
        result[side] = {
            "bluePaintPixelCount": int(len(pts)),
            "bluePaintComponentCount": len(kept),
            "bluePaintCentroid": [round(float(v), 3) for v in pts.mean(axis=0)],
            "bluePaintBBox": [int(pts[:, 0].min()), int(pts[:, 1].min()),
                             int(pts[:, 0].max()) + 1, int(pts[:, 1].max()) + 1],
            "alphaBottomY": bottom + y0,
            "bottomSixRowsCentroid": [
                round(float(sx[band].mean()) + x0, 3),
                round(float(sy[band].mean()) + y0, 3)],
            "bottomSixRowsXRange": [int(sx[band].min()) + x0,
                                   int(sx[band].max()) + x0],
        }
    return result

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", help="JSON path inside this creature directory; omit for stdout")
    args = ap.parse_args()
    frames = []
    for n in range(1, 17):
        p = ROOT / "runtime" / "cast" / "W" / f"{n:02d}.png"
        frames.append({"frame": n, "file": p.relative_to(ROOT).as_posix(),
                       "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                       "measurements": metric(p)})
    baseline = {
        side: [(frames[6]["measurements"][side]["bluePaintCentroid"][axis]
                + frames[10]["measurements"][side]["bluePaintCentroid"][axis]) / 2
               for axis in (0, 1)]
        for side in ROIS
    }
    for frame in frames:
        for side in ROIS:
            vals = frame["measurements"][side]
            vals["blueCentroidDeltaFromMean07And11"] = [
                round(vals["bluePaintCentroid"][axis] - baseline[side][axis], 3)
                for axis in (0, 1)]
    report = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "script": "tools/measure-cast-support.py",
        "scriptSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "action": "cast", "direction": "W", "coordinates": "1024 canvas; x right, y down",
        "method": {
            "roiXYXYExclusive": ROIS,
            "bluePredicate": "alpha>=128; B-R>=12; B-G>=5; R<150",
            "componentRule": "4-connected; area>=20; max canvas y>=900; not touching ROI top",
            "bottomBand": "alpha>=16; bottommost six rows within each fixed shoe ROI",
            "baseline": "Mean paint centroids of frames 07 and 11",
            "noResamplingNoAlignment": True,
        },
        "limitations": [
            "Pixel paint centroid and alpha band are not skeleton joints or physical contact points.",
            "Changes in painted pattern, shoe orientation, lighting, and occlusion affect measurements.",
            "No automatic animation pass/fail; compare full frames and playback separately.",
            "Source SHA identifies exact current PNG; old reports are historical after repair.",
        ],
        "baselineBlueCentroids": baseline,
        "frames": frames,
    }
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        path = Path(args.output)
        if not path.is_absolute():
            path = ROOT / path
        path = path.resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise ValueError("Output must remain inside this creature directory")
        path.write_text(payload + "\n", encoding="utf-8")
        print(str(path))
    else:
        print(payload)
    if args.output:
        for n in [7, 8, 9, 10, 11]:
            item = frames[n - 1]
            print(json.dumps({"frame": n, "shoes": item["measurements"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()

