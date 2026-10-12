from pathlib import Path
import json,hashlib,sys
ROOT=Path("D:/work/image/designs/creature-combat-20261005/pets/14-feierling")
n=f"{int(sys.argv[1]):02}"
g=ROOT/"generation/cast/E"
p=g/(n+".generation.json")
data=json.loads(p.read_text(encoding="utf-8"))
receipt=json.loads((g/(n+".receipt.json")).read_text(encoding="utf-8"))
data["submittedParameters"]["referenced_image_paths"]=receipt["referenced_image_paths"]
data["generatedAt"]=receipt["returnedAt"]
data["generationStartedAt"]=receipt["startedAt"]
data["evidence"]["toolOutputHint"]=receipt["output_hint"]
for i, refpath in enumerate(receipt["referenced_image_paths"][3:], start=4):
 r=Path(refpath)
 role="Cast E frame01 camera, scale, feet and identity continuity anchor" if i==4 else ("Cast E frame10 release direction and LEFT mask continuity reference" if r.name=="10.native.png" else ("Cast E frame14 recovery pose and size continuity reference" if r.name=="14.native.png" else "Cast E frame05 raised LEFT mask continuity reference"))
 data["references"].append({"path":str(r),"role":role,"sha256":hashlib.sha256(r.read_bytes()).hexdigest()})
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
