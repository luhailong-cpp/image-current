"""Focused actual-data checks; only a QA JSON is written, never art or masks."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy
import sys
from unittest.mock import patch

import numpy as np

ZONE = Path(__file__).resolve().parents[1]
MODULE = runpy.run_path(str(ZONE / "apply_native_tile_repair.py"), run_name="mask_aware_validation")
GLOBALS = MODULE["validate_base"].__globals__
BASE = ZONE / "tiles/r03_c03_candidate-v4_4096.png"
BASE_RECORD = BASE.with_suffix(".native-repair.json")
RAW = ZONE / "native/r03_c03_repair_upper_beam_a02.png"
GENERATION = Path(str(RAW) + ".generation.json")
INPUT = ZONE / "guides/r03_c03_repair_upper_beam_a02.input.json"
MASK = ZONE / "qa/repair_upper_beam_a02_mask-v3/source_selection_mask.png"
BOX = [550, 0, 1804, 1254]
checks = []


def reject(name, action, required_reason):
    try:
        action()
    except ValueError as error:
        assert required_reason in str(error), (name, str(error))
        checks.append({"name": name, "result": "rejected_as_required", "reason": str(error)})
        return
    raise AssertionError(f"Unexpected acceptance: {name}")


base, proof = MODULE["validate_base"](BASE, BASE_RECORD)
assert proof["priorRepairCount"] == 3 and proof["verifiedPixelCount"] == 4096 * 4096
checks.append({"name": "actual_v4_complete_native_chain", "result": "pass", "proof": proof})
info = MODULE["file_info"]
base_info, record_info = info(BASE), info(BASE_RECORD)
mask = MODULE["read_mask"](MASK)
repair, source = MODULE["validate_repair_source"](base, base_info, record_info, "r03_c03", BOX, RAW, GENERATION, INPUT, mask)
comparison = source["applicationCropComparison"]
assert source["cropExactlyMatchesRecordedSource"] is True
assert source["cropExactlyMatchesSourceAndApplicationBase"] is False
assert comparison["differentPixelCount"] == comparison["differentUnselectedPixelCount"] == 117925
assert comparison["differentSelectedPixelCount"] == 0 and comparison["selectedPixelCount"] == 158903
assert len(source["verifiedBaseRecordChainToCropSource"]) == 4
checks.append({"name": "actual_v4_plus_ancestor_beam_mask_allowed", "result": "pass", "comparison": comparison,
               "cropSourceBase": source["cropSourceBase"], "applicationBase": source["applicationBase"]})

target_path = Path(source["editTarget"]["path"])
target = MODULE["read_pixels"](target_path, 1254)
crop = base[BOX[1]:BOX[3], BOX[0]:BOX[2]]
different = np.any(target != crop, axis=2)
selected = mask == 255
composed = MODULE["compose_pixels"](base, repair, BOX, mask)
result_crop = composed[BOX[1]:BOX[3], BOX[0]:BOX[2]]
assert np.array_equal(result_crop[~selected], crop[~selected])
assert np.array_equal(result_crop[different], crop[different])
assert np.array_equal(result_crop[selected], repair[selected])
outside = np.ones((4096, 4096), dtype=bool)
outside[BOX[1]:BOX[3], BOX[0]:BOX[2]] = False
assert np.array_equal(composed[outside], base[outside])
checks.append({"name": "all_current_base_changes_outside_mask_preserved", "result": "pass",
               "preservedActualLaterChangedPixels": int(different.sum()),
               "allUnselectedPixelsExactlyCurrentBase": True, "allSelectedPixelsExactlyRawRepair": True,
               "allPixelsOutsideCropExactlyCurrentBase": True, "composedArtWritten": False})


def validate_target(candidate_mask):
    return MODULE["validate_edit_target"](base, base_info, record_info, "r03_c03", BOX, INPUT, candidate_mask)


# Select exactly one real changed pixel from the verified v4, with no forged art.
dy, dx = np.argwhere(different)[0].tolist()
one_conflict = np.zeros_like(mask)
one_conflict[dy, dx] = 255
reject("one_selected_actual_later_changed_pixel_rejected", lambda: validate_target(one_conflict), "(1 pixel(s))")
checks[-1]["cropLocalCoordinate"] = [dx, dy]
checks[-1]["tileCoordinate"] = [dx + BOX[0], dy + BOX[1]]

reject("no_mask_still_requires_entire_current_crop", lambda: validate_target(None), "exact base crop")
reject("all_255_mask_cannot_overlap_later_changes", lambda: validate_target(np.full_like(mask, 255)), "117925 pixel(s)")

# This CLI branch must remain strict even when an application-mask argument exists.
argv = [str(ZONE / "apply_native_tile_repair.py"), "--base", str(BASE), "--base-record", str(BASE_RECORD),
        "--input", str(INPUT), "--crop-box", *map(str, BOX), "--mask", str(MASK), "--validate-crop-only"]
with patch.object(sys, "argv", argv):
    reject("actual_crop_only_cli_ignores_mask_for_strict_preflight", MODULE["main"], "exact base crop")

# Matching ancestor image/hash cannot excuse a record identity absent from the chain.
ancestor = source["cropSourceBase"]
unrelated_record = {**ancestor["record"], "path": str(ZONE / "qa/UNRELATED_RECORD_IDENTITY_ONLY.json")}
reject("identical_ancestor_image_with_nonancestor_record_rejected",
       lambda: MODULE["verified_ancestor_chain"](base_info, record_info, ancestor["image"], unrelated_record),
       "not in the current base's recorded ancestry")

# Fault injection at the decoded target layer proves the whole ancestor crop is checked,
# including pixels that the application mask would not select. Disk bytes are untouched.
original_read_pixels = GLOBALS["read_pixels"]
uy, ux = np.argwhere(~selected)[0].tolist()


def altered_target(path, size):
    array = original_read_pixels(path, size)
    if path == target_path:
        array[uy, ux, 0] ^= np.uint8(1)
    return array


with patch.dict(GLOBALS, {"read_pixels": altered_target}):
    reject("unselected_target_tamper_still_fails_full_ancestor_proof", lambda: validate_target(mask), "recorded ancestor crop")

# Replay a hypothetical later repair entirely in memory through validate_base. This
# exercises recursive mask propagation; no output image or provenance record exists.
fake_image = ZONE / "qa/IN_MEMORY_ONLY_mask_aware_replay.png"
fake_record_path = ZONE / "qa/IN_MEMORY_ONLY_mask_aware_replay.native-repair.json"
assert not fake_image.exists() and not fake_record_path.exists()
fake_info = {"path": str(fake_image), "sha256": hashlib.sha256(composed.tobytes()).hexdigest()}
fake_record = {
    "schemaVersion": 1, "operation": MODULE["REPAIR_OPERATION"], "isAiGeneration": False,
    "tileId": "r03_c03", "base": {"image": base_info, "record": record_info},
    "repairSource": source, "cropBox": BOX, "mask": info(MASK),
    "output": {**fake_info, "dimensions": [4096, 4096]},
    "method": {key: False for key in ("registration", "resizing", "feathering", "colorCorrection", "pixelSynthesis")},
    "coverageAssertions": {"fullNativeCoverage": True},
}
original_read_json = GLOBALS["read_json"]
original_file_info = GLOBALS["file_info"]


def in_memory_json(path):
    return fake_record if path == fake_record_path else original_read_json(path)


def in_memory_info(path):
    return fake_info if path == fake_image else original_file_info(path)


def in_memory_pixels(path, size):
    return composed.copy() if path == fake_image else original_read_pixels(path, size)


with patch.dict(GLOBALS, {"read_json": in_memory_json, "file_info": in_memory_info, "read_pixels": in_memory_pixels}):
    replay, replay_proof = MODULE["validate_base"](fake_image, fake_record_path)
assert np.array_equal(replay, composed) and replay_proof["priorRepairCount"] == 4
checks.append({"name": "recursive_mask_aware_ancestor_replay", "result": "pass",
               "priorRepairCount": replay_proof["priorRepairCount"], "inMemoryFaultFixtureOnly": True,
               "artOrProvenanceWritten": False})

evidence_paths = [INPUT, GENERATION, Path(source["cropDerivation"]["path"]), RAW, target_path, MASK, BASE, BASE_RECORD]
assert info(BASE) == base_info and info(BASE_RECORD) == record_info
for evidence in (source["input"], source["generationRecord"], source["cropDerivation"], source["editTarget"]):
    assert info(Path(evidence["path"])) == evidence
checks.append({"name": "generation_input_derivation_and_base_evidence_unchanged", "result": "pass"})

record = {"createdAtUtc": datetime.now(timezone.utc).isoformat(), "status": "all_checks_passed",
          "tool": info(ZONE / "apply_native_tile_repair.py"), "validationScript": info(Path(__file__).resolve()),
          "evidence": [info(path) for path in evidence_paths], "checkCount": len(checks), "checks": checks,
          "artOrMaskWritten": False, "visualAcceptance": False,
          "limits": "The final replay uses explicit in-memory test identities; all parent images, generation evidence and masks are real. This is provenance/pixel validation, not visual acceptance."}
output = ZONE / "qa/native_tile_repair_mask_aware_validation.json"
with output.open("x", encoding="utf-8") as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write("\n")
print(json.dumps({"status": record["status"], "checkCount": len(checks), "record": str(output)}, ensure_ascii=False))
