from pathlib import Path
from datetime import datetime
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parents[1]
choices={
"NE":["01-v3","02-v1","03-midstance-v1","04-ground4-v1","05-paired-v1","06-groundlevel-v1","07-paired-v1","08-paired-v1","09-v3","10-v1","11-groundtrack-v1","12-groundtrack-v1","13-groundtrack-v1","14-groundtrack-v1","15-groundtrack-v1","16-groundtrack-v1"],
"S":["01-v2","02-v1","03-v1","04-v2","05-paired-v1","06-paired-v1","07-paired-v1","08-paired-v1","09-v1","10-v2","11-v1","12-v2","13-paired-v1","14-paired-v1","15-progression-v1","16-paired-v1"]}
# Visual estimates on native 1254 canvas, not algorithmic placement or ground pinning.
points={"NE":[[715,1180],[715,1185],[655,1165],[580,1166],[575,1163],[545,1180],[485,1166],[510,1172],[540,1149],[565,1164],[425,1181],[405,1171],[365,1183],[390,1170],[380,1206],[345,1208]],
"S":[[598,1177],[598,1189],[580,1195],[570,1140],[575,1139],[585,1128],[570,1143],[570,1095],[650,1181],[650,1187],[640,1186],[690,1182],[695,1160],[675,1140],[725,1142],[685,1110]]}
stamp=datetime.now().astimezone().isoformat()
for d,names in choices.items():
 p=B/f"review/run-{d}-sequence-input.json"; data=json.loads(p.read_text(encoding="utf-8-sig"))
 data["reviewedOn"]="2026-10-04";data["updatedAt"]=stamp
 data["events"]=[{"name":"right_contact","frame":1,"timeMs":0,"status":"candidate_observed"},{"name":"right_final_push","frame":8,"timeMs":525,"status":"candidate_observed"},{"name":"left_contact","frame":9,"timeMs":600,"status":"candidate_observed"},{"name":"left_final_push","frame":16,"timeMs":1125,"status":"candidate_observed"}]
 data.pop("contactEvents",None)
 rows=[]
 for i,n in enumerate(names):
  foot="right" if i<8 else "left";side="右" if i<8 else "左";phase=(i%8)//2
  desc=["前段接地与压缩承重","身体下方经过支撑","略后方持续支撑，另一腿向前回收","后段持续支撑，准备交替另一腿"][phase]
  if d=="NE":detail="支撑鞋随后移保持东北鞋尖轴；空中脚允许露鞋底"
  else:detail="支撑鞋保持正前方鞋轴，后移以透视深度表现"
  src=B/f"generation/{d}/{n}.png";h=hashlib.sha256(src.read_bytes()).hexdigest()
  fr=data["frames"][i];fr.update(source=f"generation/{d}/{n}.png",sourceSha256=h,observedPhase=f"{side}脚{desc}；{detail}",issues=[],durationMs=75,startMs=i*75,supportFoot=foot,positionPair=phase+1)
  im=Image.open(src)
  row={"frame":i+1,"source":fr["source"],"sourceSha256":h,"supportFoot":foot,"groundedObserved":True,"positionPair":phase+1,"observedPhase":fr["observedPhase"],"shoeContactApproxNative":points[d][i],"measurement":"human visual estimate, +/-20 native pixels, same canvas; never applied as alignment","supportType":"full_foot_or_low_heel" if phase<3 else "late_stance_forefoot_or_low_heel","imageViewed":True,"visualAcceptance":False}
  rows.append(row)
  recp=src.with_name(src.stem+".review.json");recp.write_text(json.dumps(dict(row,reviewedAt=stamp,status="selected_current_candidate"),ensure_ascii=False,indent=2),encoding="utf-8")
 data["issues"]=["本轮按连续同脚支撑重画，所有16张独立实图；未以复制帧或画布平移补接地。","位置两帧一组，组内允许膝踝压缩；末对仍为低跟后支撑，最终游戏连播体验待用户查看。"]
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
 matrix={"direction":d,"reviewedAt":stamp,"criterion":"same support foot across four progressive position pairs; 75ms each","groundedFrames":{"right":list(range(1,9)),"left":list(range(9,17))},"frames":rows,"visualAcceptance":False,"clientAccepted":False,"remaining":["actual client playback untested","pair boundaries and final toe push need user visual review"]}
 (B/f"review/run-{d}-paired-support-matrix.json").write_text(json.dumps(matrix,ensure_ascii=False,indent=2),encoding="utf-8")
 sheet=Image.new("RGB",(1280,1440),(239,239,236));dr=ImageDraw.Draw(sheet);anim=[]
 for i,n in enumerate(names):
  im=Image.open(B/f"generation/{d}/{n}.png").convert("RGBA")
  th=im.resize((310,310),Image.Resampling.LANCZOS);x=(i%4)*320;y=(i//4)*360
  sheet.paste(th,(x,y+35),th);dr.text((x+5,y+5),f"{d}{i+1:02d} {n}",fill=(10,10,10))
  anim.append(im.resize((512,512),Image.Resampling.LANCZOS))
 sheet.save(B/f"review/run-{d}-paired-final-contact.jpg")
 anim[0].save(B/f"review/run-{d}-paired-trial.apng",save_all=True,append_images=anim[1:],duration=75,loop=0,disposal=2)
print("Updated NE/S selections and source-hashed observed support matrices; full build still pending.")

