import json,hashlib,os,uuid,msvcrt
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 p=Path(p); t=p.with_name("."+p.name+"."+uuid.uuid4().hex+".tmp");t.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8");os.replace(t,p)
now=datetime.now(timezone.utc).isoformat()
pairs={"L":[[15,16],[1,2],[3,4],[5,6]],"R":[[7,8],[9,10],[11,12],[13,14]]}
coords={
"E":{1:[660,940],2:[680,940],3:[480,937],4:[485,940],5:[320,953],6:[248,926],7:[755,944],8:[690,936],9:[510,948],10:[462,920],11:[400,934],12:[358,930],13:[290,916],14:[320,922],15:[770,938],16:[780,938]},
"NE":{1:[548,924],2:[550,932],3:[470,970],4:[510,944],5:[398,960],6:[398,980],7:[739,943],8:[752,942],9:[690,948],10:[733,948],11:[620,954],12:[672,951],13:[585,974],14:[592,972],15:[607,950],16:[633,950]}}
labels=["前位落地","近身承重","身体经过","后位蹬地"]
issues={
"E":["各对并非几何固定同一点：05/06、07/08的靴中心相差约60–70px，严格位置稳定与世界地面接触尚未通过。","02的头顶/头部轮廓略高于相邻帧；09→10→11弓角变化仍可见，动态连贯性未通过。","前掌后蹬以透明单帧姿态推断，未以引擎位移标定滑步；正常1200ms/慢放/接缝未获得动态视觉验收。"],
"NE":["03/04、09/10、11/12各对靴中心存在约40–55px差别，方向总体按对后移，但逐帧固定位置尚未通过。","左脚前位15/16→近身01/02有头髋高度变化；08→09、14→15的鞋面/鞋跟朝向和透视接缝仍需动态核验，未据单帧声称脚轴全通过。","透明单帧只支持姿态接触推断；真实地面承重/滑步及正常1200ms循环、慢放视觉验收未完成。"]}
records={}
font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",18)
for d in ["E","NE"]:
 frameRecs=[];spatial=[]
 for f in range(1,17):
  p=ROOT/f"runtime/run/{d}/{f:02d}.png";im=Image.open(p);assert im.size==(1024,1024) and im.mode=="RGBA" and im.getchannel("A").getextrema()[0]==0
  foot=next(k for k,ps in pairs.items() if any(f in pair for pair in ps));idx=next(i for i,pair in enumerate(pairs[foot]) if f in pair)
  frameRecs.append({"frame":f,"file":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"supportFoot":foot,"position":idx+1,"phase":labels[idx],"approxSupportBootCenter1024":coords[d][f],"inspection":"full-size current PNG or generated native result plus refreshed current contact","staticContactReading":"平底/跟前掌承重" if idx<3 else "前掌低位接触、脚跟抬起后蹬","staticStatus":"pose_contact_readable_pending_sequence_acceptance"})
 assert len({x["sha256"] for x in frameRecs})==16
 for foot,ps in pairs.items():
  for i,pair in enumerate(ps):
   spatial.append({"supportFoot":foot,"position":i+1,"phase":labels[i],"frames":pair,"durationMs":150,"actualApproxBootCenters":[coords[d][f] for f in pair],"meanX":sum(coords[d][f][0] for f in pair)/2,"evidence":"按当前全尺寸靴形中心人工近似标注；本组相对前组沿屏左后移，后蹬跟部抬起。不是最低像素对齐，不是世界坐标。","sameFootRoots":"E按遮挡/裤口追踪；NE左侧裤口为L、右侧裤口为R；本轮已移除换腿根及多靴拒稿。","twoIndependentPoses":True})
 sheet=Image.new("RGB",(8*256,2*282),(242,240,230));dr=ImageDraw.Draw(sheet)
 for row,(foot,ps) in enumerate(pairs.items()):
  for col,f in enumerate(sum(ps,[])):
   im=Image.open(ROOT/f"runtime/run/{d}/{f:02d}.png").resize((256,256),Image.Resampling.LANCZOS);sheet.paste(im,(col*256,row*282),im)
   dr.text((col*256+8,row*282+256),f"{d} {foot} P{col//2+1}  {f:02d}",font=font,fill=(24,70,50))
 out=ROOT/f"preview/qa/run-{d}-paired-contact.png";sheet.save(out)
 normal=Image.open(ROOT/f"preview/qa/run-{d}-normal.apng");dur=[]
 for i in range(normal.n_frames):normal.seek(i);dur.append(normal.info.get("duration"))
 assert len(dur)==16 and all(x==75 for x in dur)
 record={"schemaVersion":1,"character":"09_bamboo_archer_girl","direction":d,"reviewedAt":now,"reviewer":"finish_e_ne","status":"paired_contact_repairs_saved_pending_dynamic_and_strict_position_review","latestRequirement":"每支撑脚连续8张独立接触姿态，四个沿行进轴的空间位置，每处两帧；16×75ms=1200ms","timing":{"frameMs":75,"frameCount":16,"cycleMs":1200,"slowFrameMs":300},"supportOrder":pairs,"supportContactFrames":{"L":[15,16,1,2,3,4,5,6],"R":[7,8,9,10,11,12,13,14]},"poseContactInferenceCount":{"L":8,"R":8},"worldSpaceContactValidated":False,"coordinatesMethod":"人工视觉近似靴中心；允许约±20px误差；用于对比成对相对位置，非足底追踪、非物理地面标定。","spatialPairs":spatial,"frames":frameRecs,"remainingNotPassed":issues[d],"dynamic":False,"dynamicVisualAcceptance":False,"clientModified":False,"browserUsed":False,"historicalAcceptanceFileModified":False,"preview":{"contact":f"preview/qa/run-{d}-contact.png","pairedContact":out.relative_to(ROOT).as_posix(),"normal":f"preview/qa/run-{d}-normal.apng","slow":f"preview/qa/run-{d}-slow.apng","apngDurationsMs":dur},"modelEvidence":"每次请求/回执与runtime图旁generation.json；配置目标gpt-image-2.5-sunburst/max，内置实际model/quality均未披露，null。","prohibitedOperationsPerformed":{"copiedFrame":False,"mirrored":False,"interpolated":False,"wholeFigureTranslation":False,"lowestFootAlignment":False}}
 write(ROOT/f"audit/run-{d}-paired-ground-review.json",record);records[d]=record
p=ROOT/"review-parts/run-north.json"
with open(p.with_suffix(".json.lock"),"a+b") as lock:
 lock.seek(0,os.SEEK_END)
 if lock.tell()==0:lock.write(b"0");lock.flush()
 lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_LOCK,1)
 try:
  data=read(p)
  for row in data["frames"]:
   bits=row.get("slot","").split("/")
   if len(bits)!=3 or bits[1] not in records:continue
   d=bits[1];f=int(bits[2]);r=records[d]["frames"][f-1]
   row.update({"sha256":r["sha256"],"status":"needs_review","staticInspected":True,"staticInspectionScope":r["inspection"],"phase":r["phase"],"supportFoot":r["supportFoot"],"evidence":r["staticContactReading"]+"；配对空间审阅见audit/run-"+d+"-paired-ground-review.json","phaseConfidence":"medium","dynamicStatus":"not_verified","pairedGroundReview":"audit/run-"+d+"-paired-ground-review.json","pairedGroundPosition":r["position"],"footAxisReview":"本轮实际单帧和成对接图；位置与脚轴接缝仍待动态，不继承旧全通过文字。","toeAxisFinding":"no_obvious_gross_splay_in_static_pose_depth_transition_unverified","footOrientation":"E屏右；NE沿右上透视轴，鞋跟/鞋面与相邻帧接缝尚未动态验收。"})
  for seq in data["sequences"]:
   d=seq.get("sequence","").split("/")[-1]
   if d not in records:continue
   r=records[d]
   seq.update({"status":"needs_review","frameSha256":[x["sha256"] for x in r["frames"]],"evidence":"实际已修配对接触姿态与当前SHA，详见独立空间审阅。","staticPhaseStatus":"paired_contact_repairs_saved_pending_strict_position_and_dynamic","remainingIssues":issues[d],"pairedGroundReview":"audit/run-"+d+"-paired-ground-review.json","dynamic":False,"dynamicReview":"未使用浏览器；APNG已生成并核验时长，未声称动态视觉通过或客户端通过。"})
  write(p,data)
 finally:lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
print(json.dumps({"directions":["E","NE"],"frameCount":32,"uniquePerDirection":16,"reviewsWritten":True,"dynamic":False,"reviewPartsTouched":"E/NE rows only; NW retained"},ensure_ascii=False))


