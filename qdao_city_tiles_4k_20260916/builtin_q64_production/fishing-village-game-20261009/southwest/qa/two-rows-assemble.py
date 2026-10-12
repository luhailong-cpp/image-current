"""Mechanical 2x4 native candidate and seam QA. No resizing, feathering or drawing."""
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
STEMS = [
    ["r09_c04_p01_01_v1", "r09_c04_p01_02_v7", "r09_c04_p01_03_v2", "r09_c04_p01_04_v2"],
    ["r09_c04_p02_01_v2", "r09_c04_p02_02_v2", "r09_c04_p02_03_v1", "r09_c04_p02_04_v1"],
]
N, C, H, O = 1254, 1024, 115, 230


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    assert path.parent == QA and path.name.startswith("two-rows")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def save_png(path, pixels):
    assert path.parent == QA and path.name.startswith("two-rows")
    Image.fromarray(pixels).save(path)
    with Image.open(path) as check:
        assert np.array_equal(np.asarray(check), pixels)


def main():
    spec = importlib.util.spec_from_file_location("two_rows_minimum_seam", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sources, rows, seams = [], [], []
    for r, stems in enumerate(STEMS):
        arrays = []
        for c, stem in enumerate(stems):
            path = ROOT / "native" / (stem + ".png")
            rp = Path(str(path) + ".generation.json")
            rec = json.loads(rp.read_text(encoding="utf-8-sig"))
            assert sha(path) == rec["sha256"]
            expected = [12173+c*C, 32653+r*C, 13427+c*C, 33907+r*C]
            assert rec["coordinates"]["globalContextBox"] == expected
            with Image.open(path) as im:
                im.load()
                assert im.size == (N, N)
                if im.mode == "RGBA":
                    assert im.getextrema()[3] == (255, 255)
                arrays.append(np.asarray(im.convert("RGB")).copy())
            sources.append({"stem": stem, "path": path.as_posix(), "sha256": sha(path),
                            "record": rp.as_posix(), "recordSha256": sha(rp),
                            "nativeSize": [N, N], "globalContextBox": expected,
                            "destinationBox": [c*C, r*C, c*C+N, r*C+N]})
        row = arrays[0]
        for c, right in enumerate(arrays[1:], 1):
            seam = module._minimum_vertical_seam(row[:, -O:], right[:, :O])
            overlap = np.where((np.arange(O)[None, :] >= seam[:, None])[:, :, None],
                               right[:, :O], row[:, -O:])
            row = np.concatenate([row[:, :-O], overlap, right[:, O:]], axis=1)
            seams.append({"id": f"row{r+1}-c{c}-c{c+1}", "axis": "vertical",
                          "sourceRow": r+1, "overlapBox": [c*C, r*C, c*C+O, r*C+N],
                          "seamXByNativeRowInOverlap": seam.tolist(),
                          "seamXByNativeRowInComposite": (seam+c*C).tolist(),
                          "rightSourceChosenAtOrRightOfSeam": True})
        assert row.shape == (N, 4326, 3)
        rows.append(row)
    # Transpose only for minimum-seam calculation; no interpolation is performed.
    top_overlap = np.transpose(rows[0][-O:], (1, 0, 2))
    bottom_overlap = np.transpose(rows[1][:O], (1, 0, 2))
    seam = module._minimum_vertical_seam(top_overlap, bottom_overlap)
    overlap = np.where((np.arange(O)[:, None] >= seam[None, :])[:, :, None],
                       rows[1][:O], rows[0][-O:])
    pixels = np.concatenate([rows[0][:-O], overlap, rows[1][O:]], axis=0)
    assert pixels.shape == (2278, 4326, 3)
    seams.append({"id": "row1-row2", "axis": "horizontal", "overlapBox": [0, C, 4326, C+O],
                  "seamYByColumnInOverlap": seam.tolist(),
                  "seamYByColumnInComposite": (seam+C).tolist(),
                  "bottomRowChosenAtOrBelowSeam": True})
    output = QA / "two-rows-native-candidate.png"
    save_png(output, pixels)
    manifest = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(),
                "status": "partial_native_candidate_pending_visual_review", "formalAcceptedCount": 0,
                "scope": "2x4 native patches with contexts, not a complete 4096 square tile",
                "compositionOrder": "Three vertical joins per row, then one horizontal row join",
                "operation": "230px minimum-error seam; hard choice of original source pixels only",
                "noResize": True, "noFeather": True, "noDrawing": True, "noColourCorrection": True,
                "sources": sources, "seams": seams,
                "script": {"path": Path(__file__).as_posix(), "sha256": sha(__file__)},
                "helper": {"path": HELPER.as_posix(), "sha256": sha(HELPER)},
                "output": {"path": output.as_posix(), "sha256": sha(output), "size": [4326, 2278],
                           "globalContextBox": [12173, 32653, 16499, 34931],
                           "corePartialBox": [115, 115, 4211, 2163]}, "qa": []}
    boxes = []
    for c in range(1, 4):
        center = c*C+H
        boxes.append((f"two-rows-second-row-seam-{c:02d}-{c+1:02d}-100pct.png",
                      [center-345, C, center+345, C+N], "Second-row vertical seam, full 1254 native rows"))
    for i, x in enumerate([0, 850, 1700, 2550, 3376], 1):
        boxes.append((f"two-rows-horizontal-seam-part-{i:02d}-100pct.png",
                      [x, 794, x+950, 1484], "Horizontal row seam, 690 native rows around seam"))
    for name, box, role in boxes:
        path = QA / name
        save_png(path, pixels[box[1]:box[3], box[0]:box[2]])
        record = {"file": path.as_posix(), "sha256": sha(path), "role": role,
                  "size": [box[2]-box[0], box[3]-box[1]], "sourceBox": box,
                  "source": {"path": output.as_posix(), "sha256": sha(output)},
                  "operation": "Integer crop; no interpolation or drawing",
                  "noResize": True, "noFeather": True,
                  "seamPathsRecord": (QA / "two-rows-assembly.json").as_posix()}
        write_json(Path(str(path)+".derivation.json"), record)
        manifest["qa"].append(record)
    for source in sources:
        assert sha(source["path"]) == source["sha256"]
    manifest["mechanicalValidation"] = {"passed": True, "nativeSourceCount": 8,
        "outputSize": [4326, 2278], "verticalSeamCount": 6, "verticalPathLength": 1254,
        "horizontalSeamCount": 1, "horizontalPathLength": 4326, "qaFiles": 8,
        "sourceHashesUnchanged": True, "savedPixelsVerified": True, "final4kProduced": False}
    write_json(QA / "two-rows-assembly.json", manifest)
    write_json(QA / "two-rows-native-candidate.png.derivation.json", {
        "file": output.as_posix(), "sha256": sha(output), "size": [4326, 2278],
        "operation": manifest["operation"], "compositionOrder": manifest["compositionOrder"],
        "sources": sources, "seamPathsRecord": (QA / "two-rows-assembly.json").as_posix(),
        "noResize": True, "noFeather": True, "noDrawing": True, "notFinal4k": True})
    print(json.dumps({"output": output.as_posix(), "size": [4326, 2278], "qaFiles": 8,
                      "manifest": (QA / "two-rows-assembly.json").as_posix()}))


if __name__ == "__main__":
    main()
