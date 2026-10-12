from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import json
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
timing=read(R/"animation-timing.json");timing["run"].update(frameMs=60,cycleMs=960,frameDurationsMs=[60]*16)
timing["run"]["latestUserInstruction"]="2026-10-05 direct user: 不是已经改成60ms 一帧了吗; current deliverable uses60ms."
write(R/"animation-timing.json",timing)
for d in ["N","NE","E","SE","S","SW","W","NW"]:
 p=R/f"review/run-{d}-selection.json";s=read(p)
 s["timing"].update(uniformCycleMs=960,frameDurationsMs=[60]*16,frameMs=60,cycleMs=960,latestDirectUserTimingApplied=True)
 for f in s["frames"]:f["durationMs"]=60
 for k in ["frameMs","durationMs"]:
  if k in s:s[k]=60
 for k in ["cycleMs","uniformCycleMs"]:
  if k in s:s[k]=960
 if "frameDurationsMs" in s:s["frameDurationsMs"]=[60]*16
 s["dynamicArtAccepted"]=False
 write(p,s)
 sheet=Image.new("RGB",(1024,1120),"#c6d4d9");draw=ImageDraw.Draw(sheet)
 for j in range(16):
  im=Image.open(R/f"candidate/run/{d}/{j+1:02}.png").resize((256,256),Image.Resampling.LANCZOS)
  x=j%4*256;y=j//4*280;sheet.paste(im,(x,y+24),im);draw.text((x+4,y+4),f"{d}{j+1:02} 60ms",fill="black")
 sheet.save(R/f"preview/run-{d}-selected-256.png")
for rel in ["tools/package_actions.py","tools/write_current_handoff.py","tools/apply_full_axis_revision.py"]:
 p=R/rel;t=p.read_text(encoding="utf-8")
 t=t.replace("16 x 75ms = 1200ms","16 x 60ms = 960ms").replace("16x75ms=1200ms","16x60ms=960ms").replace("75ms","60ms").replace("75 ms","60 ms").replace("1.2秒","0.96秒")
 t=t.replace('"timingUnchanged":','"currentTiming":')
 p.write_text(t,encoding="utf-8")
p=R/"preview/all.html";t=p.read_text(encoding="utf-8").replace("75 ms，完整一圈 1.2 秒","60 ms，完整一圈 0.96 秒");p.write_text(t,encoding="utf-8")
for rel,url in [("preview/nne-review.html","all.html"),("review/south-preview.html","../preview/all.html"),("review/run-EW-position-player.html","../preview/all.html")]:
 (R/rel).write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url='+url+'"><a href="'+url+'">冰剑少女当前全动作预览：跑步60ms/帧，960ms/圈</a>',encoding="utf-8")
write(R/"review/full-axis-timing-update-20261005.json",{"updatedAt":datetime.now(timezone.utc).isoformat(),"source":"latest direct user request in this chat","previousFrameMs":75,"currentFrameMs":60,"runFrames":128,"cycleMs":960,"otherActionTimingUnchanged":True,"historicalAuditTimingPreserved":True,"clientRuntimeVerified":False})
print(json.dumps({"runFrameMs":60,"cycleMs":960,"directions":8}))
