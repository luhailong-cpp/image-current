"""Read existing v1..v5/masks/raws; save QA proof and exact final repair crops only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image

QA = Path(__file__).resolve().parent
ZONE = QA.parents[1]


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def info(p):
    return {"path": p.as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}


def pinned(item):
    p = Path(item["path"])
    actual = info(p)
    assert actual["sha256"] == item["sha256"], str(p)
    return p


def pixels(p, size):
    with Image.open(p) as im:
        assert im.format == "PNG" and im.size == (size, size)
        assert im.mode == "RGB" or (im.mode == "RGBA" and im.getextrema()[3] == (255, 255))
        return np.array(im.convert("RGB"))


final_path = ZONE / "tiles/r03_c03_candidate-v5_4096.png"
final_record_path = final_path.with_suffix(".native-repair.json")
final = pixels(final_path, 4096)
chain = []
record_path = final_record_path
for expected in range(5, 1, -1):
    record = read(record_path)
    assert record["operation"] == "same-coordinate native repair over verified tile"
    assert record["tileId"] == "r03_c03"
    output = pinned(record["output"])
    assert output == ZONE / f"tiles/r03_c03_candidate-v{expected}_4096.png"
    parent = pinned(record["base"]["image"])
    parent_record = pinned(record["base"]["record"])
    assert parent == ZONE / f"tiles/r03_c03_candidate-v{expected-1}_4096.png"
    chain.append((record_path, record, output, parent))
    record_path = parent_record
root_record = read(record_path)
root_path = pinned(root_record["output"])
assert root_record["operation"] == "mechanical 4x4 native-patch assembly"
root_pixels = pixels(root_path, 4096)
replayed = root_pixels.copy()
owned = np.zeros((4096,4096), dtype=np.uint8)
repairs, references = [], {}
for number, (record_path, record, output_path, parent_path) in enumerate(reversed(chain), 1):
    parent = pixels(parent_path, 4096)
    output = pixels(output_path, 4096)
    source = record["repairSource"]
    raw_path = pinned(source)
    generation_path = pinned(source["generationRecord"])
    input_path = pinned(source["input"])
    for k in ("prompt", "receipt", "editTarget", "cropDerivation"):
        pinned(source[k])
    generation = read(generation_path)
    assert generation["sha256"] == info(raw_path)["sha256"]
    assert generation["nativeWidth"] == generation["nativeHeight"] == 1254
    assert generation["resizedAfterGeneration"] is False
    assert generation["finalArtUpscaled"] is False
    for reference in read(input_path)["inputs"]:
        p = Path(reference["path"])
        actual_hash = info(p)["sha256"] if p.is_file() else None
        references[p.as_posix()] = {"path": p.as_posix(), "expectedSha256": reference["sha256"],
                                  "exists": p.is_file(), "actualSha256": actual_hash,
                                  "hashMatches": actual_hash == reference["sha256"] if actual_hash else None}
    raw = pixels(raw_path, 1254)
    mask_path = pinned(record["mask"])
    with Image.open(mask_path) as im:
        assert im.size == (1254,1254) and im.mode == "L"
        mask = np.array(im)
    assert set(np.unique(mask)).issubset({0,255}) and np.any(mask==255)
    selected = mask == 255
    x0,y0,x1,y1 = record["cropBox"]
    target = pixels(Path(source["editTarget"]["path"]), 1254)
    derivation = read(Path(source["cropDerivation"]["path"]))
    ancestor = pinned(derivation["derivedFrom"])
    ancestor_record = pinned(derivation["derivedFrom"]["assemblyRecord"])
    ancestor_pixels = pixels(ancestor,4096)
    assert np.array_equal(target,ancestor_pixels[y0:y1,x0:x1])
    assert np.array_equal(parent[y0:y1,x0:x1][selected],target[selected])
    application_differences = np.any(parent[y0:y1,x0:x1] != target,axis=2)
    prior_overlap = int(np.count_nonzero(owned[y0:y1,x0:x1][selected]))
    assert prior_overlap == 0
    owned[y0:y1,x0:x1][selected] = number
    expected = parent.copy()
    expected[y0:y1,x0:x1][selected] = raw[selected]
    assert np.array_equal(expected,output)
    assert np.array_equal(replayed,parent)
    replayed[y0:y1,x0:x1][selected] = raw[selected]
    assert np.array_equal(final[y0:y1,x0:x1][selected],raw[selected])
    assert np.array_equal(final[y0:y1,x0:x1][selected],output[y0:y1,x0:x1][selected])
    role = {1:"second_cylinder",2:"window_wall",3:"paving",4:"upper_beam"}[number]
    qa_crop = QA / f"independent_{role}_final_crop100pct.png"
    Image.fromarray(final[y0:y1,x0:x1]).save(qa_crop)
    repairs.append({"role":role,"record":info(record_path),"raw":info(raw_path),"mask":info(mask_path),
                    "cropBox":record["cropBox"],"selectedPixels":int(selected.sum()),"overlapWithPreviousRepairMasks":prior_overlap,
                    "parentCropDifferentFromEditTargetPixels":int(application_differences.sum()),
                    "selectedDifferentPixels":int(np.count_nonzero(application_differences & selected)),
                    "entireRecordedAncestorCropMatchesEditTarget":True,
                    "allUnselectedParentPixelsPreservedAtApplication":True,
                    "allSelectedPixelsSurviveInFinalUnchanged":True,
                    "allFinalCropPixelsEqualStageOutput":bool(np.array_equal(final[y0:y1,x0:x1],output[y0:y1,x0:x1])),
                    "finalQaCrop":info(qa_crop)})
assert np.array_equal(replayed,final)
assert np.array_equal(final[owned==0],root_pixels[owned==0])
wall = next(item for item in repairs if item["role"] == "window_wall")
assert wall["allFinalCropPixelsEqualStageOutput"]
out = {"createdAtUtc":datetime.now(timezone.utc).isoformat(),"status":"exact_four_repair_preservation_pass",
       "final":info(final_path),"record":info(final_record_path),"root":info(root_path),
       "rootRecord":info(ZONE / "tiles/r03_c03_candidate-v1_4096.assembly.json"),
       "repairs":repairs,"allRepairMasksDisjoint":True,"allFinalPixelsExactlyReplayedFromV1AndFourRawSelections":True,
       "outsideAllRepairsExactlyV1Pixels":True,"selectedPixelSum":int(np.count_nonzero(owned)),
       "wallV3Complete1254CropUnchangedInV5":True,
       "referenceAvailability":list(references.values()),
       "fullCurrentProvenanceReplay":"blocked: validate-base-only failed on missing shared mail style reference; this focused mechanical replay does not bypass or replace that gate",
       "visualAcceptance":False,"newArtworkGenerated":False,"formalAcceptedCount":0}
(QA / "independent_repair_preservation.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"status":out["status"],"repairPixels":[r["selectedPixels"] for r in repairs],
                  "sum":out["selectedPixelSum"],"missingReferences":[r["path"] for r in references.values() if not r["exists"]]}))
