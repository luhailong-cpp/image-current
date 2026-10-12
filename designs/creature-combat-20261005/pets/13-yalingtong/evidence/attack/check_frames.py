import json,hashlib
from pathlib import Path
from PIL import Image
base=Path(__file__).resolve().parents[2]
rows=[]
for d in ("E","W"):
 for n in range(1,13):
  p=base/"runtime/attack"/d/f"{n:02d}.png"
  meta=json.loads(p.with_suffix(".png.generation.json").read_text(encoding="utf-8"))
  im=Image.open(p); sha=hashlib.sha256(p.read_bytes()).hexdigest(); a=im.getchannel("A")
  refs=[{"path":r["path"],"exists":Path(r["path"]).exists(),"shaMatches":hashlib.sha256(Path(r["path"]).read_bytes()).hexdigest()==r["sha256"]} for r in meta["references"]]
  rows.append({"direction":d,"frame":n,"file":str(p.relative_to(base)),"size":list(im.size),"mode":im.mode,"sha256":sha,"shaMatchesRecord":sha==meta["sha256"],"alphaExtrema":a.getextrema(),"alphaBBox":a.getbbox(),"transparentPixels":a.histogram()[0],"promptExists":Path(meta["prompt"]).exists(),"refs":refs,"actualModel":meta["actualModel"],"actualQuality":meta["actualQuality"],"visuallyInspected":meta["visualQA"]})
for p in (base/"evidence/attack").glob("*/*.attempt1.generation.json"):
 r=json.loads(p.read_text(encoding="utf-8")); d=p.parent.name;n=p.name[:2]
 r["prompt"]=str(base/"prompts/attack"/d/f"{n}.attempt1.txt")
 r["file"]=r["sourcePath"];r["status"]="rejected_and_superseded";r["replacedBy"]=f"runtime/attack/{d}/{n}.png"
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
summary={"count":len(rows),"expected":24,"uniqueSHA":len(set(r["sha256"] for r in rows)),"all1024RGBA":all(r["size"]==[1024,1024] and r["mode"]=="RGBA" for r in rows),"allTransparent":all(r["alphaExtrema"]== (0,255) for r in rows),"allRecordSHAMatch":all(r["shaMatchesRecord"] for r in rows),"allRefsMatch":all(all(q["exists"] and q["shaMatches"] for q in r["refs"]) for r in rows),"clientValidated":False,"playbackValidated":False,"frames":rows}
(base/"evidence/attack/technical-check.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in summary.items() if k!="frames"},ensure_ascii=False))

