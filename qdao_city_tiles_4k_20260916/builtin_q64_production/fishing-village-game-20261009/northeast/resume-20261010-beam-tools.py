"""Resume beam native-only preparation, recording, and QA; never changes selected sources."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import json,hashlib,shutil,datetime,sys
Z=Path(__file__).resolve().parent
PREFIX="resume-20261010-beam"
BOXES={"A":[46405,21940,47659,23194],"B":[47179,21940,48433,23194]}
ORIGIN=[45056,20480]
BASE=Z/"tiles/r06_c12.candidate.png"
BASE_SHA="997d0f2d213d60610c5e92f3314da18efbc93131419ea7dd2167c6c69207ae56"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def write(p,o):
 assert not p.exists(),p
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def ref(p):return {"path":str(p),"sha256":sha(p)}
def boxlocal(g):return [g[0]-ORIGIN[0],g[1]-ORIGIN[1],g[2]-ORIGIN[0],g[3]-ORIGIN[1]]
def base():
 assert sha(BASE)==BASE_SHA
 return Image.open(BASE).copy()
def path(folder,name,suffix):return Z/folder/(PREFIX+"-"+name+suffix)
def source_ref(p):
 r=ref(p)
 for suffix in (".generation.json",".derived.json"):
  rec=Path(str(p)+suffix)
  if rec.exists():r["provenanceRecord"]={"path":str(rec),"sha256":sha(rec)};break
 return r
def derived(p,im,sources,operation,**extra):
 assert not p.exists(),p
 im.save(p)
 write(Path(str(p)+".derived.json"),{"file":str(p),"sha256":sha(p),"pixels":list(im.size),"derivedFrom":sources,"operation":operation,"formalAccepted":False,**extra})
 return ref(p)
def prepare(window,name,prior=None):
 im=base();sources=[{"path":str(BASE),"sha256":BASE_SHA,"nativeGlobalBox":[45056,20480,49152,24576]}]
 if prior:
  rp=Path(prior);r=read(Path(str(rp)+".generation.json"));g=r["nativeGlobalBox"]
  assert sha(rp)==r["sha256"];img=Image.open(rp);assert img.size==(1254,1254)
  im.paste(img,boxlocal(g)[:2]);sources.append(source_ref(rp))
 p=path("guides",name,".png");g=BOXES[window]
 derived(p,im.crop(boxlocal(g)),sources,"Exact integer crop from current 4096 native-core union, optionally with prior native repair opaque-pasted at its recorded world box; no resize, drawing, feather or blend",window=window,nativeGlobalBox=g,sourceCandidateGlobalBox=[45056,20480,49152,24576],candidateCropBox=boxlocal(g),priorRepair=str(prior)if prior else None,configSnapshot=read(Path("D:/work/image/config/image-generation.json")))
 print(json.dumps({"target":str(p),"sha256":sha(p),"box":g}))
def ingest(name,src):
 rp=path("records",name,".receipt.json");pp=path("records",name,".prompt.txt")
 r=read(rp);dest=path("native",name,".png")
 if dest.exists():
  assert sha(dest)==sha(Path(src)),"Existing output differs"
  assert not Path(str(dest)+".generation.json").exists(),"Already recorded"
 else:shutil.copyfile(src,dest)
 im=Image.open(dest);assert im.size==(1254,1254),("Wrong native size; no resampling",im.size)
 target=Path(r["request"]["referenced_image_paths"][3]);tr=read(Path(str(target)+".derived.json"))
 assert pp.read_text(encoding="utf-8-sig")==r["request"]["prompt"]
 refs=[]
 for p,role in zip(r["request"]["referenced_image_paths"],r["referenceRoles"]):
  refs.append({**source_ref(Path(p)),"role":role})
 write(Path(str(dest)+".generation.json"),{"schemaVersion":1,"file":str(dest),"sha256":sha(dest),"generatedAt":None,"observedAtUtc":r["observedAtUtc"],"timeEvidence":"Tool-return observation, not disclosed exact generation time","width":1254,"height":1254,"format":im.format,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":tr["configSnapshot"],"submittedParameters":{"model":None,"quality":None},"submittedModel":None,"submittedQuality":None,"actualModel":None,"actualQuality":None,"unverifiedReason":"Host-managed tool exposes no model/quality selectors; response and PNG metadata disclose neither actual value.","prompt":ref(pp),"receipt":ref(rp),"references":refs,"nativeGlobalBox":tr["nativeGlobalBox"],"source":{**ref(Path(src)),"operation":"Byte-for-byte copy; no transform"},"evidence":{"receipt":str(rp),"metadataKeys":list(im.info),"returnedFields":r["response"]["keys"]},"nativeResizePerformed":False,"usable":False,"formalAccepted":False,"status":"pending_visual_review"})
 print(json.dumps({"native":str(dest),"sha256":sha(dest),"size":list(im.size),"metadataKeys":list(im.info)}))
def qa(name):
 native=path("native",name,".png");r=read(Path(str(native)+".generation.json"))
 target=Path(r["references"][3]["path"]);tr=read(Path(str(target)+".derived.json"))
 combined=base()
 prior=tr.get("priorRepair")
 if prior:
  pr=read(Path(prior+".generation.json"));combined.paste(Image.open(prior),boxlocal(pr["nativeGlobalBox"])[:2])
 g=r["nativeGlobalBox"];x,y=boxlocal(g)[:2];im=Image.open(native);it=Image.open(target)
 combined.paste(im,(x,y))
 sources=[{"path":str(BASE),"sha256":BASE_SHA},source_ref(native)]
 if prior:sources.append(source_ref(Path(prior)))
 out=[]
 for side,box,axis in [("left",(x-128,y-128,x+128,y+1382),"x"),("right",(x+1126,y-128,x+1382,y+1382),"x"),("top",(x-128,y-128,x+1382,y+128),"y"),("bottom",(x-128,y+1126,x+1382,y+1382),"y"),("object",(x,y,x+1254,y+1254),None)]:
  p=path("qa",name+"-"+side,".png")
  out.append({**derived(p,combined.crop(box),sources,"Native integer QA crop of exact opaque reinsertion; no resize, drawing or blend",candidateCropBox=list(box),seamAxis=axis,seamLocalCoordinate=128 if axis else None),"side":side})
 metrics={}
 for side,box in [("left180",(0,0,180,1254)),("right180",(1074,0,1254,1254)),("top180",(0,0,1254,180)),("bottom180",(0,1074,1254,1254))]:
  d=ImageChops.difference(im.crop(box),it.crop(box));metrics[side]={"rgbMAE":ImageStat.Stat(d).mean,"exactEqual":d.getbbox()is None}
 p=path("qa",name,".check.json")
 write(p,{"native":source_ref(native),"nativeGlobalBox":g,"qa":out,"outerMetrics":metrics,"formalAccepted":False,"usable":False,"visualReview":"pending"})
 print(json.dumps({"qa":out,"metrics":metrics}))
if __name__=="__main__":
 cmd=sys.argv[1]
 if cmd=="prepare":prepare(*sys.argv[2:])
 elif cmd=="ingest":ingest(*sys.argv[2:])
 elif cmd=="qa":qa(*sys.argv[2:])

