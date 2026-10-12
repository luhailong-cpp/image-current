from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib,sys
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding="utf-8")
invp=R/"inventory-hit.json"
inv=read(invp)
beforep=R/"reviews/video-axis-S-SW-before-20261004.json"
if sys.argv[1]=="before":
 save(beforep,{"reviewStarted":datetime.now(ZoneInfo("America/New_York")).isoformat(),"frames":[{"path":x["path"],"sha256":sha(R/x["path"]),"source_record":x["source_record"],"direction":x["direction"],"frame":x["frame"]} for x in inv["frames"] if x["action"]=="run" and x["direction"] in ["S","SW"]]})
 print("32 current before SHA saved");sys.exit()
before={x["path"]:x for x in read(beforep)["frames"]}
reasons={
"S":[
"左脚在髋下承重，右脚后收，两鞋中线跟随小腿纵深，没有横向翻踝。",
"左脚承重，右膝开始前摆，抬起的右鞋鞋尖仍朝正前方。",
"左脚后承重，右膝前抬，鞋舌、踝与膝盖在同一前后摆动面内。",
"右脚向镜头前伸而自然露底，鞋底长轴近竖直，鞋口仍承接右小腿。",
"右脚前伸、左脚后蹬，鞋底轻微倾斜与整条腿的前向透视一致。",
"右脚继续伸向落点，鞋底角度承接05，未出现独立踝旋转。",
"右脚中央接地，左脚折膝后收，两鞋朝南。",
"右脚压缩承重，左鞋在左小腿下方后收，无向侧方摊开的鞋底。",
"右脚髋下支撑，左鞋和小腿一起略向外投影，未见孤立鞋尖跳转。",
"右脚髋下承重，左脚近体后收，鞋尖朝前，与相邻11前摆相接。",
"右脚后承重、左膝前摆，两鞋中线与膝踝关系清楚。",
"左脚前伸自然见底，鞋底中线在左胫骨下方，无鞋尖横转。",
"左脚继续前伸，鞋底轻斜随整个前腿投影，右支撑鞋朝前。",
"左脚接近下次着地点，鞋掌恢复更正面的角度，膝踝连续。",
"左脚前方接地，右脚后收，鞋口和裤脚连接顺畅。",
"左脚压缩承重，右脚向后折收，首尾过渡仍为同一左脚支撑。"
],
"SW":[
"左脚髋下支撑，右后抬鞋随弯曲小腿向下收，鞋尖未突然外甩。",
"与01同一支撑段，右后鞋近竖直收于踝下，方向衔接稳定。",
"左脚后承重、右膝前摆，鞋尖朝左下，膝踝鞋掌连贯。",
"右脚前摆，鞋尖朝左下并与胫骨前向平面一致。",
"右脚前伸露鞋底，宽鞋头朝左而窄跟朝右下，属前摆透视；未见踝单独外翻。",
"与05同段，右脚鞋底与小腿同向前伸，左后脚继续承重。",
"右脚中央支撑，左后抬鞋在踝下收起，鞋掌近竖直投影，保留自然屈膝。",
"局部重绘后抬左踝和鞋掌，收回原本偏向画面右下的鞋尖；支撑右脚、膝弯与道具保留。",
"局部重绘后抬左鞋，修复08至10之间的鞋尖外甩；保持髋下右支撑点与小腿折收。",
"右脚髋下承重，左后鞋鞋尖向左下，作为09的邻帧鞋轴参考保留。",
"左膝前摆，鞋尖朝左下，右脚后承重，双腿轴向自然。",
"左脚前伸露底，鞋掌长轴与前摆小腿投影一致，不因露底而机械拉直。",
"左脚继续前伸，鞋底宽头朝左、窄跟朝右下，符合西南前摆透视。",
"左前鞋降低接近落点，鞋尖仍向左下，右后脚承重不变。",
"左脚前落地，右腿后折，右后鞋长轴与踝下收方向一致。",
"左脚压缩支撑，右后鞋向下收，16至01朝向衔接稳定。"
]}
rows=[];audits=[]
for d in ["S","SW"]:
 fs=sorted([f for f in inv["frames"] if f["action"]=="run" and f["direction"]==d],key=lambda f:f["frame"])
 assert len(fs)==16
 for f in fs:
  p=R/f["path"]; h=sha(p);assert h==f["sha256"]
  rec=read(R/f["source_record"]);assert rec["export"]["sha256"]==h
  im=Image.open(p);assert im.size==(1024,1024) and im.mode=="RGBA"
  src=R/rec["file"];assert sha(src)==rec["sha256"]
  check={"path":f["path"],"shaMatchesInventory":True,"shaMatchesGenerationExport":True,"nativeShaMatchesRecord":True,"source_record":f["source_record"],"dimensions":[1024,1024],"mode":"RGBA"}
  if "LANCZOS" in rec["export"]["operation"]:
   native=Image.open(src).convert("RGBA").resize((1024,1024),Image.Resampling.LANCZOS)
   check["nativeFullCanvasDownsamplePixelsExact"]=ImageChops.difference(native,im).getbbox() is None
   assert check["nativeFullCanvasDownsamplePixelsExact"]
  for suffix in [".png.generation.json",".generation.json"]:
   scp=p.with_suffix(suffix)
   if scp.exists():
    sc=read(scp);assert sc["sha256"]==h and sc.get("generationRecord")==f["source_record"]
    check.setdefault("sidecars",[]).append(str(scp.relative_to(R)).replace("\\","/"))
  changed=h!=before[f["path"]]["sha256"]
  if changed:
   rec["status"]="generated_exported_video_axis_static_passed"
   rec["visual_status"]="video_axis_static_passed_dynamic_pending_root_review"
   rec["axisReview"]="reviews/video-axis-S-SW-20261004.json"
   save(R/f["source_record"],rec)
   f["visual_status"]="video_axis_static_passed_dynamic_pending_root_review"
  foot="RIGHT" if 7<=f["frame"]<=14 else "LEFT"
  seq=list(range(7,15)) if foot=="RIGHT" else [15,16,1,2,3,4,5,6]
  row={"path":f["path"],"file":f["path"],"sha256":h,"direction":d,"frame":f["frame"],"decision":"replaced" if changed else "retained","reason":reasons[d][f["frame"]-1],"beforeSha256":before[f["path"]]["sha256"],"beforeSourceRecord":before[f["path"]]["source_record"],"source_record":f["source_record"],"supportFoot":foot,"positionPair":seq.index(f["frame"])//2+1,"durationMs":75,"visualReview":"full_resolution_frame_and_adjacent_sequence_static"}
  rows.append(row);audits.append(check)
  f["video_axis_review_status"]="static_passed_dynamic_pending_root_review"
pairs=[]
for d in ["S","SW"]:
 for foot,seq in [("RIGHT",list(range(7,15))),("LEFT",[15,16,1,2,3,4,5,6])]:
  for i in range(4):
   ns=seq[2*i:2*i+2]
   pairs.append({"direction":d,"supportFoot":foot,"positionPair":i+1,"frames":ns,"durationMs":150,"sha256":[next(r["sha256"] for r in rows if r["direction"]==d and r["frame"]==n) for n in ns]})
evidencePaths=[
R.parent.parent/"reference-motion-review-20261004/video-contact.jpg",
R.parent.parent/"reference-motion-review-20261004/character-detail.jpg",
Path("C:/Users/luyua/AppData/Local/Temp/codex-clipboard-7cc4bf22-e4cf-4c35-8ac6-a37fd85f4037.png")]+[R/f"work/video-axis/reference-continuous-{i}.jpg" for i in range(4)]
report={"schemaVersion":1,"reviewedAt":datetime.now(ZoneInfo("America/New_York")).isoformat(),"reviewer":"finish_s_sw","action":"run","directions":["S","SW"],"status":"static_video_axis_review_passed_dynamic_pending_root_review","frameCount":32,"frameMs":75,"cycleMsPerDirection":1200,"frames":rows,"supportPairs":pairs,"knownUnresolvedArtFailures":[],"reviewMethod":"实际查看视频接触表、局部连续采样、NW其他角色问题示例，再逐张查看本角色32张正式全分辨率图，比较相邻膝踝鞋掌轴。","evidence":[{"path":str(p).replace("\\","/"),"sha256":sha(p),"viewed":True,"role":"motion_analysis_only_not_identity"} for p in evidencePaths],"staticEvidence":["work/run-S/run-S-contact-sheet.png","work/run-SW/run-SW-contact-sheet.png","previews/run-S-position-pairs-hit-review.png","previews/run-SW-position-pairs-hit-review.png"],"sourceAudit":audits,"modelEvidence":{"target":"GPT Image 2.5 Sunburst / max","route":"host-managed builtin image_gen","submittedModel":None,"submittedQuality":None,"actualModel":None,"actualQuality":None,"confirmation":"工具无型号或质量选择器，返回未披露，未确认。"},"limits":["视频角色较小且HUD遮挡，参考其摆腿面和鞋向连续性，不据此声称测得关节角度。","该轮子代理完成静态逐图复核；可见浏览器动态复核由主线程统一完成。","客户端未接入。","本报告只对本次S/SW脚轴反馈及已保留两帧支撑段负责。"]}
save(R/"reviews/video-axis-S-SW-20261004.json",report)
for attempt in [1,2]:
 rp=R/f"reviews/run-SW-09-video-axis-20261004-candidate{attempt}.generation.json"
 rec=read(rp);rec["status"]="rejected_candidate_not_imported";rec["formalImport"]=False
 rec["visualReview"]={"verdict":"rejected","reason":"后抬左鞋仍偏向画面右下，未充分解决鞋尖外摆。第3稿正式采用。"}
 save(rp,rec)
save(invp,inv)
print("32 rows source audit passed; replaced:",[(x["direction"],x["frame"]) for x in rows if x["decision"]=="replaced"])
