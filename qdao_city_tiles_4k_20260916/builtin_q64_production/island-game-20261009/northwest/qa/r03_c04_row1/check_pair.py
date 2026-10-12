"""Explicit neighboring raw-native hard seam evidence for r03_c04 row1."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
from PIL import Image

ZONE = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument("--left", required=True)
ap.add_argument("--right", required=True)
ap.add_argument("--name", required=True)
args = ap.parse_args()
assert args.right.startswith("r03_c04_s01_")
assert Path(args.name).name == args.name
qa = Path(__file__).resolve().parent / args.name
qa.mkdir(exist_ok=False)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
module = runpy.run_path(str(ZONE / "assemble_tile.py"), run_name="native_pair_qa")
sources, arrays, coords = [], [], []
for stem in (args.left, args.right):
    path = ZONE / "native" / f"{stem}.png"
    coordinate_path = ZONE / "guides" / f"{stem}.input.json"
    coordinate = json.loads(coordinate_path.read_text(encoding="utf-8-sig"))
    tile_id = stem[:7]
    row, col = int(stem[9:11]) - 1, int(stem[12:14]) - 1
    source, array = module["load_raw_source"](path, Path(str(path) + ".generation.json"), tile_id, row, col)
    assert source["globalNativeBox"] == coordinate["globalBox"]
    source["coordinateInput"] = {"path": str(coordinate_path), "sha256": sha(coordinate_path)}
    sources.append(source)
    arrays.append(array)
    coords.append(coordinate["globalBox"])
assert coords[1][0] - coords[0][0] == 1024 and coords[1][1] == coords[0][1]
delta = arrays[0][:, 1024:].astype(np.float64) - arrays[1][:, :230].astype(np.float64)
path, stats = module["minimum_path"](np.mean(delta * delta, axis=2))
joined = np.empty((1254, 2278, 3), dtype=np.uint8)
for y, value in enumerate(path):
    split = 1024 + int(value)
    joined[y, :split] = arrays[0][y, :split]
    joined[y, split:] = arrays[1][y, int(value):]
    assert np.array_equal(joined[y, :split], arrays[0][y, :split])
    assert np.array_equal(joined[y, split:], arrays[1][y, int(value):])
outputs = []
for name, image, box in [("joined_pair_native.png", Image.fromarray(joined), [0, 0, 2278, 1254]), ("seam100pct.png", Image.fromarray(joined[:, 850:1420]), [850, 0, 1420, 1254])]:
    file = qa / name
    with file.open("xb") as handle:
        image.save(handle, format="PNG")
    outputs.append({"path": str(file), "sha256": sha(file), "dimensions": list(image.size), "pairCropBox": box, "nativeScale100Percent": True})
left_count = int((path + 1024).sum())
record = {"createdAtUtc": datetime.now(timezone.utc).isoformat(), "status": "pending_visual_structure_and_native_seam_review", "operation": "same-global-coordinate hard minimum-error seam", "sources": sources, "globalOverlapBox": [coords[1][0], coords[0][1], coords[0][2], coords[0][3]], "overlapDimensions": [230, 1254], "pathXByY": path.tolist(), "statistics": stats, "sourceContributions": [{"sourceId": 0, "pixels": left_count}, {"sourceId": 1, "pixels": 2278 * 1254 - left_count}], "allPixelsExactlySelectedFromRawSources": True, "outputs": outputs, "registration": False, "resizing": False, "feathering": False, "colorCorrection": False, "pixelSynthesis": False, "guidePixelsUsed": False, "formalAcceptedCount": 0}
with (qa / "join_record.json").open("x", encoding="utf-8") as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
print(json.dumps({"qa": str(qa), "statistics": stats, "dimensions": [2278, 1254], "formalAcceptedCount": 0}))
