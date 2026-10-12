from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent
p=R/"repair-inputs/baseline-W.png";out=R/"repair-inputs/baseline-W-legs-late.png"
box=[500,970,800,1254]
Image.open(p).crop(box).save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rec=dict(file=out.relative_to(R).as_posix(),sha256=sha(out),createdAt=datetime.now(timezone.utc).isoformat(),derivedFrom=dict(file=p.relative_to(R).as_posix(),sha256=sha(p),record="repair-inputs/baseline-W.input.json"),operation=dict(type="reference-only-crop",crop=box,newPoseCreated=False),purpose="Only lower-leg and shoe reference for AI edits; never a final animation frame")
out.with_suffix(".input.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(rec))
