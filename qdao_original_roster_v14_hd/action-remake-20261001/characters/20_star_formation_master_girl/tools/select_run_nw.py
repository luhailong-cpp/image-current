from pathlib import Path
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/"provenance/run-NW-working-slots.json").read_text(encoding="utf-8"))
phases=["右脚接触、左脚后收","右脚承重缓冲","右脚支撑、左腿前移","右脚蹬离、左膝回收","左腿前送短腾空","左腿前送腾空末段","左脚下降","左脚预接触","左脚接触、右腿后折","左脚承重","左脚提跟、右腿回收","离地转短腾空","双腿转换腾空","右脚下降、左腿后折","右脚初接触","右脚接触回环"]
for f,phase in zip(data["frames"],phases):
 f["status"]="static_direction_phase_checked";f["visualReview"]="已实看原生与16帧联系表；靴轴沿NW，支撑靴鞋底向地面，后抬脚可见鞋底，盘右卡左持物不交换。"
 f["phaseObserved"]=phase
 f["durationMs"]=75
 if f["frame"]==9:f["previousRequestedSlot"]="01";f["selectionReason"]="原请求01-v2实际为异侧左脚接触，保留真实原生并重分配到09，未复制或镜像"
data.update(character=ROOT.name,action="run",direction="NW",updatedAt=datetime.now(ZoneInfo("America/New_York")).isoformat(),frameDurationMs=75,loopMs=1200,dynamicAccepted=False,reference="09_bamboo_archer_girl/preview/qa/run-NW-contact.png",notes=["01/09为相反支撑脚；保留各自真实来源，不用镜像。","旧12–16曾重复左脚相位，选入局部修改后的12–14-v2与15/16-v3。","正背三分之四方向后收靴自然露底，支撑脚保持地面朝向；没有逐帧最低像素对齐。"])
assert len({f["sourceSha256"] for f in data["frames"]})==16
(ROOT/"run-NW-selection.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(ROOT/"provenance/run-NW-static-review.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("NW16 selected with unique sources")
