from pathlib import Path
import json, hashlib, sys
from datetime import datetime, timezone
from PIL import Image, ImageDraw
BASE=Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def dump(p,obj): Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
direction=sys.argv[1]
assert direction in ("E","W")
observations=load(BASE/f"review/run-{direction}-continuous-support-observations.json")
path=BASE/f"review/run-{direction}-sequence-input.json"
data=load(path); before_sha=sha(path)
old={int(f.get("slot",f.get("frame"))):f for f in data["frames"]}
floor=1164 if direction=="E" else 1179
first="right" if direction=="E" else "left"
other="left" if first=="right" else "right"
events=[]
for foot,start in [(first,1),(other,9)]:
 for name,slot in [("contact",start),("late_push",start+6),("final_push",start+7)]:
  events.append({"name":foot+"_"+name,"frame":slot,"timeMs":(slot-1)*75,"status":"candidate_observed","contactPersistsThroughFrame":start+7})
rows=[]
for entry in observations["frames"]:
 n=entry["slot"]; f=old[n]; source=(BASE/entry.get("source",f["source"])).resolve()
 im=Image.open(source); a=im.getchannel("A")
 assert im.size==(1254,1254) and im.mode=="RGBA"
 bounds=a.point(lambda v:255 if v>8 else 0).getbbox()
 roi=entry.get("supportShoeRoi")
 if roi:
  box=a.crop(tuple(roi)).point(lambda v:255 if v>8 else 0).getbbox()
  y=roi[1]+box[3]-1
 else: y=entry.get("supportBottomY",bounds[3]-1)
 x=entry["supportCenterX"]
 support=first if n<=8 else other; pair=((n-1)%8)//2+1
 issues=entry.get("issues",f.get("issues",[]))
 f.update({"frame":n,"slot":n,"source":source.as_posix(),"sourceSha256":sha(source),
 "sourceGenerationRecord":source.as_posix()+".generation.json","sourceDimensions":[1254,1254],
 "observedPhase":entry["observedPhase"],"issues":issues,"durationMs":75,"startMs":(n-1)*75,
 "supportFoot":support,"positionPair":pair,"continuousSupportCandidate":True,
 "footAxis":"screen_right" if direction=="E" else "screen_left",
 "manualContactPointNative":[x,y],"footPoint":[x,y],
 "contactPointMeaning":"人工确认支撑鞋及ROI；x为鞋中心约测，y为该ROI alpha>8最低占用像素。仅画布诊断，非世界地面/客户端验收；无对齐变换。",
 "nativeCanvas":[1254,1254],"alphaGt8Bounds":list(bounds),"nativeBoundsAlphaGt8":list(bounds),
 "diagnosticLowestShoeY":y,"diagnosticFloorClearance":floor-y,
 "visualAccepted":False,"clientAccepted":False})
 for stale in ("sha256","file","generationRecord","exportTransform"): f.pop(stale,None)
 review={"schemaVersion":1,"direction":direction,"slot":n,"source":source.as_posix(),
 "sourceSha256":sha(source),"reviewedAt":datetime.now(timezone.utc).isoformat(),"inspection":"实际查看全原生图；鞋轴、支撑腿归属、相邻空间顺序人工检查；不是浏览器动态或客户端验收",
 "observedPhase":f["observedPhase"],"supportFoot":support,"positionPair":pair,
 "supportShoeRoi":roi,"manualContactPointNative":[x,y],"diagnosticFloorDelta":y-floor,
 "native":list(im.size),"mode":im.mode,"alphaExtrema":list(a.getextrema()),
 "actualModel":None,"actualQuality":None,"issues":issues,"selectedAsCandidate":True,
 "visualAccepted":False,"clientAccepted":False,"alignmentApplied":False}
 dump(BASE/f"review/run-{direction}-continuous-slot-{n:02d}.json",review)
 rows.append(f)
data.update({"action":"run","direction":direction,"status":"candidate_not_accepted","visualAccepted":False,
"clientAccepted":False,"clientTested":False,"reviewedOn":"2026-10-04","durationMs":1200,
"timing":{"frameMs":75,"trialCycleMs":1200,"offlineDefaultCycleMs":1200,"mode":"uniform","selectedProductionCycleMs":None},
"timingBasis":"用户要求16张独立姿态×75ms；每脚连续8张、四个空间位置每处2张；未延长单帧或复制插值",
"events":events,"frames":rows,"issues":observations["groupIssues"],
"supportSequence":{"firstHalf":{"foot":first,"frames":list(range(1,9))},"secondHalf":{"foot":other,"frames":list(range(9,17))},"positionPairs":["front_contact_compression","under_body_mid_support","slightly_behind_weighted","rear_late_support"],"alignmentApplied":False}})
assert sorted(f["slot"] for f in rows)==list(range(1,17))
assert sum(f["durationMs"] for f in rows)==1200
assert len(set(f["sourceSha256"] for f in rows))==16
assert all(Path(f["sourceGenerationRecord"]).is_file() for f in rows)
dump(path,data)
matrix={"schemaVersion":1,"direction":direction,"input":path.as_posix(),"inputSha256":sha(path),"priorInputSha256":before_sha,
"builtAt":datetime.now(timezone.utc).isoformat(),"durationMs":1200,"frameDurationMs":75,
"sameFootSupportCandidates":[{"foot":first,"slots":list(range(1,9))},{"foot":other,"slots":list(range(9,17))}],
"rows":[{k:f[k] for k in ("slot","source","sourceSha256","supportFoot","positionPair","observedPhase","manualContactPointNative","diagnosticFloorClearance","durationMs","issues")} for f in rows],
"events":events,"checks":{"16UniqueSourceHashes":True,"16Native1254Rgba":True,"16GenerationRecords":True,"duration1200":True,"uniform75":True,"noImageTransformApplied":True},
"visualAccepted":False,"clientAccepted":False,"issues":observations["groupIssues"]}
dump(BASE/f"review/run-{direction}-continuous-support-matrix.json",matrix)
sheet=Image.new("RGB",(1280,1440),(236,232,225));d=ImageDraw.Draw(sheet)
for i,f in enumerate(rows):
 x=(i%4)*320;y=(i//4)*360
 img=Image.open(f["source"]);thumb=img.resize((312,312),Image.Resampling.LANCZOS)
 sheet.paste(thumb,(x+4,y+28),thumb);d.text((x+8,y+6),f'{direction}{i+1:02} {f["supportFoot"]} pair{f["positionPair"]} 75ms',fill=(30,30,30))
 d.text((x+8,y+340),f'shoe {f["manualContactPointNative"]} candidate',fill=(30,30,30))
sheet.save(BASE/f"review/run-{direction}-continuous-support-contact.jpg",quality=92)
print(json.dumps({"input":str(path),"inputSha256":sha(path),"sourceCount":len(rows),"durationMs":1200,"matrix":f"review/run-{direction}-continuous-support-matrix.json"},ensure_ascii=False))
