"""Compose existing exported pet PNGs into review sheets; draws no character artwork."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = Path("C:/Windows/Fonts/msyh.ttc")


def write_changed(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_bytes() != raw:
        path.write_bytes(raw)


def text_font(size):
    return ImageFont.truetype(str(FONT), size)


def center_text(draw, box, text, size, fill):
    x, y, w, h = box
    font = text_font(size)
    bounds = draw.textbbox((0, 0), text, font=font)
    draw.text((x + (w - bounds[2] + bounds[0]) / 2, y + (h - bounds[3] + bounds[1]) / 2 - bounds[1]), text, font=font, fill=fill)


def load_roster(config, requested=None):
    """Resolve the configured roster or an explicit ordered subset before writing."""
    pets = config["pets"]
    by_slug = {pet["slug"]: pet for pet in pets}
    if not pets or len(by_slug) != len(pets):
        raise ValueError("The configured pet roster must be nonempty with unique slugs")
    expected_count = config.get("expectedPetCount", len(pets))
    if not isinstance(expected_count, int) or expected_count < len(pets):
        raise ValueError("expectedPetCount must be an integer at least as large as the configured roster")
    details = {"rosterSlugs": [pet["slug"] for pet in pets]}
    if requested is None:
        return pets, expected_count, details
    path = Path(requested)
    if not path.is_absolute():
        path = ROOT / path
    raw = path.read_bytes()
    selection = json.loads(raw.decode("utf-8-sig"))
    slugs = selection.get("slugs")
    if not isinstance(slugs, list) or not slugs or not all(isinstance(slug, str) for slug in slugs):
        raise ValueError("Requested roster must contain a nonempty list of slug strings")
    if len(set(slugs)) != len(slugs):
        raise ValueError("Requested roster contains duplicate slugs")
    missing = [slug for slug in slugs if slug not in by_slug]
    if missing:
        raise ValueError("Requested roster contains unknown slugs: " + ", ".join(missing))
    label = selection.get("label", "本次截图对应原创宠物")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("Requested roster label must be a nonempty string")
    try:
        relative_path = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        relative_path = str(path.resolve())
    details = {
        "rosterSlugs": slugs, "rosterLabel": label,
        "requestedRoster": {"file": relative_path, "sha256": hashlib.sha256(raw).hexdigest()},
    }
    return [by_slug[slug] for slug in slugs], len(slugs), details


def roster_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--requested", nargs="?", const="records/requested-roster.json",
        help="Build requested-* sheets from an ordered roster JSON (default: records/requested-roster.json)",
    )
    return parser.parse_args()


def make_sheet(pets, paired, expected_count=None, roster_details=None):
    expected_count = len(pets) if expected_count is None else expected_count
    roster_details = roster_details or {"rosterSlugs": [pet["slug"] for pet in pets]}
    requested = "requestedRoster" in roster_details
    columns = 4 if paired else 7
    cw, ch = (572, 366) if paired else (340, 416)
    gap, pad, top = 16, 32, 112
    rows = math.ceil(len(pets) / columns)
    size = (columns * cw + (columns - 1) * gap + pad * 2, rows * ch + (rows - 1) * gap + top + pad)
    canvas = Image.new("RGBA", size, "#eeeadd")
    draw = ImageDraw.Draw(canvas)
    title = "五行奇谈 · 原创宠物双朝向" if paired else "五行奇谈 · 原创宠物高清设计"
    if requested:
        title = roster_details["rosterLabel"] + (" · 双朝向" if paired else " · 高清设计")
    draw.text((pad, 20), title, font=text_font(35), fill="#214f42")
    available = sum((ROOT / "runtime" / p["slug"] / "idle_E.png").exists() and (not paired or (ROOT / "runtime" / p["slug"] / "idle_W.png").exists()) for p in pets)
    subtitle = f"{available} / {expected_count} 已导出  ·  " + ("E 敌方 / W 我方  ·  两向分别绘制  ·  静态素材" if paired else "敌方朝向 E  ·  原生母图逐只保留  ·  静态素材")
    draw.text((pad, 70), subtitle, font=text_font(20), fill="#6b796c")
    sources = []
    for index, pet in enumerate(pets):
        x = pad + index % columns * (cw + gap)
        y = top + index // columns * (ch + gap)
        background = "#233e3b" if paired else "#fcfaf1"
        draw.rounded_rectangle((x, y, x + cw, y + ch), radius=13, fill=background, outline="#cbbd95", width=2)
        directions = ("E", "W") if paired else ("E",)
        for n, direction in enumerate(directions):
            path = ROOT / "runtime" / pet["slug"] / f"idle_{direction}.png"
            if paired:
                viewport = (x + 10 + n * 282, y + 15, 270, 286)
            else:
                viewport = (x + 10, y + 12, 320, 340)
            vx, vy, vw, vh = viewport
            if path.exists():
                raw = path.read_bytes()
                with Image.open(path) as im:
                    im = im.convert("RGBA")
                    im.thumbnail((vw, vh), Image.Resampling.LANCZOS)
                    canvas.alpha_composite(im, (vx + (vw - im.width) // 2, vy + (vh - im.height) // 2))
                sources.append({"file": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(), "derivedRecord": path.relative_to(ROOT).as_posix() + ".derived.json", "pet": pet["slug"], "direction": direction})
            else:
                center_text(draw, viewport, "待生成", 24, "#a5aaa0")
            if paired:
                center_text(draw, (vx, y + 295, vw, 27), "E · 敌方" if direction == "E" else "W · 我方", 18, "#d4e2d6")
        label_y = y + 325 if paired else y + 360
        center_text(draw, (x + 8, label_y, cw - 16, 42), f"{index + 1:02d}  {pet['name']}", 24, "#f5e8c5" if paired else "#2c5545")
    stem = "EW-roster" if paired else "E-roster"
    prefix = "requested-" if requested else ""
    output = ROOT / "previews" / f"{prefix}{stem}.png"
    buf = io.BytesIO()
    canvas.convert("RGB").save(buf, format="PNG", compress_level=9)
    raw = buf.getvalue()
    write_changed(output, raw)
    record = {
        "schemaVersion": 1, "file": output.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(),
        "width": canvas.width, "height": canvas.height, "format": "PNG", "derivedFrom": sources,
        "operation": "deterministic-contact-sheet-of-existing-exported-pngs-with-labels", "characterArtworkGeneratedByThisScript": False,
        "processor": "build_overviews.py", "processorSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "font": str(FONT), "fontSha256": hashlib.sha256(FONT.read_bytes()).hexdigest(), "availablePetCount": available,
        "expectedPetCount": expected_count, "clientIntegrated": False, "animation": False,
        **roster_details,
    }
    write_changed(Path(str(output) + ".derived.json"), (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return {"file": record["file"], "size": list(size), "availablePetCount": available}


def main():
    args = roster_arguments()
    config = json.loads((ROOT / "asset-config.json").read_text(encoding="utf-8-sig"))
    pets, expected_count, details = load_roster(config, args.requested)
    print(json.dumps([make_sheet(pets, False, expected_count, details), make_sheet(pets, True, expected_count, details)], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
