from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
savej=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
ev=read(P/"source-evidence.json")
old=np.array(Image.open(P/"south-crossedge.v1.target.png").convert("RGB"))
native=np.array(Image.open(P/"south-crossedge.v1.native.png").convert("RGB"))
assert old.shape==native.shape==(1254,1254,3)
for s in ev["sources"]:assert sha(s["file"])==s["sha256"]
for r in ev["references"]:assert sha(r["file"])==r["sha256"]
m1=Image.new("L",(1254,1254),0);ImageDraw.Draw(m1).rectangle((614,259,884,289),fill=255)
m2=Image.new("L",(1254,1254),0);d=ImageDraw.Draw(m2);d.line([(495,891),(627,990),(696,1043)],fill=255,width=22,joint="curve");d.ellipse((482,878,508,904),fill=255)
def erode(m):
 z=np.pad(m,1);return z[1:-1,1:-1]&z[:-2,1:-1]&z[2:,1:-1]&z[1:-1,:-2]&z[1:-1,2:]
def fmeta(p):
 im=Image.open(p);return {"file":str(p),"sha256":sha(p),"pixels":list(im.size),"mode":im.mode,"resampled":False}
out=old.copy();patches=[];allmask=np.zeros((1254,1254),bool)
for ident,img in [("S1",m1),("S2",m2)]:
 mask=np.array(img)>0;assert not np.any(mask&allmask);allmask|=mask
 er1=erode(mask);er2=erode(er1)
 alpha=mask.astype(np.float32)*.25+er1.astype(np.float32)*.5+er2.astype(np.float32)*.25
 weighted=np.rint(old*(1-alpha[:,:,None])+native*alpha[:,:,None]).astype(np.uint8)
 out[mask]=weighted[mask]
 ys,xs=np.where(mask);l,t,r,b=int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1
 pp=P/(ident+".preblended.patch.png");mp=P/(ident+".paste-mask.png");ap=P/(ident+".native-alpha.png")
 Image.fromarray(weighted[t:b,l:r]).save(pp);Image.fromarray((mask[t:b,l:r]*255).astype(np.uint8)).save(mp);Image.fromarray(np.rint(alpha[t:b,l:r]*255).astype(np.uint8)).save(ap)
 world=[ev["worldBox"][0]+l,ev["worldBox"][1]+t,ev["worldBox"][0]+r,ev["worldBox"][1]+b]
 tiles=[]
 for tile,ox in [("r11_c05",16384),("r11_c06",20480)]:
  ix0=max(ox,world[0]);ix1=min(ox+4096,world[2]);iy0=world[1];iy1=world[3]
  if ix1>ix0:
   tiles.append({"tile":tile,"worldBox":[ix0,iy0,ix1,iy1],"candidateBox":[ix0-ox,iy0-40960,ix1-ox,iy1-40960],"contextBox":[ix0-ox+115,iy0-40960+115,ix1-ox+115,iy1-40960+115],"patchCrop":[ix0-world[0],0,ix1-world[0],iy1-iy0]})
 patches.append({"id":ident,"targetCropBox":[l,t,r,b],"worldBox":world,"patch":fmeta(pp),"mask":fmeta(mp),"nativeAlpha":fmeta(ap),"maskNonzeroPixelCount":int(mask.sum()),"nativeExactInteriorPixelCount":int(er2.sum()),"maximumFeatherRadiusPixels":2,"applyInstruction":"Patch is already blended. Paste exact RGB bytes only where corresponding paste-mask pixel is nonzero; do NOT alpha-blend this patch again.","tileApplications":tiles})
assert np.array_equal(out[~allmask],old[~allmask])
cand=P/"south-crossedge.v1.proposal-crop.png";Image.fromarray(out).save(cand)
Image.fromarray((allmask*255).astype(np.uint8)).save(P/"combined-mask.png")
for ident,box in [("S1",[580,225,950,325]),("S2",[450,850,730,1085])]:
 Image.fromarray(old).crop(box).save(P/(ident+".qa-before.png"))
 Image.fromarray(out).crop(box).save(P/(ident+".qa-after.png"))
proposal={"schemaVersion":1,"createdAtUtc":datetime.now(timezone.utc).isoformat(),"status":"proposal_pending_parent_visual_review","scope":"Only two P1 dangling paving grooves at south_vertical r11_c05/r11_c06","sourceEvidence":fmeta(P/"south-crossedge.v1.target.png"),"sources":ev["sources"],"sourceWorldBox":ev["worldBox"],"nativeSource":{"file":str(P/"south-crossedge.v1.native.png"),"sha256":sha(P/"south-crossedge.v1.native.png"),"pixels":[1254,1254],"resampled":False,"actualModel":None,"actualQuality":None},"request":{"file":str(P/"south-crossedge.v1.request.json"),"sha256":sha(P/"south-crossedge.v1.request.json")},"receipt":{"file":str(P/"south-crossedge.v1.receipt.json"),"sha256":sha(P/"south-crossedge.v1.receipt.json")},"references":ev["references"],"patches":patches,"resultCrop":fmeta(cand),"outsideMasksPixelExact":True,"totalMaskPixelCount":int(allmask.sum()),"totalCropPixelCount":int(allmask.size),"imageResampling":False,"colorTransform":False,"blur":False,"currentCandidatesModified":False,"contextsModified":False,"formalAccepted":False,"actualModel":None,"actualQuality":None,"replayInstruction":"For each listed tileApplications, crop patch and binary paste-mask with patchCrop; paste masked RGB bytes at candidateBox. Apply the same bytes/mask at contextBox in corresponding context to retain candidate/context equality. For an updated parent candidate, first verify old pixels under masks are unchanged or explicitly rebase these masks."}
savej(P/"overlay-proposal.json",proposal)
receipt=read(P/"south-crossedge.v1.receipt.json");receipt.update({"localNative":proposal["nativeSource"],"dimensionsVerified":True});savej(P/"south-crossedge.v1.receipt.json",receipt)
proposal["receipt"]["sha256"]=sha(P/"south-crossedge.v1.receipt.json");savej(P/"overlay-proposal.json",proposal)
print(json.dumps({"proposal":str(P/"overlay-proposal.json"),"masks":proposal["totalMaskPixelCount"],"patches":[{"id":q["id"],"worldBox":q["worldBox"]} for q in patches]}))

