"""Local copy of existing mechanical seam/color helpers; no art generation."""

import numpy as np

from PIL import Image, ImageStat, ImageFilter



def _channel_stats(image: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    stats = ImageStat.Stat(image)
    return np.asarray(stats.mean[:3], dtype=np.float32), np.asarray(stats.stddev[:3], dtype=np.float32)

def _match_color(source: Image.Image, reference: Image.Image) -> Image.Image:
    source_array = np.asarray(source, dtype=np.float32)
    source_mean, source_std = _channel_stats(source)
    reference_mean, reference_std = _channel_stats(reference)
    source_std = np.maximum(source_std, 1.0)
    scale = np.clip(reference_std / source_std, 0.72, 1.38)
    matched = (source_array - source_mean) * scale + reference_mean
    return Image.fromarray(np.uint8(np.clip(matched, 0, 255)), mode="RGB")

def _minimum_vertical_seam(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return the lowest-error top-to-bottom seam through two equal overlap strips."""
    difference = left.astype(np.float32) - right.astype(np.float32)
    cost = np.mean(difference * difference, axis=2)
    height, width = cost.shape
    center = (width - 1) / 2.0
    normalized = np.abs((np.arange(width, dtype=np.float32) - center) / max(center, 1.0))
    typical = float(np.median(cost)) + 1.0
    cost += (normalized**4)[None, :] * typical * 0.16
    margin = min(24, max(1, width // 12))
    cost[:, :margin] += typical * 8.0
    cost[:, -margin:] += typical * 8.0

    previous = cost[0].copy()
    backtrack = np.zeros((height, width), dtype=np.int8)
    infinity = np.float32(np.finfo(np.float32).max / 16.0)
    for y in range(1, height):
        from_left = np.empty_like(previous)
        from_right = np.empty_like(previous)
        from_left[0] = infinity
        from_left[1:] = previous[:-1]
        from_right[-1] = infinity
        from_right[:-1] = previous[1:]
        candidates = np.stack((from_left, previous, from_right), axis=0)
        choices = np.argmin(candidates, axis=0)
        backtrack[y] = choices.astype(np.int8) - 1
        previous = cost[y] + np.take_along_axis(candidates, choices[None, :], axis=0)[0]

    seam = np.empty(height, dtype=np.int32)
    seam[-1] = int(np.argmin(previous))
    for y in range(height - 1, 0, -1):
        seam[y - 1] = seam[y] + int(backtrack[y, seam[y]])
    return seam

def _append_with_minimum_seam(base: np.ndarray, patch: np.ndarray, overlap: int) -> np.ndarray:
    """Append patch to the right of base using a feathered minimum-error overlap seam."""
    if base.shape[0] != patch.shape[0]:
        raise ValueError("Base and patch heights must match.")
    left_overlap = base[:, -overlap:]
    right_overlap = patch[:, :overlap]
    seam = _minimum_vertical_seam(left_overlap, right_overlap)
    x_coordinates = np.arange(overlap, dtype=np.int32)[None, :]
    binary_mask = np.uint8(x_coordinates >= seam[:, None]) * 255
    feathered = Image.fromarray(binary_mask, mode="L").filter(ImageFilter.GaussianBlur(radius=2.0))
    blend_weight = np.asarray(feathered, dtype=np.float32)[..., None] / 255.0
    blended = (
        left_overlap.astype(np.float32) * (1.0 - blend_weight)
        + right_overlap.astype(np.float32) * blend_weight
    )
    return np.concatenate(
        (
            base[:, :-overlap],
            np.uint8(np.clip(blended, 0, 255)),
            patch[:, overlap:],
        ),
        axis=1,
    )
