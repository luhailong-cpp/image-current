import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
q=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c15");d=q/"review/assembly-c162322cbdcca7cb2291";out=d/"repair-independent-qa-20261012";out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
idx=json.loads((d/"independent-qa-20261012/index.json").read_text())
base=np.array(Image.open(idx["candidate"]["path"]).convert("RGB"))
report={}
for v in ["single-stone-railing-20261012-v2","single-stone-railing-bottom-20261012-v3"]:
 p=q/"repairs"/v;m=json.loads((p/"composition.json").read_text());a=np.array(Image.open(m["alpha"]["path"]).convert("L"),dtype=np.uint32)
 old=np.array(Image.open(m["sourceCandidate"]["path"]).convert("RGB"))
 native=np.array(Image.open(m["native"]["path"]).convert("RGB"));nc=m.get("nativeCrop",[0,0,1254,1254]);new=native[nc[1]:nc[3],nc[0]:nc[2]].astype(np.uint32)
 box=m["pasteBoxIn4096"];x0,y0,x1,y1=box
 replay=old.copy();replay[y0:y1,x0:x1]=((old[y0:y1,x0:x1].astype(np.uint32)*(255-a[:,:,None])+new*a[:,:,None]+127)//255).astype(np.uint8)
 actual=np.array(Image.open(m["candidate"]["path"]).convert("RGB"));assert np.array_equal(replay,actual)
 ctx=np.array(Image.open(m["context"]["path"]).convert("RGB"));assert np.array_equal(ctx[115:4211,115:4211],actual)
 changed=np.any(base!=actual,axis=2);ys,xs=np.where(changed)
 entry={"manifest":{"path":str(p/"composition.json"),"sha256":sha(p/"composition.json")},"candidate":m["candidate"],"independentAlphaReplayExact":True,"contextCoreExact":True,"actualChangeBoxVersusBase":[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],"evidence":[],"nativeCrop":nc,"pasteBox":box}
 vv="v2" if v.endswith("-v2") else "v3"
 for e in idx["evidence"]:
  b=e.get("candidateBox")
  if not b:continue
  b=list(b);b=[max(0,b[0]),max(0,b[1]),min(4096,b[2]),min(4096,b[3])]
  differs=bool(changed[b[1]:b[3],b[0]:b[2]].any())
  z={"id":e["id"],"differsFromBase":differs,"candidateBox":b}
  if differs:
   f=out/(vv+"-"+e["id"]+".png");Image.fromarray(actual[b[1]:b[3],b[0]:b[2]]).save(f)
   z.update(path=str(f),sha256=sha(f),resized=False)
  entry["evidence"].append(z)
 report[vv]=entry
(out/"index.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:{"actualBox":v["actualChangeBoxVersusBase"],"changedEvidence":[e["id"] for e in v["evidence"] if e["differsFromBase"]]} for k,v in report.items()}))
