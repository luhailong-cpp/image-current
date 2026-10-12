import json,hashlib
from pathlib import Path
from PIL import Image
root=Path(r"D:/work/image/designs/creature-combat-20261005/pets/13-yalingtong")
ev=root/"evidence/cast/W"; hist=ev/"history"; hist.mkdir(exist_ok=True)
config=json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig"))
for stem,decision in [("09.edit02","rejected: body support offset only partly corrected"),("09.edit03","rejected: pose-reference incorrectly carried forward shifted body placement"),("10.edit02","intermediate: release pose useful; residual body shift required targeted edit03")]:
 req=json.loads((ev/f"{stem}.request.json").read_text(encoding="utf-8"))
 f=Path(req["sourcePath"]); im=Image.open(f)
 roles=req.get("referenceRoles",[])
 refs=[{"path":p,"role":role,"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p,role in zip(req["submittedParameters"]["referenced_image_paths"],roles)]
 rec={"file":str(f),"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"generatedAt":req["generatedAt"],"width":im.width,"height":im.height,"mode":im.mode,"format":im.format,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":config,"submittedParameters":req["submittedParameters"],"actualModel":None,"actualQuality":None,"unverifiedReason":"Host-managed builtin route; tool did not disclose model or quality","evidence":f"evidence/cast/W/{stem}.request.json","prompt":f"evidence/cast/W/{stem}.request.json#submittedParameters.prompt","references":refs,"visualDecision":decision,"runtimeAccepted":False,"retention":"Text evidence retained; native cache pending root final-export cleanup, no project image backup created"}
 (hist/f"{stem}.candidate.generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
print("3 non-final candidate source records saved.")

