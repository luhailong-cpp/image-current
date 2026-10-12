"""Import one built-in junction result; exact 2x2 replacement and unscaled QA only."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import json,hashlib,shutil,datetime
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def save(p,o):
 assert not p.exists(),p
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def ref(p):
 r=Path(str(p)+".generation.json")
 if not r.exists():r=Path(str(p)+".derived.json")
 return {"path":str(p),"sha256":sha(p),"sourceRecord":str(r)}
def derived(p,im,sources,op,**kw):
 assert not p.exists(),p
 im.save(p)
 save(Path(str(p)+".derived.json"),{"file":str(p),"sha256":sha(p),"pixels":list(im.size),"derivedFrom":sources,"operation":op,"formalAccepted":False,**kw})
 return {"path":str(p),"sha256":sha(p),"pixels":list(im.size),"provenanceRecord":str(p)+".derived.json",**kw}
target=Z/"guides/junction-r2c2-target.png";tr=read(Path(str(target)+".derived.json"))
combined=Image.new("RGB",(2278,2278))
for s in tr["derivedFrom"]:
 p=Path(s["path"]);assert sha(p)==s["sha256"] and sha(Path(s["sourceRecord"]["path"]))==s["sourceRecord"]["sha256"]
 im=Image.open(p);assert im.size==(1254,1254)
 combined.paste(im.crop(s["sourceBox"]),s["targetBoxInCombined"][:2])
source=Path(r"C:\Users\luyua\.codex\generated_images\01a1216d-bec0-72a3-ae22-ba97f839ea1e\exec-c688f1c4-19fc-41e6-b3b5-ec9e2a959e1f.png")
native=Z/"native/junction-r2c2-v1.png";assert not native.exists();shutil.copyfile(source,native)
im=Image.open(native);assert im.size==(1254,1254),("size mismatch, no resize",im.size)
pp=Z/"records/junction-r2c2-v1.prompt.txt";rp=Z/"records/junction-r2c2-v1.receipt.json";r=read(rp)
assert pp.read_text(encoding="utf-8-sig")==r["request"]["prompt"]
roles=["authoritative full-map layout only","materials/style only, not a coordinate crop","primary approved Q Daoist painting style only; no UI/night/people copied","sole native 2x2-junction edit target; center(627,627); correct support rail and dark wall while preserving floor and outer180"]
refs=[{"path":p,"sha256":sha(Path(p)),"role":roles[i]}for i,p in enumerate(r["request"]["referenced_image_paths"])]
refs[-1]["provenance"]=[{"path":str(target)+".derived.json","sha256":sha(Path(str(target)+".derived.json"))}]
save(Path(str(native)+".generation.json"),{"schemaVersion":1,"file":str(native),"sha256":sha(native),"generatedAt":None,"observedAtUtc":r["observedAtUtc"],"timeEvidence":"Tool result observation; generation timestamp undisclosed","width":1254,"height":1254,"format":im.format,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":tr["configSnapshot"],"submittedParameters":{"model":None,"quality":None},"submittedModel":None,"submittedQuality":None,"actualModel":None,"actualQuality":None,"unverifiedReason":"Host-managed tool exposes no model/quality selector; response and PNG metadata disclose neither actual value.","prompt":{"path":str(pp),"sha256":sha(pp)},"receipt":{"path":str(rp),"sha256":sha(rp)},"references":refs,"evidence":{"receipt":str(rp),"pngMetadataKeys":list(im.info),"returnedFields":r["response"]["keys"]},"source":{"path":str(source),"sha256":sha(source),"operation":"byte-for-byte copy, no transform"},"nativeGlobalBox":tr["nativeGlobalBox"],"dimensionValidation":{"expected":[1254,1254],"actual":list(im.size),"passed":True},"nativeResizePerformed":False,"usableNative":False,"formalAccepted":False,"status":"single_attempt_junction_pending_QA"})
combined.paste(im,(512,512))
sources=tr["derivedFrom"]+[ref(native)]
candidates=[]
for patch,box,gb in [
 ("p22",(0,0,1254,1254),[45965,21389,47219,22643]),
 ("p23",(1024,0,2278,1254),[46989,21389,48243,22643]),
 ("p32",(0,1024,1254,2278),[45965,22413,47219,23667]),
 ("p33",(1024,1024,2278,2278),[46989,22413,48243,23667])]:
 p=Z/"native"/("junction-r2c2-"+patch+"-candidate.png")
 candidates.append(derived(p,combined.crop(box),sources,"Native 1:1 quadrant composition, opaque replacement at (512,512) with unscaled AI result, then 1254 crop; no blend/drawing/resample",patchId="r06_c12_"+patch,nativeGlobalBox=gb,combinedNativeGlobalBox=tr["combinedNativeGlobalBox"],replacementGlobalBox=tr["nativeGlobalBox"],cropFromCombined=list(box),status="pending_QA",usable=False))
qa=[]
for name,box,axis in [
 ("outer-left",(384,384,640,1894),"x"),
 ("outer-right",(1638,384,1894,1894),"x"),
 ("outer-top",(384,384,1894,640),"y"),
 ("outer-bottom",(384,1638,1894,1894),"y"),
 ("core-vertical",(1011,512,1267,1766),"x"),
 ("core-horizontal",(512,1011,1766,1267),"y"),
 ("center-junction",(883,883,1395,1395),"xy")]:
 p=Z/"qa"/("junction-r2c2-"+name+".png")
 qa.append(derived(p,combined.crop(box),sources,"Unscaled native QA crop from exact replacement union; no annotation or drawing",boxInCombined=list(box),seamAxis=axis,seamLocalCoordinate=([256,256] if axis=="xy" else 128),pixelScale=1))
metrics={}
it=Image.open(target)
for side,box in [("left180",(0,0,180,1254)),("right180",(1074,0,1254,1254)),("top180",(0,0,1254,180)),("bottom180",(0,1074,1254,1254))]:
 diff=ImageChops.difference(it.crop(box).convert("RGB"),im.crop(box).convert("RGB"))
 metrics[side]={"rgbMeanAbsoluteDifference":ImageStat.Stat(diff).mean,"exactEqual":diff.getbbox()is None,"box":list(box)}
save(Z/"qa/junction-r2c2-check.json",{"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"native":ref(native),"nativeSize":list(im.size),"singleGenerationCall":True,"candidates":candidates,"qaArtifacts":qa,"outer180Metrics":metrics,"visualReview":"pending","formalAccepted":False,"usable":False,"sourceHashesUnchanged":all(sha(Path(s["path"]))==s["sha256"]for s in tr["derivedFrom"])})
print(json.dumps({"native":str(native),"sha256":sha(native),"size":list(im.size),"metadataKeys":list(im.info),"candidates":candidates,"outer180Metrics":metrics,"qa":[x["path"]for x in qa]}))

