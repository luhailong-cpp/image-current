"""S-only latest support-pair review and deterministic preview export."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json, hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pairs=[
("右脚",[14,15],"前端初接","前伸右脚平掌初接，脚尖沿S；左脚继续摆动"),
("右脚",[0,1],"前侧承重","右脚前载，膝踝自然压缩，脚位从前端收近"),
("右脚",[2,3],"身体经过","右支撑靴进一步收至身体下方，另一膝前摆；脚尖无外翻"),
("右脚",[4,5],"后侧蹬离","原蜷起后脚已真实伸到后方前掌支撑；左腿前摆露底为摆动脚"),
("左脚",[6,7],"前端初接","左前伸鞋掌放平，原宽鞋底仰起消除"),
("左脚",[8,9],"前侧承重","左支撑靴由前端收近，鞋底压平，膝踝承重"),
("左脚",[10,11],"身体经过","左脚继续向髋下收近，脚尖沿S而非向侧面外撇"),
("左脚",[12,13],"后侧蹬离","左后脚从蜷起改为伸踝前掌支撑，右脚前摆准备换脚")]
changed=[2,3,4,5,6,8,9,10,11,12,13,14]
frames=[]; images=[]; errors=[]; native_ids=[]
for n in range(16):
 p=R/"runtime/run/S"/f"{n:02}.png"; g=p.with_name(p.name+".generation.json"); rec=json.loads(g.read_text(encoding="utf-8-sig")); source=rec["derivedFrom"][0]; native=R/source["file"]
 im=Image.open(p).convert("RGBA"); ni=Image.open(native).convert("RGBA")
 if sha(p)!=rec["sha256"]: errors.append(f"SHA mismatch {n}")
 if im.size!=(1024,1024) or ni.size!=(1254,1254): errors.append(f"dimensions {n}")
 if ni.resize((1024,1024),Image.Resampling.LANCZOS).tobytes()!=im.tobytes(): errors.append(f"not whole-canvas {n}")
 if im.getchannel("A").getextrema()[0]!=0: errors.append(f"alpha {n}")
 native_ids.append(sha(native))
 leg,pair,phase,observation=next(x for x in pairs if n in x[1])
 frames.append({"frame":n,"direction":"S","file":p.relative_to(R).as_posix(),"sha256":sha(p),"generationRecord":g.relative_to(R).as_posix(),"nativeSource":source,"supportLeg":leg,"pairFrames":pair,"positionPhase":phase,"observation":observation,"changedByFinishS":n in changed,"actualModel":None,"actualQuality":None})
 images.append(im.resize((480,480),Image.Resampling.LANCZOS))
if len(set(native_ids))!=16: errors.append("native source reused")
for speed,duration in [("1200",75),("4800",300)]:
 p=R/"preview"/f"run-S-contactpairs-{speed}.webp"
 images[0].save(p,save_all=True,append_images=images[1:],duration=duration,loop=0,lossless=True,method=6)
 meta={"file":p.relative_to(R).as_posix(),"sha256":sha(p),"derivedFrom":[{"file":x["file"],"sha256":x["sha256"],"generationRecord":x["generationRecord"]} for x in frames],"operation":"16 original whole-canvas images uniformly downscaled to480; no duplicate, interpolation, mirror or spatial re-alignment","frameMs":duration,"cycleMs":16*duration,"actualModel":None,"actualQuality":None}
 p.with_name(p.name+".generation.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
report={"scope":"run/S only","reviewedAt":datetime.now(timezone.utc).isoformat(),"latestHumanRequirement":"直脚着地两帧，再旁边点两帧，依次过渡；同一支撑脚在不同相对位置各两张独立姿态","timing":{"frameMs":75,"pairMs":150,"cycleMs":1200},"pairMap":[{"supportLeg":l,"frames":ns,"position":p,"observation":o} for l,ns,p,o in pairs],"changedFrames":changed,"retainedFrames":[0,1,7,15],"travel":"正面S朝向镜头；前后深度靠膝踝及鞋掌姿态表达，未将整图平移或让脚尖向侧面外撇","reference":"已实际查看并传入09竹弓少女runtime/run/S/01.png；只比较同向脚轴，06自身身份及持物保留。后续局部精修附目标原生图与designs已确认画法，防止身份相机漂移。","reviewMethod":["逐张查看原生新输出与16帧联系图","本目录16个runtime及native尺寸/透明/SHA/全画布导出像素核对","生成正常1200ms及慢放4800ms预览；整圈播放观感交主窗口最终验收"],"technicalIssues":errors,"staticIndividualFrameReviewCompleted":True,"wholeCycleVisualApproved":False,"clientIntegrated":False,"modelNote":"目标GPT Image2.5Sunburst/max；宿主管理内置入口无model/quality选择器，实际提交及返回版本/质量未确认","frames":frames}
(R/"review/run_S_contactpairs_20261004.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
lines=["# S方向连续接地位置段复核","","正常16×75ms=1200ms，每位置段2帧=150ms。全为独立原生图；无复制停帧、插值、镜像或整图平移。","","| 支撑脚 | 帧号 | 空间位置 | 实图复核 |","| --- | --- | --- | --- |"]
lines += [f"|{leg}|{','.join(f'{n:02}' for n in pair)}|{phase}|{obs}|" for leg,pair,phase,obs in pairs]
lines += ["","已完成逐图脚轴、支撑职责、上身相机和原生导出的静态复核。整圈主窗口播放观感验收尚未在本子任务宣称通过；客户端未接入。","","当前预览：../preview/run-S-contactpairs-1200.webp；慢放：../preview/run-S-contactpairs-4800.webp。","逐图路径与SHA见同名JSON。模型目标与实际参数已分开记录，实际版本/质量未确认。"]
(R/"review/run_S_contactpairs_20261004.md").write_text("\n".join(lines),encoding="utf-8")
print(json.dumps({"frames":len(frames),"uniqueNative":len(set(native_ids)),"errors":errors,"normal":"preview/run-S-contactpairs-1200.webp","slow":"preview/run-S-contactpairs-4800.webp"},ensure_ascii=False))

