from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
prop=read(P/"overlay-proposal.json");ev=read(P/"source-evidence.json")
S=P.parent.parent
corePaths={"r11_c05":S/"r11_c05/refinement-resume20261010/integrated-v2/r11_c05.repaired-v2.candidate.png","r11_c06":S/"r11_c06/pipeline/output/94ddb3ea62a89ee2/r11_c06.candidate.png"}
cores={t:np.array(Image.open(p).convert("RGB")) for t,p in corePaths.items()}
contextPaths={t:p.with_name(p.stem+".context.png") for t,p in corePaths.items()}
contexts={t:np.array(Image.open(p).convert("RGB")) for t,p in contextPaths.items()}
checks=[]
for src in ev["sources"]:checks.append({"file":src["file"],"unchanged":sha(src["file"])==src["sha256"]})
assert all(c["unchanged"] for c in checks)
for q in prop["patches"]:
 patch=np.array(Image.open(q["patch"]["file"]).convert("RGB"));mask=np.array(Image.open(q["mask"]["file"]))>0
 for a in q["tileApplications"]:
  x0,y0,x1,y1=a["candidateBox"];l,t,r,b=a["patchCrop"];view=cores[a["tile"]][y0:y1,x0:x1];view[mask[t:b,l:r]]=patch[t:b,l:r][mask[t:b,l:r]]
 q["contextApplications"]=[]
 wx0,wy0,wx1,wy1=q["worldBox"]
 for tile,ox in [("r11_c05",16384),("r11_c06",20480)]:
  ix0=max(ox-115,wx0);ix1=min(ox+4211,wx1)
  iy0=max(40960-115,wy0);iy1=min(40960+4211,wy1)
  if ix1<=ix0 or iy1<=iy0:continue
  box=[ix0-ox+115,iy0-40960+115,ix1-ox+115,iy1-40960+115]
  crop=[ix0-wx0,iy0-wy0,ix1-wx0,iy1-wy0]
  q["contextApplications"].append({"tile":tile,"worldBox":[ix0,iy0,ix1,iy1],"contextBox":box,"patchCrop":crop,"includesAnyHalo":ix0<ox or ix1>ox+4096,"sourceContext":{"file":str(contextPaths[tile]),"sha256":sha(contextPaths[tile])}})
  x0,y0,x1,y1=box;l,t,r,b=crop
  view=contexts[tile][y0:y1,x0:x1];view[mask[t:b,l:r]]=patch[t:b,l:r][mask[t:b,l:r]]
for tile in cores:assert np.array_equal(cores[tile],contexts[tile][115:4211,115:4211])
rejoined=np.concatenate([cores["r11_c05"][1453:2707,3469:4096],cores["r11_c06"][1453:2707,:627]],1)
target=np.array(Image.open(prop["resultCrop"]["file"]).convert("RGB"))
assert np.array_equal(rejoined,target)
prop["replayInstruction"]="For candidate edits use tileApplications. For context edits use the separate contextApplications, which include all intersecting 115px outer halo copies as well as each core. For every entry, crop preblended RGB patch AND binary paste-mask by patchCrop and copy exact RGB bytes wherever mask is nonzero to candidateBox/contextBox. Do NOT alpha-blend again. An updated parent output can accept these overlays only after checking old masked pixels remain equal to the recorded source or an explicit rebase. Context core must equal its candidate after edits."
prop["localVisualReview"]={"S1GeometryPassed":True,"S2GeometryPassed":True,"additionalBranchesAdded":False,"S1Method":"Removed the unsupported west-facing 247 px spur; preserved the east-facing horizontal line and pre-existing vertical joint at its proper T termination.","S2Method":"Connected existing lower-right diagonal back to existing main diagonal with one approximately 125 px missing segment. Narrow native strip extends beyond old stump to obtain a clean join.","outsideMasksExact":True,"broadMaterialCorrectionAttempted":False,"crossEdgeFullPassClaimed":False,"reason":"Residual broader stone colour/texture mismatch remains outside the two geometry ROIs."}
save(P/"overlay-proposal.json",prop)
report={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"status":"passed_mechanical_replay_and_local_geometry_review","sourceChecks":checks,"candidateAndContextCoreEqualAfterSimulatedApply":True,"rejoinedCandidateCropEqualsProposalPixels":True,"sourceCurrentCandidatesWritten":False,"sourceContextsWritten":False,"nativeCalls":1,"rejectedNativeCalls":0,"actualNativePixels":[1254,1254],"patchCount":2,"affectedMaskPixels":prop["totalMaskPixelCount"],"sourceResampling":False,"outsideMasksExact":True,"actualModel":None,"actualQuality":None,"formalAccepted":False,"qaImages":[str(P/"S1.qa-before.png"),str(P/"S1.qa-after.png"),str(P/"S2.qa-before.png"),str(P/"S2.qa-after.png")],"proposalSha256":sha(P/"overlay-proposal.json")}
save(P/"replay-verification.json",report)
print(json.dumps({"verification":str(P/"replay-verification.json"),"replayPassed":True,"contextHaloApplicationsRecorded":True}))

