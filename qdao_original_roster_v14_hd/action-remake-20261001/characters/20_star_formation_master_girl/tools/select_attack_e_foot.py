from pathlib import Path
import json, hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(ROOT/"attack-selection.json")
frames=[]
for f in old["frames"]:
 if f["direction"]!="E": continue
 f=dict(f)
 if f["frame"] in [1,2,3]:
  prior=f["source"]
  versions={1:3,2:2,3:2}
  src=f'generation/attack/E/{f["frame"]:02}-v{versions[f["frame"]]}.png'
  f.update(source=src,generationRecord=src+".generation.json",sourceSha256=sha(ROOT/src),status="static_foot_direction_checked",visualReview="脚向静态检查通过；动态待验收",footDirection="E",priorSource=prior,reviewNote="局部AI摆正后靴及相连膝踝；保留原动作、站距、上身与持物。")
 frames.append(f)
data={"schema":1,"character":ROOT.name,"action":"attack","direction":"E","updatedAt":datetime.now(ZoneInfo("America/New_York")).isoformat(),"frames":frames,"dynamicAcceptance":False}
(ROOT/"attack-E-foot-selection.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print({"frames":len(frames),"repaired":[1,2,3],"retained":list(range(4,13))})
