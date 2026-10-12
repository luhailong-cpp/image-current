"""Actual base/crop provenance checks and in-memory fault injection; no art output."""
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
MODULE = runpy.run_path(str(ZONE / "apply_native_tile_repair.py"), run_name="tile_repair_validation")
GLOBALS = MODULE["validate_base"].__globals__
BASE = ZONE / "tiles/r03_c03_candidate-v1_4096.png"
BASE_RECORD = BASE.with_suffix(".assembly.json")
INPUT = ZONE / "guides/r03_c03_repair_second_cylinder_a01.input.json"
BOX = [1670, 2220, 2924, 3474]
checks = []


def reject(name, action):
    try:
        action()
    except (ValueError, OSError, KeyError, TypeError) as error:
        checks.append({"name": name, "result": "rejected_as_required", "reason": str(error)})
        return
    raise AssertionError(f"Unexpected acceptance: {name}")


base, proof = MODULE["validate_base"](BASE, BASE_RECORD)
assert proof["verifiedPixelCount"] == 16777216 and proof["originalRawSourceCount"] == 17
checks.append({"name": "actual_candidate_v1_all_pixels_and_17_raw_sources", "result": "pass", "proof": proof})
base_info, base_record_info = MODULE["file_info"](BASE), MODULE["file_info"](BASE_RECORD)


def validate_crop():
    return MODULE["validate_edit_target"](base, base_info, base_record_info, "r03_c03", BOX, INPUT)


crop = validate_crop()
assert len(crop["references"]) == 4 and crop["globalBox"] == [9862, 10412, 11116, 11666]
checks.append({"name": "actual_cylinder_edit_crop_four_declared_references", "result": "pass", "editCrop": crop})

read_json = GLOBALS["read_json"]
for name, target, change in [
    ("wrong_base_output_hash", BASE_RECORD, lambda value: value["output"].__setitem__("sha256", "0" * 64)),
    ("missing_full_native_coverage", BASE_RECORD, lambda value: value["coverageAssertions"].__setitem__("fullNativeCoverage", False)),
    ("changed_original_generation_record", BASE_RECORD, lambda value: value["sources"][0]["generationRecord"].__setitem__("sha256", "0" * 64)),
    ("wrong_crop_global_coordinates", INPUT, lambda value: value["globalBox"].__setitem__(0, 9863)),
    ("wrong_declared_tile_crop", INPUT, lambda value: value["tileCropBox"].__setitem__(0, 1671)),
    ("wrong_crop_derivation_hash", INPUT, lambda value: value["editTarget"]["derivationRecord"].__setitem__("sha256", "0" * 64)),
]:
    data = deepcopy(read_json(target))
    change(data)
    def substituted(path):
        return data if path == target else read_json(path)
    with patch.dict(GLOBALS, {"read_json": substituted}):
        reject(name, (lambda: MODULE["validate_base"](BASE, BASE_RECORD)) if target == BASE_RECORD else validate_crop)

target_path = Path(crop["editTarget"]["path"])
read_pixels = GLOBALS["read_pixels"]
def altered_crop(path, size):
    array = read_pixels(path, size)
    if path == target_path:
        array[0, 0, 0] ^= np.uint8(1)
    return array
with patch.dict(GLOBALS, {"read_pixels": altered_crop}):
    reject("one_changed_edit_crop_channel", validate_crop)

raw_path = ZONE / "native/r03_c03_s03_04_a05.png"
raw, raw_info, generation = MODULE["load_raw"](raw_path, Path(str(raw_path) + ".generation.json"))
checks.append({"name": "existing_builtin_raw_generation_gate", "result": "pass", "rawHash": raw_info["sha256"]})
reject("unrelated_old_generation_cannot_claim_new_crop", lambda: MODULE["validate_crop_input"](base, base_info, base_record_info, "r03_c03", BOX, INPUT, generation, raw_path.parent))
reject("crop_outside_tile", lambda: MODULE["validate_box"]([3000, 2220, 4254, 3474]))
reject("non_native_crop_size", lambda: MODULE["validate_box"]([1670, 2220, 2923, 3474]))

# Reuse an existing explicit mask for a numerical primitive check only.
# The old raw image is NOT an authorized source for this crop and cannot pass
# validate_repair_source; no composed image or newly chosen mask is saved.
mask_path = ZONE / "qa/s03_01_native_composite_a01_base_a04_beam/source_selection_mask.png"
mask = MODULE["read_mask"](mask_path)
composed = MODULE["compose_pixels"](base, raw, BOX, mask)
selection = MODULE["selection_record"](mask, BOX, [8192, 8192])
assert selection["repairPixelCount"] == 37345
assert selection["tileBoundingBoxHalfOpen"] == [2772, 2450, 2924, 2719]
assert np.array_equal(composed[2450:2719, 2772:2924][mask[230:499, 1102:1254] == 255], raw[230:499, 1102:1254][mask[230:499, 1102:1254] == 255])
checks.append({"name": "same_coordinate_binary_selection_primitive_only", "result": "pass", "selectedPixels": 37345, "artWritten": False, "notAValidRepairInputCombination": True})
del composed

bad_mask = mask.copy()
bad_mask[0, 0] = 128
original_open = Image.open
def bad_mask_open(path, *args, **kwargs):
    if Path(path) == mask_path:
        image = Image.fromarray(bad_mask)
        image.format = "PNG"
        return image
    return original_open(path, *args, **kwargs)
with patch.object(Image, "open", side_effect=bad_mask_open):
    reject("mask_nonbinary_128", lambda: MODULE["read_mask"](mask_path))
reject("missing_explicit_mask", lambda: MODULE["read_mask"](ZONE / "qa/no-such-explicit-mask.png"))

result = {"createdAtUtc": datetime.now(timezone.utc).isoformat(), "status": "base_and_crop_provenance_validation_passed", "tool": MODULE["file_info"](ZONE / "apply_native_tile_repair.py"), "checks": checks, "artFilesWritten": False, "masksGenerated": False, "formalAcceptedCount": 0, "limits": ["The parent is generating the actual whole-object repair and will choose its explicit mask.", "No valid complete repair input set was available for an output/recursive-replay end-to-end run at this validation time.", "The in-memory primitive check does not validate the old raw image as a repair of the new crop.", "No visual acceptance follows from these numerical checks."]}
out = ZONE / "qa/native_tile_repair_validation.json"
with out.open("x", encoding="utf-8") as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
print(json.dumps({"status": result["status"], "checks": len(checks), "record": str(out), "artFilesWritten": False}))
