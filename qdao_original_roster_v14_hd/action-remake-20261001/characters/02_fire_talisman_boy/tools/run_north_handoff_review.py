"""Finish private review handoff; cast NE slots are read only."""
from pathlib import Path
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding="utf-8")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(ZoneInfo("America/New_York")).isoformat()
own=load(ROOT/"inventory-run-north.json")
cast=load(ROOT/"inventory-run-ne-cast.json")
sources={(r["direction"],r["frame"]):r for r in own["frames"]+cast["frames"]}
ne=[
("右初触候选","right","left","右低鞋露后跟、左鞋高折，五符已修，右肩连接可追踪。","medium"),
("右承重候选","right","left","右脚近平、右膝屈，左鞋回收；和01→03臂摆幅度较大。","medium"),
("右支撑","right","left","右低鞋近平、左腿折高，鞋尖向NE；右符臂转到侧前。","high"),
("右后蹬/离地过渡候选","right?","left","本轮attempt03：沿03右髋连续，viewer右低腿向后下伸、右鞋跟起露底；左腿viewer左高折。是否末端脚尖仍触地需统一地面实播，不冒充已测触地。五符、右符左铃可追。","high"),
("右蹬后早腾空","none","both","本轮attempt03：右低鞋较04上升，右膝开始回收；左鞋高收且左腿未提前变成低长后伸。两鞋露底、无平压地。五符、右符左铃可追。","high"),
("错位腾空交换候选","none","both","本轮attempt06实际附09竹弓NE15关节/鞋轴参考：右膝折起、右鞋高，左腿下前过，双鞋高低错开，已无attempt04并腿跳。五符及右符左铃可追。左伸距较07未明显缩短，05→06→07仍需root实播确认。","high"),
("下降/换腿过渡","none","both","cast phase-v4：左低脚长轴前后、右鞋较高；尚未见压地。","medium"),
("左预接触","left?","right","cast phase-v4：左鞋向下且露后跟、右脚高回收；承重尚不确定。","medium"),
("左初触候选","left","right","本轮attempt02：左腿下伸低位鞋跟、右鞋高折；已对齐10/11左支撑。","high"),
("左缓冲支撑","left","right","cast anatomy-v2：左低鞋近平、膝屈；右鞋高折回收，手肩正确。","high"),
("左支撑","left","right","cast five-v3：左低鞋平底，右鞋高抬；五符可数。","high"),
("左后蹬/离地过渡","left?","right","cast phase-v4：左鞋后伸、跟起露底；右鞋高折，前掌接地仍需共同地面验证。","medium"),
("早腾空","none","both","左腿后伸露底、右鞋前提；两鞋没有清楚承重，铃臂已前摆。","medium"),
("交换/右腿下伸","none","both","右脚低位向下、左腿折高；右符臂回摆到体侧。","high"),
("右预接触过渡","right?","left","右鞋后跟边向下，左鞋高折；符手更低，和16连续性需实播。","medium"),
("右预接触","right?","left","右低鞋近平，左腿高回收；16→01符臂跨后摆幅度需要实播。","medium")]
dur=[75]*16
nerows=[];nefeet=[]
for f,(phase,support,swing,obs,confidence) in enumerate(ne,1):
    p=ROOT/f"frames/run/NE/{f:02}.png";source=sources[("NE",f)]
    row={"frame":f,"path":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"sourceRecord":source.get("source_record",source["native_evidence"]),"actualPhase":phase,"supportFoot":support,"recoveryOrSwingFoot":swing,"legIdentificationConfidence":confidence,"observation":obs,"trialDurationMs":dur[f-1],"sourceOwner":"north" if f in (1,2,3,4,5,6,9) else "cast_read_only"}
    nerows.append(row)
    nefeet.append({k:row[k] for k in ("frame","path","sha256","sourceRecord","sourceOwner")}|{"criteria":{"shoeAxis":"single_frame_pass","talismanCount":"single_frame_pass_five","wholeSequence":"pending_root_dynamic_review"},"observation":"实看鞋掌/鞋尖未见明确向两侧外撇，沿NE纵深；五张符顶边可逐张辨认。静态鞋向/符数通过不代表腿相位或正常速度已通过。"})
write(ROOT/"work/run-NE/grounding-review-20261003.json",{"schema":1,"direction":"NE","reviewedAt":now,"evidence":"已实际查看16帧全图、当前联系表；cast九槽只读，不修改其清单/记录。","timing":{"status":"user_requested_uniform_1200ms_client_unconfirmed","cycleMs":1200,"frameMs":75,"durationsMs":dur,"phaseWeightsApplied":False,"reason":"用户最新明确统一正常1200ms，每帧75ms；时长不代替接地姿态验收。"},"frames":nerows,"limitations":["NE05→06→07左伸距和交换相位要重点实播","01/02→03与16→01摆臂幅度要重点实播","触地/重心与统一配准未在客户端验证"]})
write(ROOT/"work/run-NE/foot-direction-review-20261003.json",{"schema":1,"direction":"NE","reviewedAt":now,"frames":nefeet,"criterion":"只对鞋轴及五符逐图给出单图通过；动态/接地仍未通过。"})
# Add explicit swing-leg observations without pretending occluded joints are proven.
allrows=[]
for direction in ("W","N","NW","NE"):
    p=ROOT/f"work/run-{direction}/grounding-review-20261003.json";doc=load(p)
    footdoc=load(ROOT/f"work/run-{direction}/foot-direction-review-20261003.json")
    for row in doc["frames"]:
        f=row["frame"];asset=ROOT/row["path"];assert sha(asset)==row["sha256"]
        if "recoveryOrSwingFoot" not in row:
            sup=row.get("supportFoot","unknown")
            row["recoveryOrSwingFoot"]={"right":"left","right?":"left?","left":"right","left?":"right?","none":"both"}.get(sup,"unknown")
            row["legIdentificationConfidence"]="medium" if sup.endswith("?") else ("high" if direction=="N" else "medium")
            if direction=="NW" and f in (1,2,3,14,15,16):
                row["legIdentificationConfidence"]="low"
                row["jointOcclusionNote"]="胯/远近腿被袍摆遮挡，支撑腿左右只是低置信推断；请在根窗口慢速实播追踪。"
        review=footdoc["frames"][f-1]
        row["singleFrameCriteria"]=review["criteria"]
        row["trialDurationMs"]=75
        row["durationMs"]=75
        if row.get("action")=="shorten_trial":
            row["action"]="review_flight_pose_at_uniform_75ms"
        allrows.append({"direction":direction,**row})
    doc["timing"]={"status":"user_requested_uniform_1200ms_client_unconfirmed","cycleMs":1200,"frameMs":75,"durationsMs":[75]*16,"phaseWeightsApplied":False,"reason":"用户最新明确统一正常1200ms；删除旧快档与非均匀权重。时长不代替接地姿态验收。"}
    for row in doc["frames"]:
        row["trialDurationMs"]=75
        row["durationMs"]=75
    doc["reviewedAt"]=now;write(p,doc)
# Verify the 55 owned asset-to-record chains only; cast files are never written.
problems=[];checks=[]
for r in own["frames"]:
    p=ROOT/r["path"];im=Image.open(p)
    rec=load(ROOT/r["native_evidence"])
    sid=load(p.with_suffix(".png.generation.json"))
    digest=sha(p)
    host=Path(rec.get("evidence",{}).get("hostOutput",""))
    native=ROOT/rec["native"]["file"]
    host_match=(sha(host)==sha(native)) if host.is_file() and native.is_file() else None
    ok=im.size==(1024,1024) and im.mode=="RGBA" and im.getchannel("A").getextrema()==(0,255) and digest==r["sha256"]==sid["sha256"]==rec["export"]["sha256"] and rec["native"]["width"]>=1024 and rec["native"]["height"]>=1024 and rec["actualModel"] is None and rec["actualQuality"] is None
    ok=ok and host_match is not False
    if not ok:problems.append(r["path"])
    checks.append({"path":r["path"],"sha256":digest,"sourceRecord":r["native_evidence"],"nativeSize":[rec["native"]["width"],rec["native"]["height"]],"hostToNativeMatch":host_match,"technicalPass":ok})
    r["single_frame_criteria"]={"shoeAxis":"single_frame_pass","wholeSequence":"pending_root_dynamic_review"}
    if r["direction"]=="NE":r["single_frame_criteria"]["talismanCount"]="single_frame_pass_five"
    r["review_record"]=f"work/run-{r['direction']}/foot-direction-review-20261003.json"
own["reviewedAt"]=now
own["reviewDocuments"]=[f"work/run-{d}/{name}-review-20261003.json" for d in ("W","N","NW","NE") for name in ("foot-direction","grounding")]
write(ROOT/"inventory-run-north.json",own)
write(ROOT/"work/run-NW/north-final-review-20261003.json",{"reviewedAt":now,"ownFrames":len(checks),"technicalPass":not problems,"problems":problems,"generationRoute":"builtin","modelTarget":"GPT Image2.5 Sunburst/max","actualModel":None,"actualQuality":None,"dynamicStatus":"pending_root_browser_review","clientStatus":"not_integrated","frames":checks,"fourDirectionPhaseReview":allrows})
print(json.dumps({"ownedFrames":len(checks),"reviewedPhaseRows":len(allrows),"technicalPass":not problems,"hostMatchCount":sum(c["hostToNativeMatch"] is True for c in checks),"hostUnverifiedCount":sum(c["hostToNativeMatch"] is None for c in checks),"problems":problems},ensure_ascii=False))

