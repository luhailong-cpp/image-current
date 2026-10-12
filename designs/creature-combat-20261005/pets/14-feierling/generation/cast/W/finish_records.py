import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
base=Path(r"D:/work/image/designs/creature-combat-20261005/pets/14-feierling")
g=base/"generation/cast/W"
for no in ("01","14","15"):
 p=g/(no+".attempt-01.generation.json")
 d=json.loads(p.read_text(encoding="utf-8"));d["prompt"]="generation/cast/W/"+no+".attempt-01.prompt.txt"
 d["status"]="superseded-by-accepted-repair";d["replacedBy"]="generation/cast/W/"+no+".generation.json"
 d["historicalExport"]={"file":d["file"],"sha256":d["sha256"],"width":d["width"],"height":d["height"],"note":"This historical runtime path is now occupied by the accepted replacement; historical export pixels are not retained."}
 d.update({"file":d["nativeFile"],"sha256":d["native"]["sha256"],"width":d["native"]["width"],"height":d["native"]["height"]})
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
rows=[]
for n in range(1,17):
 no=f"{n:02d}";p=g/(no+".generation.json");d=json.loads(p.read_text(encoding="utf-8"))
 for ref in d["references"]:
  ref["sha256"]=hashlib.sha256(Path(ref["file"]).read_bytes()).hexdigest()
 d["visualStatus"]="individually-viewed-accepted-for-parent-continuity-review"
 d["visualReview"]={"method":"Generated image displayed and inspected frame-by-frame; required native identity/style references separately viewed with view_image.","identity":"copper-red fox boy, two fox ears, one screen-right black-tip red tail","direction":"true three-quarter rear facing upper-left","ownership":"anatomical left hand wooden mask, anatomical right hand empty seal","clientVerified":False,"groupPlayback":"delegated to parent final QA"}
 if no in ("01","14","15"):
  d["supersedes"]="generation/cast/W/"+no+".attempt-01.generation.json"
  d["repairReason"]={"01":"stationary supporting feet to match 02–16","14":"removed reappearing wrong-direction glow after frame13 was already dark","15":"removed reappearing wrong-direction glow after frame13 was already dark"}[no]
 if no in ("14","15"):
  old=json.loads((g/(no+".attempt-01.generation.json")).read_text(encoding="utf-8"))
  d["editedFrom"]={"file":old["nativeFile"],"sha256":old["native"]["sha256"],"generationRecord":"generation/cast/W/"+no+".attempt-01.generation.json"}
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
 im=Image.open(d["nativeFile"]);a=im.getchannel("A");h=a.histogram()
 rows.append({"frame":no,"nativeFile":d["nativeFile"],"nativeSha256":d["native"]["sha256"],"nativeSize":im.size,"alphaExtrema":a.getextrema(),"solidAlphaAtLeast250":sum(h[250:]),"nonzeroPixels":sum(h[1:]),"bodyBBoxAlphaAtLeast128":a.point(lambda v:255 if v>=128 else 0).getbbox(),"runtime":"runtime/cast/W/"+no+".png","generationRecord":"generation/cast/W/"+no+".generation.json"})
qa=base/"QA/cast-W";qa.mkdir(parents=True,exist_ok=True)
summary={"action":"cast","direction":"W","count":16,"durationMs":45,"inspectedAt":datetime.now(timezone.utc).isoformat(),"allNative1254RGBA":all(Image.open(x["nativeFile"]).size==(1254,1254) and Image.open(x["nativeFile"]).mode=="RGBA" for x in rows),"uniqueNativeShaCount":len(set(x["nativeSha256"] for x in rows)),"perFrame":rows,"limits":["Final same-direction shared export transform and group playback belong to parent.","AI precise edits 14/15 removed unwanted light but modestly enlarged figure versus 13/16; do not hide with per-frame alignment.","09 spell cloud broader than originally requested; parent accepted retain because ownership/direction remain clear.","No client integration or runtime verification."]}
(qa/"frame-review.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"count":len(rows),"uniqueNativeSha":summary["uniqueNativeShaCount"],"allNative1254RGBA":summary["allNative1254RGBA"],"bodyBBox":[{"frame":r["frame"],"bbox":r["bodyBBoxAlphaAtLeast128"]} for r in rows]}))

