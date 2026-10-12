"""Mechanical native seam evidence for one built-in local repair, no synthesis."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy

import numpy as np
from PIL import Image

ZONE = Path(__file__).resolve().parents[1]
QA = ZONE / "qa/s03_04a05_check"
QA.mkdir(exist_ok=False)
DP = runpy.run_path(str(ZONE / "assemble_tile.py"), run_name="repair_qa")["minimum_path"]
new_path = ZONE / "native/r03_c03_s03_04_a05.png"
bottom_path = ZONE / "native/r03_c03_s04_04_a01.png"
guide_path = ZONE / "guides/r03_c03_s03_04_a05.hard-seam-edit-target.png"
base_path = ZONE / "native/r03_c03_s03_04_a04.png"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    image = Image.open(path).convert("RGB")
    assert image.size == (1254, 1254)
    return np.array(image)


def save(name, pixels, role):
    path = QA / name
    image = Image.fromarray(pixels)
    with path.open("xb") as handle:
        image.save(handle, format="PNG")
    return {"path": str(path), "sha256": sha(path), "dimensions": list(image.size), "role": role, "nativeScale100Percent": True}


new, bottom, guide, base = map(read, (new_path, bottom_path, guide_path, base_path))
delta = new[1024:].astype(np.float64) - bottom[:230].astype(np.float64)
seam, stats = DP(np.mean(delta * delta, axis=2).T)
joined = np.empty((2278, 1254, 3), dtype=np.uint8)
joined[:1254] = new
for x, y in enumerate(seam):
    joined[1024 + int(y):, x] = bottom[int(y):, x]
outputs = [
    save("bottom_hard_minerror100pct.png", joined[899:1379], "new a05/bottom native hard seam, combined crop [0,899,1254,1379)"),
    save("central_junction100pct.png", joined[975:1175, 540:850], "central repaired junction and inlet context, combined crop [540,975,850,1175)"),
    save("guide_vs_a05_repair100pct.png", np.concatenate((guide[975:1175, 540:850], new[975:1175, 540:850]), axis=1), "left=actual old hard seam edit guide;right=new native a05; both [540,975,850,1175)"),
]
outside = np.ones((1254, 1254), dtype=bool)
outside[995:1135, 580:810] = False
drift = {}
for label, ref in [("editGuide", guide), ("a04Base", base)]:
    difference = np.abs(new.astype(np.int16) - ref.astype(np.int16))
    drift[label] = {"outsideRequestedRoiChangedPixels": int(np.count_nonzero(np.any(difference[outside] != 0, axis=1))), "outsideRequestedRoiMeanAbsoluteRgbDifference": float(difference[outside].mean()), "top230MeanAbsoluteRgbDifference": float(difference[:230].mean()), "left230MeanAbsoluteRgbDifference": float(difference[:, :230].mean())}
record = {"createdAtUtc": datetime.now(timezone.utc).isoformat(), "status": "pending_native_visual_review", "operation": "same-coordinate minimum-error hard native seam", "sources": [{"path": str(p), "sha256": sha(p)} for p in (new_path, bottom_path, guide_path, base_path)], "seamPathYByX": seam.tolist(), "statistics": stats, "driftMeasurements": drift, "outputs": outputs, "registration": False, "resizing": False, "feathering": False, "colorCorrection": False, "pixelSynthesis": False, "formalAcceptedCount": 0}
with (QA / "record.json").open("x", encoding="utf-8") as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
print(json.dumps({"qa": str(QA), "drift": drift}))
