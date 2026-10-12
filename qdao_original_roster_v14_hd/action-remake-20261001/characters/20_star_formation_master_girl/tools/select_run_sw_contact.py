from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"run-SW-selection.json";s=json.loads(p.read_text(encoding="utf-8-sig"))
changes=[]
for f in s["frames"]:
 if f["frame"] not in [1,16]:continue
 v="01-v4" if f["frame"]==1 else "16-v3";old=f["source"];source=f"generation/run/SW/{v}.png";path=ROOT/source
 im=Image.open(path);im.load();foot=im.getchannel("A").crop((250,950,780,1254)).point(lambda a:255 if a>=128 else 0).getbbox()
 bottom=950+foot[3] if foot else None
 f.update(source=source,generationRecord=source+".generation.json",sourceSha256=hashlib.sha256(path.read_bytes()).hexdigest(),status="static_foot_direction_grounding_checked",visualReview="基于02正确短胫局部生成；前靴轴SW、鞋面朝上、脚底向地。已实看保留三卡/星盘与后收腿，修除原长胫落点偏低。",durationMs=75)
 f["supersedesSource"]=old;changes.append({"frame":f["frame"],"old":old,"source":source,"footRegionBottom":bottom,"note":"靴区底界仅诊断；生成时按固定底稿接触位置修骨架，未按最低像素平移"})
s["updatedAt"]=datetime.now(ZoneInfo("America/New_York")).isoformat();s["frameDurationMs"]=75;s["loopMs"]=1200
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"provenance/run-SW-contact-final-fix.json").write_text(json.dumps({"changes":changes,"staticReviewed":True,"dynamicAccepted":False,"clientIntegrated":False},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(changes,ensure_ascii=False))
