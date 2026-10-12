"""Select inspected localized prop fixes without changing timing or ground registration."""
from pathlib import Path
from datetime import datetime
import json,hashlib
B=Path(__file__).resolve().parents[1]
changes={
 "attack":{6:("06-clearance-v1","右灯臂适度屈肘，灯体退回画布安全范围；左右手、双脚与承重姿势保留。"),7:("07-tassel-v2","出手后灯向前下方随势；灯穗改为向上卷起，未再垂到原先低于脚底的位置。"),11:("11-tassel-v2","起身回守，右灯在髋旁；灯穗向内卷起，双脚与手臂位置保留。")},
 "cast":{12:("12-volume-v1","右灯回收于腹前，灯碗体量恢复，左瓶护胸。"),15:("15-clearance-v1","施法末段低位收灯；灯穗向外上方卷起，避开前鞋，双脚与持手保留。"),16:("16-clearance-v1","稳定收势；灯穗保持上卷，不再遮住前鞋或拖过脚底。")}}
stamp=datetime.now().astimezone().isoformat()
rows=[]
for action,slots in changes.items():
 p=B/f"review/{action}-E-sequence-input.json";data=json.loads(p.read_text(encoding="utf-8-sig"))
 for f in data["frames"]:
  slot=f.get("frame",f.get("slot"))
  if slot not in slots:continue
  stem,phase=slots[slot];source=f"generation/{action}/E/{stem}.png";src=B/source
  digest=hashlib.sha256(src.read_bytes()).hexdigest()
  old=f["source"]
  f.update(source=source,sourceSha256=digest,observedPhase=phase,issues=[],review=f"generation/{action}/E/{stem}.review.json",generationRecord=source+".generation.json")
  row=dict(action=action,direction="E",frame=slot,source=source,sourceSha256=digest,replacedSource=old,status="selected_current_candidate",reviewedAt=stamp,observed=phase,visualAcceptance=False,clientAcceptance=False)
  (B/f["review"]).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding="utf-8");rows.append(row)
 if action=="attack":
  data["issues"]=[s for s in data.get("issues",[]) if not s.startswith("06灯距")]
  data["issues"].append("06边距、07/11灯穗过低已局部修正；07仍为低位随势，最终游戏收招切换未验证。")
 else:
  data["issues"]=[s for s in data.get("issues",[]) if "12" not in s and "15" not in s and "16" not in s]
  data["issues"].append("12灯碗体量与15/16灯穗遮鞋已局部修正；未改变脚位或整图注册。")
 data["updatedAt"]=stamp;p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
for stem,reason in [("07-clearance-v1","wrong arm ownership, body shifted and lantern clips right edge"),("11-clearance-v1","lamp raised too far toward shoulder; breaks recovery trajectory")]:
 p=B/f"generation/attack/E/{stem}.review.json"
 p.write_text(json.dumps(dict(status="rejected_not_selected",reviewedAt=stamp,reason=reason),ensure_ascii=False,indent=2),encoding="utf-8")
(B/"review/combat-clearance-review.json").write_text(json.dumps(dict(reviewedAt=stamp,frames=rows,clientAcceptance=False),ensure_ascii=False,indent=2),encoding="utf-8")
print("Selected six localized prop fixes; original frame timing and ground registration preserved.")
