import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
from PIL import Image

root = Path(r"E:\work\image\tianyong_festival_hd_20260910").resolve()
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("hd_city_mechanics", root / "build_hd_city.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
checks = {}
fixture = Path(tempfile.mkdtemp(prefix="_mechanical_qc_", dir=root)).resolve()
assert fixture.parent == root and fixture.name.startswith("_mechanical_qc_")
try:
    module.ROOT = fixture
    module.GRID = 2
    module.MASTER = module.GRID * module.CORE
    module.prepare()
    native = module.open_rgb(module.SOURCE)
    for _, _, name in module.entries():
        native.save(fixture / "refined" / name, format="PNG")
        (fixture / "prompts" / (Path(name).stem + ".txt")).write_text(
            "Mechanical pipeline fixture: reuse original native artwork for format and stitching validation; no new generation.", encoding="utf-8")
    module.assemble()
    module.verify()
    result = json.loads((fixture / "verification.json").read_text())
    checks["native1254_to_2x2_master2048_assembly"] = result["tileReassemblyPixelsEqualMaster"]
    checks["native_qa_crops_exact"] = result["nativeScaleQaCropsMatchMaster"]
    checks["preview_exact"] = result["previewPixelsMatchDownsample"]
    first_name = next(module.entries())[2]
    first_prompt = fixture / "prompts" / (Path(first_name).stem + ".txt")
    first_prompt.write_text(" \n", encoding="utf-8")
    try:
        module.inspect_refinements()
        raise AssertionError("Empty prompt was accepted")
    except ValueError as error:
        checks["empty_prompt_rejected"] = "nonempty" in str(error)
    first_prompt.write_text("Mechanical test fixture.", encoding="utf-8")
    native.resize((1024, 1024)).save(fixture / "refined" / first_name)
    try:
        module.inspect_refinements()
        raise AssertionError("Undersized native artwork was accepted")
    except ValueError as error:
        checks["undersized_native_rejected"] = "enlargement is forbidden" in str(error)
    shutil.copyfile(fixture / "guides" / first_name, fixture / "refined" / first_name)
    try:
        module.inspect_refinements()
        raise AssertionError("Unrefined layout guide was accepted")
    except ValueError as error:
        checks["guide_as_final_art_rejected"] = "not new artwork" in str(error)
    if not all(checks.values()):
        raise AssertionError(checks)
    output = {"scope": "mechanical pipeline fixture only; not a review of generated city art", "checks": checks,
              "allPassed": True, "productionRuntimeChanged": False}
    (root / "qa" / "pipeline-mechanics-check.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False))
finally:
    # Verify the final absolute recursive-deletion target is the newly created task-local fixture.
    resolved_fixture = fixture.resolve()
    if resolved_fixture.parent != root or not resolved_fixture.name.startswith("_mechanical_qc_"):
        raise RuntimeError("Refusing cleanup outside the verified temporary fixture")
    shutil.rmtree(resolved_fixture)
