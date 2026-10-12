from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest")
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
idx=read(B/"current-artifacts.json")
for t in ["r03_c03","r03_c04","r04_c03","r04_c04"]:
 d=B/"delivery-2x2/stage-v2"; p=d/(t+".png");a=d/(t+".assembly.json");q=d/(t+".qa.json")
 previous=read(B/"delivery-2x2/stage-v1"/(t+".qa.json"))
 previous.update(createdAt=datetime.now(timezone.utc).isoformat(),candidate={"file":str(p),"sha256":sha(p)},internalAccepted=t!="r03_c04",proof=read(a)["proof"],jointReview="center-and-three-shared-boundaries-pass-road-outer-edge-pending")
 previous["evidence"].append("work-r03_c04/joint-south-resume/center-final/visual-review.json")
 previous["rootInspected"]+=["stage-v2 center, all four perimeter crops","stage-v1 south-column07/08","stage-v1 west-row01/08","stage-v1 east-row05"]
 previous["limitations"]=["Current 2x2 is a connected candidate, not final 49-tile delivery","r03_c04 road patch outer perimeter still being repaired","External outer perimeter needs adjacent artwork"]
 write(q,previous)
 idx[t]={"candidate":p.relative_to(B).as_posix(),"assembly":a.relative_to(B).as_posix(),"qa":q.relative_to(B).as_posix(),"status":"internally-accepted-joint-candidate" if previous["internalAccepted"] else "joint-candidate-road-edge-repair-pending","formalAccepted":False}
write(B/"current-artifacts.json",idx)
issues=read(B/"open-artwork-issues.json")
for e in issues["issues"]:
 if e["type"]=="center-post-ground-material-transition":e.update(status="resolved-and-root-rechecked",evidence="delivery-2x2/stage-v2/qa/center.100pct.png")
write(B/"open-artwork-issues.json",issues)

