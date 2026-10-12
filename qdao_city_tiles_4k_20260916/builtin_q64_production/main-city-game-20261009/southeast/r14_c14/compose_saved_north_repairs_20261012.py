import json,hashlib,datetime,sys
from pathlib import Path
import numpy as np
from PIL import Image
d=Path(sys.argv[1]);t=d.parent.parent;s=t.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{"path":str(p),"sha256":sha(p)}
prep=json.loads((d/"preparation.json").read_text())
bi=prep.get("baseCandidate",prep.get("sourceCandidate"));ni=prep.get("northCore",prep.get("neighborCore"))
for obj in [bi,ni,prep["alpha"]]:assert sha(obj["path"])==obj["sha256"]
basep=Path(bi["path"]);northp=Path(ni["path"])
npth=d/"repair-native-1254.png";gen=json.loads((d/"repair-native-1254.png.generation.json").read_text());assert sha(npth)==gen["sha256"]
assert gen["actualModel"] is None and gen["actualQuality"] is None
if t.name=="r14_c15":
 context=t/"repairs/single-stone-railing-bottom-20261012-v3/context-4326.png"
 parentmanifest=t/"repairs/single-stone-railing-bottom-20261012-v3/composition.json"
 joined_x=0
else:
 context=t/"candidate/r14_c14-context-west-material-composed-v1-20261012.png"
 parentmanifest=t/"repairs/west-material-major-20261012T123237-50414b22/preparation.json"
 joined_x=2842
old=np.array(Image.open(basep).convert("RGB"));new=np.array(Image.open(npth).convert("RGB"));assert new.shape==(1254,1254,3)
a=np.array(Image.open(prep["alpha"]["path"]).convert("L"),dtype=np.uint32)
nc=prep["nativeCrop"];pb=prep["pasteBoxIn4096"];x0,y0,x1,y1=pb
sample=new[nc[1]:nc[3],nc[0]:nc[2]].astype(np.uint32);assert sample.shape[:2]==a.shape
comp=old.copy();comp[y0:y1,x0:x1]=((old[y0:y1,x0:x1].astype(np.uint32)*(255-a[:,:,None])+sample*a[:,:,None]+127)//255).astype(np.uint8)
cp=d/"candidate-4096.png";assert not cp.exists();Image.fromarray(comp).save(cp)
ctx=np.array(Image.open(context).convert("RGB"));assert np.array_equal(ctx[115:4211,115:4211],old)
ctx[115:4211,115:4211]=comp;cx=d/"context-4326.png";Image.fromarray(ctx).save(cx)
changed=np.any(comp!=old,axis=2);ys,xs=np.where(changed)
# Independent replay uses scalar Python integer arithmetic for only adopted pixels.
replay=Image.open(basep).convert("RGB");rp=replay.load();sp=Image.open(npth).convert("RGB").load()
al=Image.open(prep["alpha"]["path"]).convert("L").load()
for yy in range(y1-y0):
 for xx in range(x1-x0):
  av=al[xx,yy]
  if av:
   oo=rp[x0+xx,y0+yy];nn=sp[nc[0]+xx,nc[1]+yy]
   rp[x0+xx,y0+yy]=tuple((oo[c]*(255-av)+nn[c]*av+127)//255 for c in range(3))
assert np.array_equal(np.array(replay),comp)
fullalpha=np.zeros((4096,4096),bool);fullalpha[y0:y1,x0:x1]=a>0;assert not changed[~fullalpha].any()
if t.name=="r14_c14":assert np.array_equal(comp[:630,:630],old[:630,:630])
north=Image.open(northp).convert("RGB");joined=Image.new("RGB",(1254,1254));joined.paste(north.crop((joined_x,3456,joined_x+1254,4096)),(0,0));joined.paste(Image.fromarray(comp).crop((joined_x,0,joined_x+1254,614)),(0,640))
jp=d/"composed-core-join-native-1254.png";joined.save(jp)
qa=[{"path":str(jp),"sha256":sha(jp),"pixels":[1254,1254],"role":"fixed north640 plus actual candidate614, no halo"}]
def emit(name,im,box,role):
 f=d/(name+".png");im.crop(box).save(f);qa.append({"path":str(f),"sha256":sha(f),"pixels":[box[2]-box[0],box[3]-box[1]],"cropBoxInJoined1254":list(box),"role":role,"resized":False})
if t.name=="r14_c15":
 for name,box in [("top-boundary-100pct",(0,480,512,840)),("bottom-boundary-100pct",(66,608,398,896)),("left-boundary-100pct",(66,560,322,880)),("right-boundary-100pct",(142,560,398,880))]:emit(name,joined,box,"all saved-alpha boundary context, native pixels")
else:
 for k in range(3):
  emit("fixed-core-boundary-q"+str(k)+"-100pct",joined,(k*418,384,(k+1)*418,896),"fixed north-core join")
  emit("shaped-bottom-boundary-q"+str(k)+"-100pct",joined,(k*418,640,(k+1)*418,1000),"shaped alpha lower edge")
 emit("left-endpoint-100pct",joined,(0,512,420,1012),"x2842 context and adoption starts x2874")
 east=s/"r14_c15/repairs/single-stone-railing-bottom-20261012-v3/candidate-4096.png"
 eastim=Image.open(east).convert("RGB");ej=Image.new("RGB",(512,1024));ej.paste(Image.fromarray(comp).crop((3840,0,4096,1024)),(0,0));ej.paste(eastim.crop((0,0,256,1024)),(256,0));ep=d/"east-core-join-q0-100pct.png";ej.save(ep);qa.append({"path":str(ep),"sha256":sha(ep),"pixels":[512,1024],"role":"candidate east256 + r14c15 west256 true cores, y0..1024","eastNeighbor":info(east),"resized":False})
verification={"replayedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"independentScalarReplayExact":True,"candidateContextCoreExact":True,"outsideSavedAlphaUnchanged":True,"northCoreUnmodified":True,"nativeOriginalByteCopyVerified":True,"frozenNW630Unchanged":True if t.name=="r14_c14" else "not applicable to this tile","changedPixels":int(changed.sum()),"actualChangeBox":[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],"formalAccepted":False}
vp=d/"replay-verification.json";vp.write_text(json.dumps(verification,indent=2)+"\n")
manifest={"schemaVersion":1,"tile":t.name,"version":d.name,"composedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"sourceCandidate":bi,"sourceContext":info(context),"northCore":ni,"native":info(npth),"generationRecord":info(d/"repair-native-1254.png.generation.json"),"receipt":info(d/"receipt.json"),"preparation":info(d/"preparation.json"),"request":info(d/"request.json"),"prompt":info(d/"prompt.txt"),"alpha":prep["alpha"],"nativeCrop":nc,"pasteBoxIn4096":pb,"blendArithmetic":"(old*(255-alpha)+new*alpha+127)//255 uint32","resampling":False,"RGBColorCorrection":False,"candidate":info(cp),"context":info(cx),"compositor":info(Path(__file__)),"replay":info(vp),"verification":verification,"QAImages":qa,"status":"unpublished_trial_pending_visual_review","formalAccepted":False}
mp=d/"composition.json";mp.write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"candidate":info(cp),"manifest":info(mp),"verification":verification,"QAImages":len(qa)}))
