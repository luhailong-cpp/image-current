"""Export the six reviewed v5 screens; never invokes an image API.

Run: python qdao_ui_redesign_v5/export_ui.py
Verify existing exports: python qdao_ui_redesign_v5/export_ui.py --check
Requires Pillow. Sources remain unchanged. Refuse materially different aspect ratios.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageOps
from build_transition import export_transition, check_transition, guard_superseded_full_export

ROOT = Path(__file__).resolve().parent
TARGET = (2560, 1080)
SCREENS = (
    ("01_login", "login", "image_gen", "source/01_login.prompt.txt"),
    ("02_server_select", "server_selection", "v10_painted_components_native_label_composition", "../qdao_ui_style_recut_v10/tools/build_composites.mjs"),
    ("03_character_select", "character_selection", "image_gen", "source/03_character_select.prompt.txt"),
    ("04_main_city_hud", "main_city_hud", "v10_painted_components_native_label_composition", "../qdao_ui_style_recut_v10/tools/build_composites.mjs"),
    ("05_battle_scene", "battle_background", "image_gen", "source/05_battle_scene.prompt.txt"),
    ("06_battle_entry_loading", "battle_entry_loading", "image_gen", "source/06_battle_entry_loading.prompt.txt"),
)

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect(path: Path) -> dict:
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        return {"path": path.relative_to(ROOT).as_posix(), "size": list(im.size),
                "mode": im.mode, "bytes": path.stat().st_size, "sha256": digest(path)}

def export() -> dict:
    guard_superseded_full_export()
    records = []
    for stem, role, method, recipe in SCREENS:
        src = ROOT / "source" / f"{stem}.png"
        dst = ROOT / f"{stem}_2560x1080.png"
        before = inspect(src)
        if not (ROOT / recipe).is_file():
            raise FileNotFoundError(recipe)
        with Image.open(src) as original:
            ratio_error = abs((original.width / original.height) / (TARGET[0] / TARGET[1]) - 1)
            if ratio_error > 0.01:
                raise ValueError(f"{src.name}: aspect difference exceeds 1%; recompose with image generation before exporting")
            crop_width = min(original.width, original.height * TARGET[0] / TARGET[1])
            crop_height = min(original.height, original.width * TARGET[1] / TARGET[0])
            left, top = (original.width - crop_width) / 2, (original.height - crop_height) / 2
            crop_box = [round(v, 6) for v in (left, top, left + crop_width, top + crop_height)]
            if original.size == TARGET:
                shutil.copyfile(src, dst)
                resampling = "none; byte-for-byte copy"
            else:
                ImageOps.fit(original.convert("RGB"), TARGET, method=Image.Resampling.LANCZOS,
                             centering=(0.5, 0.5)).save(dst, optimize=True)
                resampling = "proportional centered cover, Pillow LANCZOS"
        if digest(src) != before["sha256"]:
            raise RuntimeError(f"Source modified: {src}")
        records.append({"id": stem, "role": role, "creation_method": method, "recipe": recipe,
                        "source": before, "export": inspect(dst), "resampling": resampling,
                        "source_crop_box_xyxy": crop_box, "relative_aspect_error": round(ratio_error, 8),
                        "native_2560x1080_generation": False})
    export_transition()
    result = {"schema_version": 1, "game_title": "五行奇谈", "date": "2026-09-06",
              "target_size": list(TARGET), "status": "visual_assets_only_not_engine_integrated",
              "screens": records,
              "components_manifest": "components/manifest.json", "hud_placement": "hud/placement.json",
              "copy_source": "copy.zh-CN.json", "transition_manifest": "transition_manifest.json", "remaining_work": "../docs/WUXING_QITAN_HANDOFF.md"}
    (ROOT / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result

def check() -> dict:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    if {s["id"] for s in manifest["screens"]} != {s[0] for s in SCREENS}:
        raise ValueError("Manifest screen coverage mismatch")
    for entry in manifest["screens"]:
        for kind in ("source", "export"):
            expected = entry[kind]
            actual = inspect(ROOT / expected["path"])
            if actual != expected:
                raise ValueError(f"Metadata or hash mismatch: {expected['path']}")
        if tuple(entry["export"]["size"]) != TARGET:
            raise ValueError("Export size mismatch")
        if not (ROOT / entry["recipe"]).is_file():
            raise FileNotFoundError(entry["recipe"])
    check_transition()
    return manifest

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify existing files and hashes without writing")
    args = parser.parse_args()
    result = check() if args.check else export()
    for row in result["screens"]:
        print(f"OK {row['id']}: {row['source']['size']} -> {row['export']['size']}")

if __name__ == "__main__":
    main()
