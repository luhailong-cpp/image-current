"""One-off provenance validation using actual natives; never assembles game art."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy
from unittest.mock import patch

import numpy as np
from PIL import Image

ZONE = Path(__file__).resolve().parents[1]
OUT = ZONE / "qa" / "assembler_composite_validation"
OUT.mkdir(exist_ok=False)
MODULE = runpy.run_path(str(ZONE / "assemble_tile.py"), run_name="composite_validation")
GLOBALS = MODULE["load_cell"].__globals__
COMPOSITE = ZONE / "qa/s03_01_native_composite_a01_base_a04_beam"
ENTRY = {"path": str(COMPOSITE / "candidate.png"), "nativeCompositeRecord": str(COMPOSITE / "native_composite_record.json")}
checks = []


def rejected(name, action):
    try:
        action()
    except (ValueError, OSError, KeyError, TypeError) as error:
        checks.append({"name": name, "result": "rejected_as_required", "reason": str(error)})
        return
    raise AssertionError(f"Unexpected acceptance: {name}")


source, pixels = MODULE["load_cell"](ENTRY, ZONE, "r03_c03", 2, 0)
assert pixels.shape == (1254, 1254, 3)
assert [s["nativeInputPixelCount"] for s in source["nativeComposite"]["sources"]] == [1535171, 37345]
checks.append({"name": "actual_two_raw_source_composite", "result": "pass", "sourceHash": source["sha256"], "originalNativePixelCounts": [1535171, 37345]})

for row, col in [(1, 1), (2, 1), (3, 1), (4, 1), (4, 2), (4, 3), (4, 4)]:
    path = ZONE / "native" / f"r03_c03_s{row:02d}_{col:02d}_a01.png"
    raw, array = MODULE["load_raw_source"](path, Path(str(path) + ".generation.json"), "r03_c03", row - 1, col - 1)
    assert array.shape == (1254, 1254, 3)
    checks.append({"name": f"existing_raw_gate_{path.stem}", "result": "pass", "sha256": raw["sha256"]})

rejected("ambiguous_raw_and_composite_entry", lambda: MODULE["load_cell"]({**ENTRY, "generationRecord": "unused.json"}, ZONE, "r03_c03", 2, 0))
rejected("composite_masquerading_as_raw", lambda: MODULE["load_cell"]({"path": ENTRY["path"], "generationRecord": str(ZONE / "native/r03_c03_s03_01_a01.png.generation.json")}, ZONE, "r03_c03", 2, 0))
rejected("composite_pinned_candidate_hash_mismatch", lambda: MODULE["load_cell"]({**ENTRY, "sha256": "0" * 64}, ZONE, "r03_c03", 2, 0))

original_record = json.loads(Path(ENTRY["nativeCompositeRecord"]).read_text(encoding="utf-8-sig"))
for name, mutate in [
    ("wrong_global_box", lambda data: data["coordinateSystem"]["sameGlobalNativeBox"].__setitem__(0, 8078)),
    ("third_raw_source", lambda data: data["sources"].append(deepcopy(data["sources"][0]))),
    ("nested_composite_leaf", lambda data: data["sources"][0].__setitem__("nativeCompositeRecord", "forbidden.json")),
    ("wrong_generation_record_hash", lambda data: data["sources"][0]["generationRecord"].__setitem__("sha256", "0" * 64)),
]:
    data = deepcopy(original_record)
    mutate(data)
    path = OUT / f"rejection_fixture_{name}.json"
    with path.open("x", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    rejected(name, lambda path=path: MODULE["load_cell"]({**ENTRY, "nativeCompositeRecord": str(path)}, ZONE, "r03_c03", 2, 0))

# Fault injection changes decoded data in memory, never native files or art.
original_read = GLOBALS["read_native_pixels"]
def changed_candidate(path):
    array, metadata = original_read(path)
    if path == Path(ENTRY["path"]):
        array[0, 0, 0] ^= np.uint8(1)
    return array, metadata
with patch.dict(GLOBALS, {"read_native_pixels": changed_candidate}):
    rejected("one_changed_candidate_channel", lambda: MODULE["load_cell"](ENTRY, ZONE, "r03_c03", 2, 0))

mask_path = Path(source["nativeComposite"]["mask"]["path"])
mask = MODULE["read_binary_mask"](mask_path)
bad_mask = mask.copy()
bad_mask[0, 0] = 128
original_open = Image.open
def invalid_mask_image(path, *args, **kwargs):
    if Path(path) == mask_path:
        image = Image.fromarray(bad_mask)
        image.format = "PNG"
        return image
    return original_open(path, *args, **kwargs)
with patch.object(Image, "open", side_effect=invalid_mask_image):
    rejected("nonbinary_mask_channel_128", lambda: MODULE["load_cell"](ENTRY, ZONE, "r03_c03", 2, 0))

raw_path = ZONE / "native/r03_c03_s03_01_a01.png"
gen_path = Path(str(raw_path) + ".generation.json")
original_read_text = Path.read_text
generation = json.loads(original_read_text(gen_path, encoding="utf-8-sig"))
receipt_path = Path(generation["evidence"]["receipt"])
for name, target, data in [
    ("raw_prompt_hash_mismatch", gen_path, {**generation, "promptSha256": "0" * 64}),
    ("raw_receipt_route_mismatch", receipt_path, {"route": "api", "tool": "image_gen.imagegen"}),
]:
    def substituted_text(path, *args, **kwargs):
        return json.dumps(data) if path == target else original_read_text(path, *args, **kwargs)
    with patch.object(Path, "read_text", substituted_text):
        rejected(name, lambda: MODULE["load_raw_source"](raw_path, gen_path, "r03_c03", 2, 0))

# Only integer ownership planes are allocated here; no synthetic image is made.
sources = [{} for _ in range(9)]
sources[8] = source
ids = np.full((3302, 1254), 255, dtype=np.uint8)
ids[2048:3302] = 8
contributions = [{"sourceId": 8, "pixelCount": 1254 ** 2, "outputBoundingBoxHalfOpen": [0, 2048, 1254, 3302], "nativeBoundingBoxHalfOpen": [0, 0, 1254, 1254]}]
MODULE["add_nested_contributions"](contributions, ids, sources, {8: mask}, 0)
leaves = contributions[0]["originalNativeContributions"]
assert [leaf["pixelCount"] for leaf in leaves] == [1535171, 37345]
assert leaves[1]["outputBoundingBoxHalfOpen"] == [1102, 2278, 1254, 2547]
checks.append({"name": "nested_padded_positions_and_counts", "result": "pass", "contributions": leaves})

tile_ids = ids[115:, 115:]
tile_contributions = [{"sourceId": 8, "pixelCount": 1139 * 1254, "outputBoundingBoxHalfOpen": [0, 1933, 1139, 3187], "nativeBoundingBoxHalfOpen": [115, 0, 1254, 1254]}]
MODULE["add_nested_contributions"](tile_contributions, tile_ids, sources, {8: mask}, 115)
tile_leaves = tile_contributions[0]["originalNativeContributions"]
assert tile_leaves[1]["pixelCount"] == 37345
assert tile_leaves[1]["outputBoundingBoxHalfOpen"] == [987, 2163, 1139, 2432]
checks.append({"name": "nested_after_outer_crop_positions", "result": "pass", "contributions": tile_leaves})

ids[:, 1102:] = 255
clipped = [{"sourceId": 8, "pixelCount": 1102 * 1254, "outputBoundingBoxHalfOpen": [0, 2048, 1102, 3302], "nativeBoundingBoxHalfOpen": [0, 0, 1102, 1254]}]
MODULE["add_nested_contributions"](clipped, ids, sources, {8: mask}, 0)
assert clipped[0]["originalNativeContributions"][1]["pixelCount"] == 0
assert clipped[0]["originalNativeContributions"][1]["outputBoundingBoxHalfOpen"] is None
checks.append({"name": "repair_source_entirely_removed_by_later_seam", "result": "pass"})

record = {"createdAtUtc": datetime.now(timezone.utc).isoformat(), "status": "numerical_provenance_validation_passed", "assemblerSha256": hashlib.sha256((ZONE / "assemble_tile.py").read_bytes()).hexdigest(), "checks": checks, "full4KAssemblyRun": False, "newArtFilesWritten": False, "formalAcceptedCount": 0, "limits": ["No 16-cell manifest was selected or run.", "These checks cannot establish visual seam acceptance."]}
with (OUT / "validation.json").open("x", encoding="utf-8") as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
print(json.dumps({"status": record["status"], "checks": len(checks), "record": str(OUT / "validation.json"), "full4KAssemblyRun": False}))
