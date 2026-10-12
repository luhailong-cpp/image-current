from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest")
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
index=load(B/"current-artifacts.json")
for t in ["r03_c03","r03_c04","r04_c03","r04_c04"]:
 d=B/"delivery-2x2/stage-v1"; p=d/(t+".png");a=d/(t+".assembly.json");q=d/(t+".qa.json")
 accepted=t in ["r03_c03","r04_c03"]
 review={"createdAt":datetime.now(timezone.utc).isoformat(),"candidate":{"file":str(p),"sha256":sha(p)},"internalAccepted":accepted,"formalAccepted":False,"allPixelsNative":True,"proof":load(a)["proof"],"jointReview":"pending-two-local-material-repairs","evidence":["work-r03_c03/joint-final/visual-review.json","work-r04_c04/joint-west/final-v3/visual-review.json","work-r03_c04/joint-south-resume/proposal-v1/visual-review.json","work-r03_c04/paving-fresh/paving-repair-review.json"],"rootInspected":["north-column-segment-01..08","E3 lower doorpost","paving north/south/east/west and former defect4"],"limitations":["Current 2x2 is a connected candidate, not final 49-tile delivery","Road outer material join and center ground join still being repaired","External perimeter QA needs neighboring artwork"]}
 write(q,review)
 index[t]={"candidate":p.relative_to(B).as_posix(),"assembly":a.relative_to(B).as_posix(),"qa":q.relative_to(B).as_posix(),"status":"internally-accepted-joint-candidate" if accepted else "joint-candidate-local-repair-pending","formalAccepted":False}
write(B/"current-artifacts.json",index)

