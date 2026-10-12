"""Compose existing pet portraits into a deterministic review sheet; draws no pet art."""
from __future__ import annotations

import hashlib
import io
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from build_overviews import ROOT, FONT, center_text, text_font, write_changed, load_roster, roster_arguments


def main():
    args = roster_arguments()
    config = json.loads((ROOT / "asset-config.json").read_text(encoding="utf-8-sig"))
    pets, expected_count, roster_details = load_roster(config, args.requested)
    columns, rows = 7, math.ceil(len(pets) / 7)
    cell_width, cell_height, gap, padding, top = 240, 302, 16, 32, 112
    width = columns * cell_width + (columns - 1) * gap + padding * 2
    height = rows * cell_height + (rows - 1) * gap + top + padding
    canvas = Image.new("RGBA", (width, height), "#eeeadd")
    draw = ImageDraw.Draw(canvas)
    available = sum((ROOT / "ui" / pet["slug"] / "portrait_512.png").exists() for pet in pets)
    title = roster_details["rosterLabel"] + " · 头像取景" if args.requested else "五行奇谈 · 原创宠物头像取景"
    draw.text((padding, 20), title, font=text_font(35), fill="#214f42")
    draw.text((padding, 70), f"{available} / {expected_count} 已导出  ·  512像素透明头像  ·  实际母图人工取景", font=text_font(20), fill="#6b796c")
    sources = []
    for index, pet in enumerate(pets):
        x = padding + index % columns * (cell_width + gap)
        y = top + index // columns * (cell_height + gap)
        draw.rounded_rectangle((x, y, x + cell_width, y + cell_height), radius=13, fill="#fcfaf1", outline="#cbbd95", width=2)
        path = ROOT / "ui" / pet["slug"] / "portrait_512.png"
        viewport = (x + 12, y + 12, 216, 232)
        if path.exists():
            raw = path.read_bytes()
            with Image.open(path) as portrait:
                portrait = portrait.convert("RGBA")
                portrait.thumbnail((216, 216), Image.Resampling.LANCZOS)
                canvas.alpha_composite(portrait, (x + (cell_width - portrait.width) // 2, y + 12 + (232 - portrait.height) // 2))
            sources.append({
                "file": path.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "derivedRecord": path.relative_to(ROOT).as_posix() + ".derived.json",
                "pet": pet["slug"],
            })
        else:
            center_text(draw, viewport, "待生成", 22, "#a5aaa0")
        center_text(draw, (x + 6, y + 250, cell_width - 12, 42), f"{index + 1:02d}  {pet['name']}", 22, "#2c5545")
    prefix = "requested-" if args.requested else ""
    output = ROOT / "previews" / f"{prefix}portrait-roster.png"
    buffer = io.BytesIO()
    canvas.convert("RGB").save(buffer, format="PNG", compress_level=9)
    raw = buffer.getvalue()
    write_changed(output, raw)
    processor = Path(__file__)
    helper = processor.with_name("build_overviews.py")
    record = {
        "schemaVersion": 1,
        "file": output.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "width": width, "height": height, "format": "PNG",
        "derivedFrom": sources,
        "operation": "deterministic-contact-sheet-of-existing-transparent-portrait-pngs-with-labels",
        "columns": columns, "rows": rows,
        "characterArtworkGeneratedByThisScript": False,
        "processor": processor.name,
        "processorSha256": hashlib.sha256(processor.read_bytes()).hexdigest(),
        "layoutHelper": helper.name,
        "layoutHelperSha256": hashlib.sha256(helper.read_bytes()).hexdigest(),
        "font": str(FONT),
        "fontSha256": hashlib.sha256(FONT.read_bytes()).hexdigest(),
        "availablePetCount": available, "expectedPetCount": expected_count,
        **roster_details,
        "clientIntegrated": False, "animation": False,
    }
    write_changed(Path(str(output) + ".derived.json"), (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"file": record["file"], "size": [width, height], "availablePetCount": available}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
