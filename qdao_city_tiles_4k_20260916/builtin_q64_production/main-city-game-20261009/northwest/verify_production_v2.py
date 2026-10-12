"""Read-only/in-memory smoke checks for production_v2; never writes production state."""
import json
import runpy
from pathlib import Path
from PIL import Image

SCRIPT = Path(__file__).with_name("production_v2.py")
module = runpy.run_path(str(SCRIPT), run_name="verification")
print(json.dumps(module["self_check"]()))
globals_ = module["prepare"].__globals__
saved = {key: globals_[key] for key in ("save_png", "write_json", "sha", "ensure_coordinates")}
saved_image_open = Image.open
captured_images, captured_records = {}, {}

def capture_image(path, image):
    captured_images[str(path)] = image.copy()

def capture_record(path, record, replace=False):
    captured_records[str(path)] = record

def memory_sha(path):
    image = captured_images.get(str(path))
    return "memory-only-not-evidence" if image is not None else saved["sha"](path)

try:
    globals_["save_png"] = capture_image
    globals_["write_json"] = capture_record
    globals_["sha"] = memory_sha
    # Existing source repair: north,left gets exactly N,W,NW, never its own source.
    result = module["prepare"]("r05_c04", "s02_02", "verification_only", "north,left")
    assert {(r["tile"], r["patch"]) for r in result["references"]} == {
        ("r05_c04", "s01_01"), ("r05_c04", "s01_02"), ("r05_c04", "s02_01")}
    assert not any(r["patch"] == "s02_02" and r["tile"] == "r05_c04" for r in result["references"])
    assert all(r["sourceResampled"] is False for r in result["references"])
    # Hypothetical adjacent tile: use a synthetic layout guide only in memory.
    target_dir = module["ZONE"] / "r05_c05"
    hypothetical_layout = target_dir / "layout-only" / "s01_01.layout-only.png"
    def coordinates_override(tile, create=False):
        if tile == "r05_c05":
            return target_dir, module["coordinates"](tile)
        return saved["ensure_coordinates"](tile, create)
    def open_override(path, *args, **kwargs):
        if str(path) == str(hypothetical_layout):
            return Image.new("RGB", (1254, 1254), (1, 2, 3))
        return saved_image_open(path, *args, **kwargs)
    def sha_override(path):
        if str(path) == str(hypothetical_layout):
            return "synthetic-layout-only"
        return memory_sha(path)
    globals_["ensure_coordinates"] = coordinates_override
    globals_["sha"] = sha_override
    Image.open = open_override
    result2 = module["prepare"]("r05_c05", "s01_01", "verification_only", "west")
    assert len(result2["references"]) == 1
    anchor = result2["references"][0]
    assert (anchor["tile"], anchor["patch"]) == ("r05_c04", "s01_04")
    assert anchor["sourceBox"] == [1024, 0, 1254, 1254]
    assert anchor["targetBox"] == [0, 0, 230, 1254]
    output = captured_images[result2["guide"]]
    with saved_image_open(anchor["file"]) as source:
        assert output.crop((0, 0, 230, 1254)).tobytes() == source.convert("RGB").crop((1024, 0, 1254, 1254)).tobytes()
    assert output.getpixel((230, 0)) == (1, 2, 3)
finally:
    Image.open = saved_image_open
    globals_.update(saved)

progress = module["aggregate_progress"]()
assert progress["expectedNativeCoreCount"] == 1024
assert progress["missingNativePatchCount"] == 1024 - progress["selectedUsableNativeCount"]
assert progress["formalAcceptedCount"] <= progress["internalQAPassedCount"] <= progress["currentComplete4kCandidateCount"]
assert progress["candidateCountMeansPixelCoverageNotAcceptance"] is True
assert progress["clientMappingValidated"] is False and progress["capacity5000Validated"] is False
print(json.dumps({
    "status": "passed", "productionWrites": 0, "imageFilesWritten": 0,
    "checks": ["existing repair excludes itself", "north/left filtering includes corner",
               "cross-tile native overlap exact source pixels", "missing layout remains only a guide",
               "read-only 64-tile progress and independent QA stages"],
    "snapshot": {k: progress[k] for k in (
        "generatedNativeCount", "selectedAvailableNativeCount", "selectedUsableNativeCount",
        "missingNativePatchCount", "complete4kCandidateCount", "currentComplete4kCandidateCount",
        "internalQAPassedCount", "formalAcceptedCount")}
}, ensure_ascii=False))

