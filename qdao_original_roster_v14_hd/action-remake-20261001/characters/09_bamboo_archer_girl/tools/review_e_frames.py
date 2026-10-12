import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
notes={1:"身份、两手和完整弓可读；待与峰值03统一固定脚位。",2:"已重绘收窄脚距，接触表实际核实当前版本；与03横向脚位仍需统一。",3:"已实际查看原生和1024透明导出，屈膝后仰、右手护腹、左手持弓明确；待整段脚位与镜头一致验收。",4:"回弹上身清楚；与03比较双脚向右偏移，待统一。",5:"右臂下降收势明确；与03比较脚位仍有偏移。",6:"已重绘为右空手低位警戒，误取箭问题消除；接触表确认手臂与身体相连，仍待整段脚位验收。"}
rows=[]
for i,note in notes.items():
 p=ROOT/"runtime/hit/E"/f"{i:02d}.png"
 if p.exists():rows.append({"slot":f"hit/E/{i:02d}","status":"needs_review","sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"evidence":note,"staticAnatomy":"reviewed","dynamicApproval":False})
for i in range(1,13):
 p=ROOT/"runtime/attack/E"/f"{i:02d}.png"
 if p.exists():rows.append({"slot":f"attack/E/{i:02d}","status":"needs_review","sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"evidence":"已实际查看原图和12帧接触表，取箭、拉弦、释放、收势顺序明确；04–06为一箭/右指/弦顶点相连，07后无箭。仍待比例、脚位及播放衔接验收。","staticAnatomy":"reviewed","dynamicApproval":False})
for i in range(1,17):
 p=ROOT/"runtime/cast/E"/f"{i:02d}.png"
 if p.exists():rows.append({"slot":f"cast/E/{i:02d}","status":"needs_review","sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"evidence":"已实际查看原图和16帧接触表，左手完整弓/右手箭弦可读；05–09蓄力，10释放，11展开收势。05初搭弦偏深、11到12脚距收回突变，待定点修正/动态验收。","staticAnatomy":"reviewed","dynamicApproval":False})
out=ROOT/"review-parts/combat-E.json";out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"frames":rows,"sequences":[{"sequence":"hit/E","status":"needs_revision","evidence":"6张已齐，02脚距收窄和06收势已修；整体脚位仍需统一，没有给出动态通过。"},{"sequence":"attack/E","status":"needs_review","evidence":"12帧原图及接触表已检查，04–06弓箭弦机械连接可读；脚距/根位置细跳待复核。"},{"sequence":"cast/E","status":"needs_revision","evidence":"16帧原图及接触表已检查；05搭弦偏深、11到12脚距突变需修。"}]},ensure_ascii=False,indent=2),encoding="utf-8")
print("Explicit E frame review saved.")

