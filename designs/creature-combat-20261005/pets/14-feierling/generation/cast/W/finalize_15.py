import json,hashlib
from pathlib import Path
from PIL import Image
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/14-feierling")
g=base/"generation/cast/W"
p=g/"15.generation.json";d=json.loads(p.read_text(encoding="utf-8"))
for i,r in enumerate(d["references"]):
 r["sha256"]=hashlib.sha256(Path(r["file"]).read_bytes()).hexdigest()
 if i==3:r["role"]="frame16-native-exact-composition-and-proportion-anchor"
d["editedFrom"]={"file":d["references"][3]["file"],"sha256":d["references"][3]["sha256"],"generationRecord":"generation/cast/W/16.generation.json"}
d["supersedes"]="generation/cast/W/15.attempt-02.generation.json"
d["repairReason"]="Previous removal-only edit enlarged character; regenerated from frame16 exact body/foot anchor with slightly raised right hand and no magic."
d["visualStatus"]="individually-viewed-accepted-for-parent-final-loop-review"
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
h=g/"15.attempt-02.generation.json";old=json.loads(h.read_text(encoding="utf-8"));old["prompt"]="generation/cast/W/15.attempt-02.prompt.txt"
old["status"]="superseded-size-drift";old["replacedBy"]="generation/cast/W/15.generation.json"
old["historicalExport"]={"file":old["file"],"sha256":old["sha256"],"note":"Replaced runtime pixels not retained."}
old.update({"file":old["nativeFile"],"sha256":old["native"]["sha256"],"width":old["native"]["width"],"height":old["native"]["height"]})
h.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding="utf-8")
for no in ("15","16"):
 r=json.loads((g/(no+".generation.json")).read_text(encoding="utf-8"));im=Image.open(r["nativeFile"]);a=im.getchannel("A")
 print(no,im.size,a.point(lambda v:255 if v>=128 else 0).getbbox(),r["nativeFile"])

