"""Shared manifest/PNG readers. No image mutation; no external dependencies."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct

try:
    from PIL import Image
except ImportError:
    Image = None

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "run": {d: 16 for d in ("N", "NE", "E", "SE", "S", "SW", "W", "NW")},
    "hit": {"E": 6, "W": 6},
    "attack": {"E": 12, "W": 12},
    "cast": {"E": 16, "W": 16},
}
DURATIONS = {"run": 75, "hit": 40, "attack": 30, "cast": 45}


def local_path(value: str) -> Path:
    """All deliverable references must resolve inside this character directory."""
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"引用越过本角色目录: {value}")
    return path


def load_manifest(path: Path | None = None) -> dict:
    return json.loads((path or ROOT / "manifest.json").read_text(encoding="utf-8-sig"))


def frames_of(manifest: dict) -> list[dict]:
    frames = manifest.get("frames", [])
    if isinstance(frames, list):
        return [f for f in frames if isinstance(f, dict)]
    # Also accept frames[action][direction] = [{...}, ...].
    output = []
    for action, directions in frames.items():
        for direction, group in directions.items():
            for frame in group:
                if isinstance(frame, dict):
                    output.append({"action": action, "direction": direction, **frame})
    return output


def png_info(path: Path) -> dict:
    with path.open("rb") as stream:
        header = stream.read(33)
    if len(header) < 33 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"不是有效 PNG: {path.name}")
    width, height, depth, color = struct.unpack(">IIBB", header[16:26])
    info = {"width": width, "height": height, "bitDepth": depth, "colorType": color,
            "mode": "RGBA" if color == 6 else f"PNG colorType {color}", "decoded": False}
    if Image is not None:
        with Image.open(path) as image:
            image.load()
            info["decoded"] = True
            if "A" in image.getbands():
                info["alphaExtrema"] = list(image.getchannel("A").getextrema())
    return info


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
