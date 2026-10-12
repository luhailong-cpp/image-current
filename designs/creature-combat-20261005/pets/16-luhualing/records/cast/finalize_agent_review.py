import json,hashlib
from pathlib import Path
from PIL import Image
r=Path(__file__).resolve().parents[2]
p=r/"records/cast/cast-agent-visual-review.json"; data=json.loads(p.read_text(encoding="utf-8"))
updates={3:"最终修复已实际看：以正确W02为编辑目标，枝手始终屏左肩外侧，稍收肘向内，壶原屏右侧保持。后视遮挡下不强求枝尖真实贴壶口；无跨头或中线。",4:"最终修复已实际看：以正确W02为编辑目标，枝手在屏左肩外侧稍抬，枝尖靠自身肩侧，壶屏右位置稳定；03→04→05抬枝阶段连续，未穿越身体。",5:"最终修复已实际看：壶右枝左，露珠由壶口汇聚，枝提前抬起可承接03/04/06；一壶一枝、原肩臂归属和后视身份保持。"}
for item in data["entries"]:
    if item["direction"]=="W" and item["frame"] in updates: item["note"]=updates[item["frame"]]
    if not(item["direction"]=="E" and item["frame"] in (10,11)):
        gp=r/"records/cast"/item["direction"]/(f'{item["frame"]:02d}.generation.json')
        rec=json.loads(gp.read_text(encoding="utf-8")); rec["visualReview"]={"status":"individually_viewed","note":item["note"],"continuousPlayback":"root final review pending","client":"not performed"}
        gp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
data["poseAdjustment"]="W03/W04 use rear-camera occlusion adjustment authorized by root: keep branch hand outside original screen-left shoulder; compact elbow/wrist gathering replaces visible branch-tip/pot contact to prevent arm-crossing jump."
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
paths=[r/".work/cast"/d/f"{i:02d}.png" for d,ns in [("E",range(1,17)),("W",range(1,9))] for i in ns]
qa={"count":len(paths),"missing":[str(p) for p in paths if not p.exists()],"uniqueSha256":len({hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),"sizes":sorted({Image.open(p).size for p in paths}),"modes":sorted({Image.open(p).mode for p in paths}),"alphaExtrema":sorted({Image.open(p).getchannel("A").getextrema() for p in paths})}
(r/"records/cast/cast-agent-technical-check.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8")
s=r/"cast-status.json"; status=json.loads(s.read_text(encoding="utf-8")); status["requiresRootExportRefresh"]=["W/03","W/04"]; status["latestRepair"]="W03/W04 complete and individually viewed; same-side branch gathering";status["technicalCheck"]="records/cast/cast-agent-technical-check.json";s.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(qa))

