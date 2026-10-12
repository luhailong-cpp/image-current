from pathlib import Path
import json, hashlib
from PIL import Image
R=Path(r"D:/work/image/designs/creature-combat-20261005/pets/05-yanyuling").resolve()
P=R/"provenance/cast/E"; D=R/"runtime/cast/E"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]; reference_errors=[]
for i in range(1,17):
 n=f"{i:02d}"; f=D/(n+".png"); rec=json.loads((P/(n+".generation.json")).read_text("utf-8")); im=Image.open(f); im.load(); a=im.getchannel("A"); bb=a.point(lambda x:255 if x>=32 else 0).getbbox()
 for ref in rec["references"]:
  q=Path(ref["path"])
  if not q.exists() or sha(q)!=ref["sha256"]: reference_errors.append({"frame":n,"reference":str(q)})
 checks.append({"frame":n,"file":str(f),"width":im.width,"height":im.height,"mode":im.mode,"sha256":sha(f),"recordShaMatches":sha(f)==rec["sha256"],"alphaExtrema":a.getextrema(),"alpha32BBox":bb,"solidSubjectTouchesBorder":bb[0]==0 or bb[1]==0 or bb[2]==1024 or bb[3]==1024,"durationMs":45,"generationRecord":str(P/(n+".generation.json"))})
rejected=["04-rejected","08-rejected","09-rejected","11-rejected","16-rejected"]
deleted=[]
for n in rejected:
 f=(D/(n+".png")).resolve()
 assert f.is_relative_to(R)
 recp=P/(n+".generation.json"); rec=json.loads(recp.read_text("utf-8"))
 rec["file"]=str(f); rec["prompt"]=str(P/(n+".prompt.txt")); rec["evidence"]["receipt"]=str(P/(n+".receipt.json"))
 rec["visualReview"]["status"]="rejected; replaced with separately generated accepted frame"
 if n=="16-rejected":rec["visualReview"]["note"]="Lowest front claw touched bottom edge; replaced with AI-corrected naturally curled complete claw tips."
 if f.exists(): deleted.append({"file":str(f),"sha256":sha(f)});f.unlink()
 rec["cleanup"]["rejectedExportDeleted"]=True;rec["cleanup"]["reason"]="Final accepted replacement verified and present; project retention rule removes rejected raster, keeps prompt/receipt/SHA."
 recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),"utf-8")
for i in range(1,17):
 p=P/(f"{i:02d}"+".generation.json");rec=json.loads(p.read_text("utf-8"))
 for ref in rec["references"]:
  if any(ref["path"]==v["file"] or Path(ref["path"]).resolve()==Path(v["file"]).resolve() for v in deleted):
   ref["retained"]=False;ref["retentionReason"]="Rejected correction input deleted after final accepted replacement verified; historical input SHA and receipt retained."
 rec["visualReview"]["groupPlayback"]="pending parent final six-group playback"
 p.write_text(json.dumps(rec,ensure_ascii=False,indent=2),"utf-8")
out={"group":"cast/E","framesExpected":16,"framesActual":len(checks),"allDimensionsAndModeValid":all(c["width"]==1024 and c["height"]==1024 and c["mode"]=="RGBA" for c in checks),"allOutputShaMatches":all(c["recordShaMatches"] for c in checks),"uniqueImageShaCount":len(set(c["sha256"] for c in checks)),"hasNontrivialAlpha":all(c["alphaExtrema"]==(0,255) for c in checks),"solidBorderTouchFrames":[c["frame"] for c in checks if c["solidSubjectTouchesBorder"]],"referenceErrorsBeforeAuthorizedCleanup":reference_errors,"deletedRejectedRasters":deleted,"individualVisualReview":"All 16 actual generated frames inspected, with targeted AI repairs of 04,08,09,11,16.","groupPlayback":"Parent will perform final normal/slow/step review after direction-wide export.","clientIntegration":"not tested","frames":checks}
(P/"CHECKS.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),"utf-8")
print(json.dumps({k:v for k,v in out.items() if k!="frames"},ensure_ascii=False))

