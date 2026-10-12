import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
v=json.loads((root/"qa/visual-review.json").read_text(encoding="utf-8"))
for f in v["frames"]:
 p=root/f["file"]
 for rec in [Path(str(p)+".generation.json"),root/"records"/f"{p.parent.parent.name}-{p.parent.name}-{p.stem}.json"]:
  if not rec.exists():continue
  r=json.loads(rec.read_text(encoding="utf-8"))
  if r.get("sha256")!=f["sha256"]:continue
  r["visualStatus"]="final-frame-viewed; "+f["sequenceReview"]
  r["finalVisualReview"]={"record":"qa/visual-review.json",**{key:f[key] for key in ("stillReview","sequenceReview","clientReview","evidence")}}
  if "sequenceEvidence" in f:
   r["finalVisualReview"]["sequenceEvidence"]=f["sequenceEvidence"]
  rec.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
cleanup=dict(checkedAt=datetime.now(timezone.utc).isoformat(),scope=str(root),runtimePngCount=len(list((root/"runtime").rglob("*.png"))),retainedImages={"runtime":"68 final PNGs","previews":"12 animated WebP previews","qa":"6 numbered final contact sheets"},workspaceOriginalOrRejectedImageCopies=[],workInProgressUniqueImageCopies=[],deletedPaths=[],replacementNote="Rejected working runtime versions were overwritten by separately generated final repairs after their text/SHA records were retained. No image backup copies created.",sharedReferences="Original E/W identity and approved style remain in shared Image source locations; not deleted.",hostCache="Generated host-native files are outside this pet's only permitted write directory. No host cache deletion performed; actual paths and hashes retained as historical evidence.")
(root/"cleanup.json").write_text(json.dumps(cleanup,ensure_ascii=False,indent=2),encoding="utf-8")
print("Synchronized current visual-review pointers; recorded retention scope.")
