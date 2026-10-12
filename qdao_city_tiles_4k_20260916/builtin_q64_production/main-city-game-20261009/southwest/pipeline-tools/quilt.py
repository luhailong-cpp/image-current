"""Frozen native-only quilting functions extracted from the existing assembler.
No file I/O, source loading, tile-specific origins, or global state mutation.
"""
from __future__ import annotations
import hashlib
import numpy as np
GRID, CORE, HALO = 4, 1024, 115
OVERLAP, PATCH, FINAL = 230, 1254, 4096


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def choose_rectangle(available: set[tuple[int, int]]) -> tuple[int, int, int, int] | None:
    """Largest completely populated rectangle; ties prefer width, then top/left."""
    options = []
    for top in range(1, GRID + 1):
        for left in range(1, GRID + 1):
            for bottom in range(top, GRID + 1):
                for right in range(left, GRID + 1):
                    cells = {(r, c) for r in range(top, bottom + 1) for c in range(left, right + 1)}
                    if cells <= available:
                        options.append(((len(cells), right - left + 1, -top, -left),
                                        (top, left, bottom, right)))
    return max(options)[1] if options else None


def minimum_seam(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Minimum squared-error seam, with weak center and edge regularization."""
    require(left.shape == right.shape and left.ndim == 3, "Invalid seam input geometry.")
    difference = left.astype(np.float32) - right.astype(np.float32)
    cost = np.mean(difference * difference, axis=2)
    height, width = cost.shape
    center = (width - 1) / 2.0
    normalized = np.abs((np.arange(width, dtype=np.float32) - center) / max(center, 1.0))
    typical = float(np.median(cost)) + 1.0
    cost += normalized[None, :] ** 4 * typical * 0.16
    margin = min(24, max(1, width // 12))
    cost[:, :margin] += typical * 8.0
    cost[:, -margin:] += typical * 8.0
    previous = cost[0].copy()
    backtrack = np.zeros((height, width), dtype=np.int8)
    for y in range(1, height):
        candidates = np.stack((np.r_[np.float32(np.inf), previous[:-1]], previous,
                               np.r_[previous[1:], np.float32(np.inf)]))
        choices = np.argmin(candidates, axis=0)
        backtrack[y] = choices.astype(np.int8) - 1
        previous = cost[y] + np.take_along_axis(candidates, choices[None, :], axis=0)[0]
    seam = np.empty(height, dtype=np.int32)
    seam[-1] = int(np.argmin(previous))
    for y in range(height - 1, 0, -1):
        seam[y - 1] = seam[y] + int(backtrack[y, seam[y]])
    return seam


def feather_mask(seam: np.ndarray, width: int, radius: int) -> np.ndarray:
    require(radius in (0, 1, 2), "Feather radius must be 0, 1, or 2 pixels.")
    distance = np.arange(width, dtype=np.int32)[None, :] - seam[:, None]
    if radius == 0:
        return np.uint8(distance >= 0) * 255
    # Bounded linear feather: exactly no blend beyond radius pixels of the seam.
    numerator = np.clip(distance + radius, 0, radius * 2) * 255
    return ((numerator + radius) // (radius * 2)).astype(np.uint8)


def blend_exact(left: np.ndarray, right: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    weight = alpha.astype(np.uint32)[..., None]
    return ((left.astype(np.uint32) * (255 - weight)
             + right.astype(np.uint32) * weight + 127) // 255).astype(np.uint8)


def append(base: np.ndarray, patch: np.ndarray, label: str, radius: int) -> tuple[np.ndarray, dict]:
    require(base.shape[0] == patch.shape[0] and min(base.shape[1], patch.shape[1]) >= OVERLAP,
            f"Invalid overlap geometry: {label}")
    left, right = base[:, -OVERLAP:], patch[:, :OVERLAP]
    seam = minimum_seam(left, right)
    alpha = feather_mask(seam, OVERLAP, radius)
    mixed = blend_exact(left, right, alpha)
    difference = np.abs(left.astype(np.int16) - right.astype(np.int16))
    metrics = {"label": label, "overlapPixels": OVERLAP, "seamLength": len(seam),
               "seamMin": int(seam.min()), "seamMax": int(seam.max()),
               "seamSha256Int32LittleEndian": hashlib.sha256(seam.astype("<i4").tobytes()).hexdigest(),
               "beforeBlendMeanAbsoluteDifference": float(difference.mean()),
               "beforeBlendP95AbsoluteDifference": float(np.percentile(difference, 95)),
               "featherRadiusPixels": radius, "geometryValidated": False}
    return np.concatenate((base[:, :-OVERLAP], mixed, patch[:, OVERLAP:]), axis=1), metrics


def assemble_pixels(arrays: dict, rectangle: tuple[int, int, int, int], radius: int) -> tuple[np.ndarray, list]:
    top, left, bottom, right = rectangle
    strips, metrics = [], []
    for row in range(top, bottom + 1):
        strip = arrays[(row, left)]
        for column in range(left + 1, right + 1):
            strip, metric = append(strip, arrays[(row, column)],
                                   f"row{row:02d}_c{column - 1:02d}_c{column:02d}", radius)
            metrics.append(metric)
        strips.append(strip)
    combined = np.transpose(strips[0], (1, 0, 2))
    for row, strip in enumerate(strips[1:], top + 1):
        combined, metric = append(combined, np.transpose(strip, (1, 0, 2)),
                                  f"rows{row - 1:02d}_{row:02d}", radius)
        metrics.append(metric)
    combined = np.transpose(combined, (1, 0, 2))
    require(combined.shape == ((bottom - top + 1) * CORE + OVERLAP,
                               (right - left + 1) * CORE + OVERLAP, 3),
            "Assembled native coverage does not match recorded coordinates.")
    return combined, metrics


def qa_regions(width: int, height: int, rows: int, columns: int, offset: int) -> list[dict]:
    regions = []
    # Cover the entire potential 230-pixel seam corridor plus four pixels.
    margin = HALO + 4
    xs, ys = [offset + c * CORE for c in range(1, columns)], [offset + r * CORE for r in range(1, rows)]
    for x in xs:
        regions.append({"name": f"vertical_x{x}_full", "kind": "full-length-internal-seam",
                        "box": [max(0, x - margin), 0, min(width, x + margin), height]})
    for y in ys:
        regions.append({"name": f"horizontal_y{y}_full", "kind": "full-length-internal-seam",
                        "box": [0, max(0, y - margin), width, min(height, y + margin)]})
    for y in ys:
        for x in xs:
            regions.append({"name": f"intersection_x{x}_y{y}", "kind": "internal-seam-intersection",
                            "box": [x - 256, y - 256, x + 256, y + 256]})
    return regions
