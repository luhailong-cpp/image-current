from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parent
rows=[];sources=[]
for i in range(7,13):
 rp=R/f"records/attack-W/{i:02}.generation.json"
 r=json.loads(rp.read_text(encoding="utf-8"));p=Path(r["derivedFrom"]["path"])
 if "guardfix-20261008" not in r["prompt"]:continue
 with Image.open(p) as im:
  a=np.array(im.getchannel("A"))
  mx=[int(a[0].max()),int(a[-1].max()),int(a[:,0].max()),int(a[:,-1].max())]
  rows.append(dict(file=r["file"],sha256=r["sha256"],source=str(p),nativeSha256=r["native"]["sha256"],prompt=r["prompt"],nativeSize=list(im.size),nativeEdgeOrder=["top","bottom","left","right"],nativeEdgeMax=mx,edgeAbove64=max(mx)>64))
for p in sorted((R/"records/attack-W").glob("*.guardfix-20261008*.generation.json")):
 if not 7<=int(p.name[:2])<=12:continue
 r=json.loads(p.read_text(encoding="utf-8"))
 if p.name=="07.guardfix-20261008.generation.json":
  r["disposition"]="rejected-candidate";p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
 if p.name=="07.guardfix-20261008-retry1.generation.json":
  r["disposition"]="selected-final";p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
 sources.append(dict(path=r["file"],sha256=r["sha256"],record=p.relative_to(R).as_posix(),disposition=r.get("disposition")))
review=dict(recordedAt=datetime.now(timezone.utc).isoformat(),scope="attack W07-12",status="static-review-in-progress" if len(rows)<6 else "static-review-complete",route="builtin-imagegen",frames=rows,visualChecks=["Generated outputs and fixed-transform exported frames viewed individually","Two hands and shoes; anatomical left supports harp, right plucks/recovers","True back three-quarter W, chestnut braid and ivory/indigo silk preserved","Compact staggered guard feet restored, no wide-spread stance"],notes=["W07 raised pluck and W08 lowered wrist distinct","W09 returning wrist redraw differs about25nativepx from original input but preserves recovery; left ribbon loop retained","W12 dark-shoe threshold merges both shoes into one component; root single-component centroid is not a valid single-shoe metric for this frame","W12 only six right-edge pixels y886..891 have alpha>64, max88; no solid subject cut seen, retain evidence for root review","No playback claim; final temporal review delegated to root"],cleanupCandidates=sources,cleanupPerformed=False)
def measured_regions(p):
 a=np.asarray(Image.open(p).convert("RGBA"));out=[]
 for x0,y0,x1,y1 in [(560,1135,660,1245),(650,1030,745,1140)]:
  q=a[y0:y1,x0:x1];yy,xx=np.nonzero((q[:,:,3]>150)&(q[:,:,:3].max(2)<185))
  out.append(dict(box=[x0,y0,x1,y1],pixels=len(xx),centroid=[round(float(xx.mean())+x0,2),round(float(yy.mean())+y0,2)]))
 return out
if len(rows)==6:
 review["regionMeasurement"]={"limits":"Manually bounded dark regions, excludes portions of shoes; auxiliary comparison only, not joint locations or playback proof","baseline":measured_regions(R/"repair-inputs/baseline-W.png"),"frame12":measured_regions(Path(rows[-1]["source"]))}
(R/"records/attack-W/guardfix-20261008-late-review.json").write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(dict(checked=len(rows),attention=[x["file"] for x in rows if x["edgeAbove64"]],sources=len(sources)),ensure_ascii=False))
