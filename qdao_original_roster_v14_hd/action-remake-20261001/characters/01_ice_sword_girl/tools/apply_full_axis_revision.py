"""Promote only explicitly reviewed current revision sprites; no pose processing."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
approval=read(R/"review/full-axis-approved-native-20261005.json")
assert approval["passed"] and not approval["remainingRequiredRepairs"]
prior=read(R/"review/manifest-before-full-axis-20261005.json")
prior_sha={f["path"]:f["sha256"] for s in prior["sequences"] for f in s["frames"]}
for item in approval["reviewedDrafts"]:
 src=R/item["path"];assert src.resolve().is_relative_to(R)
 assert item["passed"] and sha(src)==item["sha256"]
 g=read(src.with_name(src.name+".generation.json"))
 assert g["sha256"]==item["sha256"]
 with Image.open(src) as im:assert im.size==(1254,1254) and im.mode=="RGBA" and im.getchannel("A").getextrema()==(0,255)
changes=[];groups={}
for item in approval["reviewedDrafts"]:
 a,d,i=item["action"],item["direction"],item["frame"]
 assert a=="run" and 1<=i<=16
 src=R/item["path"];gp=src.with_name(src.name+".generation.json");g=read(gp)
 dst=R/f"candidate/{a}/{d}/{i:02}.png";dgp=dst.with_name(dst.name+".generation.json")
 oldsha=sha(dst);assert oldsha==prior_sha[dst.relative_to(R).as_posix()]
 oldrecord=R/f"sources/reference-history/{oldsha}.generation.json"
 if not oldrecord.exists():oldrecord.write_bytes(dgp.read_bytes())
 assert read(oldrecord)["sha256"]==oldsha
 with Image.open(src) as im:im.resize((1024,1024),Image.Resampling.LANCZOS).save(dst)
 rec={"file":dst.relative_to(R).as_posix(),"sha256":sha(dst),"width":1024,"height":1024,"mode":"RGBA","nativeFrameSize":[1254,1254],
 "derivedFrom":{"file":item["path"],"sha256":g["sha256"],"generationRecord":gp.relative_to(R).as_posix(),"generationRecordSha256":sha(gp)},
 "operation":{"type":"whole_canvas_LANCZOS_downsample","inputSize":[1254,1254],"outputSize":[1024,1024],"translation":[0,0],"crop":None,"alphaFootAlignment":False,"bboxNormalization":False,"mirrored":False,"poseInterpolation":False},
 "actualModel":None,"actualQuality":None,"supersedesExport":{"sha256":oldsha,"generationRecord":oldrecord.relative_to(R).as_posix()},"status":"full_action_axis_revision_selected","clientRuntimeVerified":False}
 write(dgp,rec)
 selpath=R/f"review/{a}-{d}-selection.json"
 s=groups.setdefault((a,d),(selpath,read(selpath)))[1]
 f=s["frames"][i-1];assert f["frame"]==i
 f.update(path=item["path"],sourcePath=item["path"],sha256=g["sha256"],generationRecord=gp.relative_to(R).as_posix(),nativeSize=[1254,1254],candidatePath=dst.relative_to(R).as_posix(),candidateSha256=sha(dst),candidateGenerationRecord=dgp.relative_to(R).as_posix(),notes=item["observations"],staticInspected=True)
 changes.append({"action":a,"direction":d,"frame":i,"file":dst.relative_to(R).as_posix(),"source":item["path"],"oldSha256":oldsha,"sha256":sha(dst),"nativeSha256":g["sha256"]})
for (a,d),(path,s) in groups.items():
 s.update(artStatus="full_action_axis_revision_reviewed",offlineArtworkReviewComplete=True,fullAxisRevision="review/full-axis-revision-selection-20261005.json",remainingRequiredImageRepairs=[],dynamicArtAccepted=False,dynamicArtNote="Final revision visually checked as sequential actual sprites; browser clock/order checked separately. Client playback not verified.")
 write(path,s)
 cell=256;sheet=Image.new("RGB",(cell*4,(cell+24)*4),"#c6d4d9");draw=ImageDraw.Draw(sheet)
 for j in range(16):
  im=Image.open(R/f"candidate/{a}/{d}/{j+1:02}.png").resize((cell,cell),Image.Resampling.LANCZOS);x=j%4*cell;y=j//4*(cell+24)
  sheet.paste(im,(x,y+24),im);draw.text((x+4,y+4),f"{d}{j+1:02} 60ms",fill="black")
 sheet.save(R/f"preview/run-{d}-selected-256.png")
write(R/"review/full-axis-revision-selection-20261005.json",{"createdAt":datetime.now(timezone.utc).isoformat(),"changes":changes,"unchangedFrameCount":196-len(changes),"currentTiming":"run16x60ms=960ms","clientRuntimeVerified":False,"approvalEvidence":{"file":"review/full-axis-approved-native-20261005.json","sha256":sha(R/"review/full-axis-approved-native-20261005.json")}})
print(json.dumps({"changedFrames":len(changes),"unchangedFrames":196-len(changes)}))
