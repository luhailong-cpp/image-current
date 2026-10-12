"""Native-size review crops from an existing candidate; no painting or scaling."""
from pathlib import Path
import hashlib
import json
from PIL import Image

zone = Path(__file__).resolve().parent
source = zone / "tiles/r06_c12.candidate.png"
im = Image.open(source).convert("RGB")
assert im.size == (4096, 4096)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
out = zone / "qa/r06_c12/cores"
out.mkdir(parents=True, exist_ok=True)
items = []
for row in range(1, 5):
    for col in range(1, 5):
        box = [(col-1)*1024, (row-1)*1024, col*1024, row*1024]
        path = out / f"p{row}{col}.native-1to1.png"
        im.crop(box).save(path)
        items.append({"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "box": box, "pixelScale": 1, "pixels": [1024, 1024],
                      "visualReview": "pending", "formalAccepted": False})
(out / "manifest.json").write_text(json.dumps({
    "sourceCandidate": str(source), "sourceCandidateSha256": source_hash,
    "purpose": "Inspect entire native cores, including internal anchor-to-new-art transitions away from core joins.",
    "operation": "integer crop only; no resize, blend, feather or painting",
    "items": items
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"sourceCandidateSha256": source_hash, "coreReviewCount": len(items)}))
