"""Build only the 2560x1080 scene compatibility assets; retain native paintings.

python build_runtime.py --deploy
python build_runtime.py --check

Pillow performs one uniform-scale resample from a floating-point center-cover
source rectangle. This is compatibility upsampling, not new native detail.
Existing Unity .meta files and GUIDs must never be modified by this script.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parent
CLIENT = PACKAGE.parent.parent / "mmorpg-client"
RESOURCES = CLIENT / "Assets/Resources"
SIZE = (2560, 1080)
MAPPINGS = {
    "01_main_city_wide": ["UI/Ugui/Native/scene_background.png"],
    "02_login_landscape": ["UI/Ugui/RefreshV8/login_background.png"],
    "03_sanctuary_courtyard": ["UI/Ugui/RefreshV8/sanctuary_background.png"],
    "04_battle_forest_bridge": [
        "UI/Ugui/RefreshV8/battle_background.png",
        "UI/Ugui/Battle/Backgrounds/qdao_battle_arena_cloud_terrace_2560x1080_v1.png",
    ],
    "05_battle_entry": [
        "UI/Ugui/RefreshV8/battle_loading.png",
        "UI/Ugui/Battle/Backgrounds/qdao_battle_entry_loading_2560x1080_v1.png",
    ],
}
NOTES = {
    "01_main_city_wide": "Center plaza, stairs and central temple retained; only outer scenery is cropped. Static fallback only; this is not the walkable 6144 map.",
    "02_login_landscape": "Clean background: native title, character and buttons are rendered independently by the client. Less than one source pixel cropped on each horizontal edge.",
    "03_sanctuary_courtyard": "Same painting as main_city_wide. Center plaza remains the role-selection standing area; no baked character or UI.",
    "04_battle_forest_bridge": "Both platforms and bridge retained. BattleStage visual feet and all pet shadows are now calibrated to independently traced stone interiors; protocol slots and assignment rules remain unchanged.",
    "05_battle_entry": "Illustration only, with boy and fox. Both characters retained completely; no baked loading or progress UI. Must be used for entrance, never as the live battle background.",
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def cover_box(size):
    width, height = size
    ratio = SIZE[0] / SIZE[1]
    if width / height > ratio:
        keep = height * ratio
        return ((width - keep) / 2, 0.0, (width + keep) / 2, float(height))
    keep = width / ratio
    return (0.0, (height - keep) / 2, float(width), (height + keep) / 2)

def source_entries():
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8-sig"))
    return manifest["outputs"]

def build(deploy):
    records = []
    before = {}
    for entry in source_entries():
        source = PACKAGE / entry["file"]
        assert digest(source) == entry["sha256"], f"Native source changed: {source}"
        target_name = entry["id"] + "_2560x1080.png"
        output = ROOT / target_name
        with Image.open(source) as original:
            box = cover_box(original.size)
            scale_x = SIZE[0] / (box[2] - box[0])
            scale_y = SIZE[1] / (box[3] - box[1])
            assert abs(scale_x - scale_y) < 1e-10, "Nonuniform image scaling is forbidden"
            original.convert("RGB").resize(SIZE, Image.Resampling.LANCZOS, box=box).save(output)
        targets = []
        for rel in MAPPINGS[entry["id"]]:
            target = RESOURCES / rel
            meta = target.with_suffix(target.suffix + ".meta")
            assert target.is_file() and meta.is_file(), f"Existing asset/meta contract required: {target}"
            meta_hash = digest(meta)
            before[str(meta)] = meta_hash
            guid = re.search(r"^guid: (\S+)$", meta.read_text(encoding="utf-8-sig"), re.M).group(1)
            if deploy:
                shutil.copyfile(output, target)
            assert digest(meta) == meta_hash, f"Metadata changed: {meta}"
            targets.append({"resourcePath": rel[:-4], "clientFile": "Assets/Resources/" + rel,
                            "sha256": digest(target), "matchesRuntime": digest(target) == digest(output),
                            "metaSha256": meta_hash, "guid": guid})
        records.append({"id": entry["id"], "source": entry["file"], "sourceSha256": entry["sha256"],
                        "nativeSize": [entry["nativeWidth"], entry["nativeHeight"]],
                        "runtimeFile": target_name, "runtimeSize": list(SIZE), "runtimeSha256": digest(output),
                        "sourceCropBox": list(box), "uniformScale": scale_x,
                        "resampling": "Pillow LANCZOS, single floating-point source-box resample",
                        "nativeDetailIncreased": False, "review": NOTES[entry["id"]], "targets": targets})
    manifest = {"schema": "qdao.festival-scenes.runtime.v1", "clientRoot": str(CLIENT),
                "status": "deployed" if deploy else "staged", "sizeContract": list(SIZE),
                "nativeArtUnchanged": True, "unityMetadataUnchanged": all(digest(Path(p)) == h for p,h in before.items()),
                "engineValidation": "pending; static pixel/path/meta verification only", "outputs": records}
    (ROOT / "runtime-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    make_previews()
    return manifest

def make_previews():
    entries = [(entry["id"], ROOT / (entry["id"] + "_2560x1080.png")) for entry in source_entries()]
    sheet = Image.new("RGB", (1440, 3 * 332), "#eee8d7")
    draw = ImageDraw.Draw(sheet)
    for i, (name, path) in enumerate(entries):
        col, row = i % 2, i // 2
        with Image.open(path) as scene:
            scene.thumbnail((700, 295))
            sheet.paste(scene, (col*720 + (720-scene.width)//2, row*332))
        draw.text((col*720+10, row*332+305), name + " / 2560 x 1080 / equal scale", fill="#27443a")
    sheet.save(ROOT / "runtime-contact.jpg", quality=91)

def check():
    record = json.loads((ROOT / "runtime-manifest.json").read_text(encoding="utf-8"))
    checks = []
    for item in record["outputs"]:
        source = PACKAGE / item["source"]
        checks.append({"check": item["id"] + " native source untouched", "passed": digest(source) == item["sourceSha256"]})
        runtime = ROOT / item["runtimeFile"]
        with Image.open(runtime) as image:
            checks.append({"check": item["id"] + " 2560x1080 opaque RGB", "passed": image.size == SIZE and image.mode == "RGB"})
        checks.append({"check": item["id"] + " staged pixels match manifest", "passed": digest(runtime) == item["runtimeSha256"]})
        for target in item["targets"]:
            asset = CLIENT / target["clientFile"]
            meta = asset.with_suffix(asset.suffix + ".meta")
            checks.append({"check": target["resourcePath"] + " deployed pixels", "passed": digest(asset) == item["runtimeSha256"]})
            checks.append({"check": target["resourcePath"] + " retained meta and GUID", "passed": digest(meta) == target["metaSha256"]})
    checks.append({"check": "shared main city and sanctuary painting remain byte-identical", "passed": digest(ROOT / "01_main_city_wide_2560x1080.png") == digest(ROOT / "03_sanctuary_courtyard_2560x1080.png")})
    result = {"status": "passed" if all(c["passed"] for c in checks) else "failed", "checks": checks,
              "limits": ["Unity import and engine screenshot validation are separate.", "BattleStage visual placement is separately checked by verify_battle_stage.py; Unity screenshots and NUnit execution remain separate."]}
    (ROOT / "runtime-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "passed": sum(c["passed"] for c in checks), "total": len(checks)}))
    assert result["status"] == "passed"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deploy", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        build(args.deploy)
    check()
