"""Read native sources; write only QA products for row two's middle patches."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
QA = Path(__file__).resolve().parent
ZONE = QA.parent
sys.path.insert(0, str(ZONE))
from join_vertical import minimum_error_path

SIZE, STRIDE, HALO_OVERLAP = 1254, 1024, 230
PAIRS = [
    ("H", "r03_c03_s02_01_a04", "r03_c03_s02_02_a02"),
    ("H", "r03_c03_s02_02_a02", "r03_c03_s02_03_a01"),
    ("V", "r03_c03_s01_02_a03", "r03_c03_s02_02_a02"),
    ("V", "r03_c03_s01_03_a03", "r03_c03_s02_03_a01"),
    ("H", "r03_c03_s02_03_a01", "r03_c03_s02_04_a02"),
    ("V", "r03_c03_s01_04_a03", "r03_c03_s02_04_a02"),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(stem):
    path = ZONE / "native" / (stem + ".png")
    im = Image.open(path)
    assert im.size == (SIZE, SIZE) and im.mode in ("RGB", "RGBA")
    if im.mode == "RGBA":
        assert im.getextrema()[3] == (255, 255)
    return np.asarray(im.convert("RGB")).copy(), {"stem": stem, "path": str(path), "sha256": sha(path), "dimensions": list(im.size)}


def save(name, array, box=None):
    im = Image.fromarray(array)
    if box:
        im = im.crop(box)
    path = QA / name
    im.save(path)
    return {"path": str(path), "sha256": sha(path), "dimensions": list(im.size), "cropBoxHalfOpen": box}


def main():
    records = []
    for axis, a, b in PAIRS:
        A, sa = read(a)
        B, sb = read(b)
        first = A if axis == "H" else np.transpose(A, (1, 0, 2))
        second = B if axis == "H" else np.transpose(B, (1, 0, 2))
        delta = first[:, STRIDE:].astype(float) - second[:, :HALO_OVERLAP].astype(float)
        error = np.mean(delta * delta, axis=2)
        path = minimum_error_path(error)
        joined = np.empty((SIZE, SIZE + STRIDE, 3), dtype=np.uint8)
        for index, p in enumerate(path):
            split = STRIDE + int(p)
            joined[index, :split] = first[index, :split]
            joined[index, split:] = second[index, int(p):]
            assert np.array_equal(joined[index, :split], first[index, :split])
            assert np.array_equal(joined[index, split:], second[index, int(p):])
        if axis == "V":
            joined = np.transpose(joined, (1, 0, 2))
        crop = (899, 0, 1379, SIZE) if axis == "H" else (0, 899, SIZE, 1379)
        stem = f"middle_{axis}_{a}_to_{b}"
        selected = error[np.arange(SIZE), path]
        records.append({
            "axis": axis, "firstSource": sa, "secondSource": sb,
            "placement": [[0, 0], [STRIDE, 0] if axis == "H" else [0, STRIDE]],
            "seamPath": {"index": "y" if axis == "H" else "x", "values": path.tolist(), "valueMeaning": "zero-based overlap x" if axis == "H" else "zero-based overlap y"},
            "statistics": {"overlapMAE": float(np.abs(delta).mean()), "overlapP95": float(np.percentile(np.abs(delta), 95)), "pathMSE": float(selected.mean()), "straightMSE": float(error[:, 115].mean()), "pathMinMax": [int(path.min()), int(path.max())]},
            "outputs": {"pair": save(stem + "_pair.png", joined), "seam100pct": save(stem + "_seam100pct.png", joined, crop)},
        })
    record = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(), "operation": "mechanical middle-row native hard-seam QA", "status": "pending_visual_review", "isAiGeneration": False,
        "method": {"overlapPixels": 230, "cost": "mean squared original RGB difference", "optimizer": "continuous dynamic programming with +/-1 or 0 overlap-axis step per scanline", "boundary": "first source before stride+path, second source on and after it", "resize": False, "registration": False, "feathering": False, "colorCorrection": False, "pixelSynthesis": False, "exactSourceProvenanceAsserted": True}, "joins": records,
        "limits": ["Pairwise top/left joins only; bottom joins, cross-junction ownership and complete tile remain unaccepted."]}
    dest = QA / "middle_row_current_qa.json"
    dest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(dest), "joins": [{"axis": r["axis"], "first": r["firstSource"]["stem"], "second": r["secondSource"]["stem"], "statistics": r["statistics"], "outputs": r["outputs"]} for r in records]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
