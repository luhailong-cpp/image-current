"""Final technical verification of material delivery; never substitutes for visual review."""
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
rd=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sel=rd(R/"selection.json");mf=rd(R/"merge-manifest.json");st=rd(R/"STATUS.json")
assert len(sel["frames"])==len(mf["files"])==196 and len(list((R/"runtime").rglob("*.png")))==196
assert st["offlineMaterialComplete"] and mf["offlineMaterialComplete"]
assert st['axisReviewed'] and mf['axisReviewed']
assert st['fullBodyReviewed'] and mf['fullBodyReviewed']
prior=rd(R/"provenance/grounding4-prior-selection.json")
old={(f["action"],f["direction"],f["frame"]):f for f in prior["frames"]}
fm={(f["action"],f["direction"],f["frame"]):f for f in mf["files"]}
combat=0
for f in sel["frames"]:
 k=(f["action"],f["direction"],f["frame"]);p=R/f["source"];r=rd(R/f["generationRecord"]);m=fm[k]
 assert sha(p)==f["sourceSha256"]==r["sha256"]==m["sha256"],p
 assert sha(R/f["generationRecord"])==m["generationRecordSha256"]
 with Image.open(p) as im:assert im.size==(1024,1024) and im.mode=="RGBA" and im.getchannel("A").getextrema()==(0,255)
 origin=f["nativeOrigin"]
 assert min(origin["nativeSize"])>=1024
 assert (R/origin["generationRecord"]).exists()
 assert sha(R/origin["generationRecord"])==origin["generationRecordSha256"],origin["generationRecord"]
 if f["action"]!="run":
  assert f["sourceSha256"]==old[k]["sourceSha256"];combat+=1
assert combat==68
timings={"run":(16,60),"hit":(6,40),"attack":(12,30),"cast":(16,45)}
groups=[]
for g in mf["groups"]:
 count,ms=timings[g["action"]];assert g["count"]==count and g["loopMs"]==count*ms
 assert len({f["sha256"] for f in g["frames"]})==count
 for speed,mul in [("normal",1),("slow",4)]:
  p=R/f"preview/{g['action']}-{g['direction']}-{speed}.png"
  with Image.open(p) as im:
   assert im.n_frames==count,(p,im.n_frames)
   durations=[]
   for i in range(count):im.seek(i);durations.append(im.info.get("duration"))
   assert durations==[ms*mul]*count,(p,durations)
 groups.append({"action":g["action"],"direction":g["direction"],"frames":count,"frameMs":ms,"loopMs":count*ms,"uniqueImages":count,"normalAndSlowAPNG":"passed"})
for name,ms in [("960ms",60),("slow",240)]:
 p=R/f"preview/run-eight-directions-{name}.png"
 with Image.open(p) as im:
  assert im.n_frames==16
  for i in range(16):im.seek(i);assert im.info["duration"]==ms
assert rd(R/"provenance/run-playback-uniform-check.json")["checks"]["timingBoundaries"]["passed"]
result={"verifiedAt":datetime.now(timezone.utc).isoformat(),"passed":True,"runtimeRGBA1024":196,"nativeInputsAtLeast1024":196,"groups":groups,"combatByteIdenticalToPrior":68,"allRuntimeAndRecordHashesMatchManifest":True,"sourceRecordHashesVerified":196,"newRunImageCounts":rd(R/"provenance/grounding-pairs-applied.json")["counts"],"runNormalLoopMs":960,"extraEndPauseMs":0,"browserVisualReview":"provenance/offline-visual-review.json","imageCleanup":"provenance/grounding-pairs-image-cleanup.json" if (R/"provenance/grounding-pairs-image-cleanup.json").exists() else "pending","clientIntegrated":False,"clientValidation":"not_run","userFinalAcceptance":False}
(R/"provenance/final-verification.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
result['fullBodyEdits']=rd(R/'provenance/full-body-edits-applied.json')['count']
result['fullBodyRetained']=196-result['fullBodyEdits']
result['fullBodyReviewed']=True
result['axisRevision']='2026-10-04_knee_ankle_boot'
result['axisEdits']=rd(R/'provenance/axis-edits-applied.json')['count']
result['axisRunRetained']=rd(R/'provenance/axis-edits-applied.json')['retainedRun']
(R/"provenance/final-verification.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k!="groups"},ensure_ascii=False))
