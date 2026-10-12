"""Mechanical native row assembly and full-height seam QA; no image synthesis."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json

import numpy as np
from PIL import Image

QA = Path(__file__).resolve().parent
ROOT = QA.parent
HELPER = ROOT.parents[3] / "tianyong_festival_hd_20260910" / "seam_helpers.py"
STEMS = ["r09_c04_p01_01_v1", "r09_c04_p01_02_v7", "r09_c04_p01_03_v2", "r09_c04_p01_04_v2"]
CORE, HALO, OVERLAP, NATIVE = 1024, 115, 230, 1254


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    assert path.parent == QA and path.name.startswith("first-row")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_png(path, pixels):
    assert path.parent == QA and path.name.startswith("first-row")
    Image.fromarray(pixels).save(path)
    with Image.open(path) as check:
        assert np.array_equal(np.asarray(check), pixels)


def main():
    spec = importlib.util.spec_from_file_location("first_row_seam_helper", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sources, arrays = [], []
    for index, stem in enumerate(STEMS):
        path = ROOT / "native" / (stem + ".png")
        record_path = Path(str(path) + ".generation.json")
        record = json.loads(record_path.read_text(encoding="utf-8-sig"))
        digest = sha(path)
        assert digest == record["sha256"]
        with Image.open(path) as image:
            image.load()
            assert image.size == (NATIVE, NATIVE)
            assert image.mode in ("RGB", "RGBA")
            if image.mode == "RGBA":
                assert image.getextrema()[3] == (255, 255)
            arrays.append(np.asarray(image.convert("RGB")).copy())
        expected_box = [12173 + index * CORE, 32653, 13427 + index * CORE, 33907]
        assert record["coordinates"]["globalContextBox"] == expected_box
        sources.append({"stem": stem, "path": path.as_posix(), "sha256": digest,
                        "record": record_path.as_posix(), "recordSha256": sha(record_path),
                        "nativeSize": [NATIVE, NATIVE], "globalContextBox": expected_box,
                        "rowDestinationBox": [index * CORE, 0, index * CORE + NATIVE, NATIVE]})
    row = arrays[0].copy()
    seams = []
    for index, right in enumerate(arrays[1:], 1):
        left_overlap, right_overlap = row[:, -OVERLAP:], right[:, :OVERLAP]
        seam = module._minimum_vertical_seam(left_overlap, right_overlap)
        choose_right = np.arange(OVERLAP)[None, :] >= seam[:, None]
        selected = np.where(choose_right[:, :, None], right_overlap, left_overlap)
        row = np.concatenate((row[:, :-OVERLAP], selected, right[:, OVERLAP:]), axis=1)
        seams.append({"id": f"{index:02d}-{index+1:02d}", "leftSource": STEMS[index-1],
                      "rightSource": STEMS[index], "overlapPixels": OVERLAP,
                      "rowOverlapBox": [index * CORE, 0, index * CORE + OVERLAP, NATIVE],
                      "seamXByRowInOverlap": seam.tolist(),
                      "seamXByRowInAssembledImage": (seam + index * CORE).tolist(),
                      "rightSourceChosenAtOrRightOfSeam": True})
    assert row.shape == (NATIVE, 4 * CORE + 2 * HALO, 3)
    output = QA / "first-row-native-candidate.png"
    save_png(output, row)
    manifest = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
                "status": "candidate_pending_visual_review", "formalAcceptedCount": 0,
                "scope": "One native row with outer contexts; not a complete 4096 square tile.",
                "operation": "Sequential 230px minimum-error overlap; hard source-pixel choice only",
                "noResize": True, "noFeather": True, "noDrawing": True, "noColourCorrection": True,
                "noSourceMutation": True, "sources": sources, "seams": seams,
                "script": {"path": Path(__file__).as_posix(), "sha256": sha(__file__)},
                "helper": {"path": HELPER.as_posix(), "sha256": sha(HELPER)},
                "output": {"path": output.as_posix(), "sha256": sha(output), "size": [4326, 1254],
                           "globalContextBox": [12173, 32653, 16499, 33907],
                           "coreRowBox": [115, 115, 4211, 1139]}, "qa": []}
    for index, seam in enumerate(seams, 1):
        center = index * CORE + HALO
        box = [center - 345, 0, center + 345, NATIVE]
        path = QA / f"first-row-seam-{seam['id']}-100pct.png"
        save_png(path, row[:, box[0]:box[2]])
        derived = {"file": path.as_posix(), "sha256": sha(path), "size": [690, NATIVE],
                   "operation": "Integer crop of full-height native assembled seam; no resampling",
                   "source": {"path": output.as_posix(), "sha256": sha(output)},
                   "sourceBox": box, "seamId": seam["id"],
                   "seamXByRowInCrop": [x - box[0] for x in seam["seamXByRowInAssembledImage"]],
                   "noResize": True, "noFeather": True, "noDrawing": True}
        write_json(Path(str(path) + ".derivation.json"), derived)
        manifest["qa"].append({"file": path.as_posix(), "sha256": sha(path), "size": [690, NATIVE],
                               "cropBox": box, "derivation": str(path) + ".derivation.json"})
    for source in sources:
        assert sha(source["path"]) == source["sha256"]
    manifest["mechanicalValidation"] = {"passed": True, "nativeSources": 4, "sourceDimensionsChecked": True,
                                        "savedImagePixelsVerified": True, "completeSeamRows": 1254,
                                        "seamCount": 3, "outputSize": [4326, 1254], "final4kProduced": False}
    write_json(QA / "first-row-assembly.json", manifest)
    print(json.dumps({"output": output.as_posix(), "size": [4326, 1254], "qaSeams": 3,
                      "manifest": (QA / "first-row-assembly.json").as_posix()}))


if __name__ == "__main__":
    main()
