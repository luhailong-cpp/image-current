from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;T=D.parent;SW=T.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def meta(p):
 im=Image.open(p);return {"file":str(p),"sha256":sha(p),"pixels":list(im.size)}
p=D/"G01.proposal.json";j=json.loads(p.read_text(encoding="utf8"))
base=np.array(Image.open(j["base"]["file"]).convert("RGB"));new=np.array(Image.open(j["proposal"]["file"]).convert("RGB"));l,t,r,b=j["candidateBox"]
mix=np.array(Image.open(D/"G01.premixed.patch.png"));mask=np.array(Image.open(D/"G01.paste-mask.png"))
replay=base.copy();roi=replay[t:b,l:r];roi[mask>0]=mix[mask>0]
assert np.array_equal(replay,new)
edge=[]
for y in [1240,1260,1280,1450,1470,1490]:
 a=new[y,475:535].mean(axis=1);d=a[3:]-a[:-3];x=int(d.argmax()+475+1)
 edge.append({"tileY":y,"brightRightEdgeX":x,"maxThreePixelIntensityJump":round(float(d.max()),2)})
sources={}
for name in ["06-bottom-step-focused","07-bottom-step-width"]:
 h=T/"repairs-resume20261011"/name
 for f in ["receipt.json","generation.json","request.json","prompt.txt"]:
  pp=h/f;dest=D/(name+"."+f);shutil.copyfile(pp,dest);sources[name+"."+f]={"original":str(pp),"snapshot":str(dest),"sha256":sha(pp)}
qa={"schemaVersion":1,"reviewedAtUtc":datetime.now(timezone.utc).isoformat(),"issueId":"G01","status":"LOCAL_GEOMETRY_REUSE_PROPOSAL_PASSES_VISUAL_REVIEW_PARENT_MERGE_PENDING","base":j["base"],"proposal":j["proposal"],"candidateBox":j["candidateBox"],"worldBox":j["worldBox"],"visualFindings":["Lowest stair now reaches upper stair right endpoint around x505; previous x285 premature ending removed.","Tread top, riser front and rounded end meet continuously. Existing red paper retained on the extended front face.","No changed pixels outside [170,1315,560,1522]; all four outside tile edges and every other integrated-v2 repair unchanged.","Native step-end source translated horizontally -168 pixels with zero vertical offset relative to its previous tile placement; no scaling, rotation, warping or program-painted material.","Tiny stone texture and grout irregularities remain baseline quality, not addressed by this geometry-only proposal."],"edgeMeasurements":edge,"geometryCaveat":"Rounded bevel width is several native pixels; x505 is approximate architectural alignment, not a mathematically zero-width drawn line.","nativeOrigin":{"file":str(T/"repairs-resume20261011/07-bottom-step-width/rejected-native.png"),"sha256":j["nativeSource"]["sha256"],"originalToolPath":"C:/Users/luyua/.codex/generated_images/01a12971-38df-7791-a216-b3fcdd2b4460/exec-3253350f-1689-4135-af85-421029d4f149.png","originalRequestPreparedAtUtc":"2026-10-11T05:46:41.719036+00:00","originalOutputReturnedAtUtc":None,"timestampCaveat":"Historical receipt does not include exact tool-return timestamp; not inferred from file time."},"sourceSnapshots":sources,"mechanicalChecks":{"nativeSource1254Square":True,"proposal4096Square":True,"maskReplayPixelIdentical":True,"allOutsideRoiPixelIdentical":True,"allOuterTileEdgesPixelIdentical":True,"resampling":False,"generatedPixelsPaintedByCode":False,"maximumFeatherRadiusPixels":2},"newImageGenCalls":0,"networkGenerationRestoredVerified":False,"noNewGeneratedOutput":"Only historical 07 source reused; no post-restoration generation claimed.","actualModel":None,"actualQuality":None,"internalTileAcceptance":False,"formalAcceptance":False,"pending":["Parent must merge ROI over exact recorded integrated-v2 base and review combined 2x2.","Whole-tile material and remaining guide-pattern issues from previous QA remain open."]}
(D/"G01.qa.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf8")
j["status"]="local-geometry-passes-parent-integration-pending";j["qa"]=str(D/"G01.qa.json");j["qaSha256"]=sha(D/"G01.qa.json");j["nativeReceipt"]=str(D/"07-bottom-step-width.receipt.json");j["nativeReceiptSha256"]=sha(D/"07-bottom-step-width.receipt.json");j["replayVerified"]=True
p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({"edgeMeasurements":edge,"proposal":meta(p) if False else {"file":str(p),"sha256":sha(p)},"qa":{"file":str(D/"G01.qa.json"),"sha256":sha(D/"G01.qa.json")}}))


