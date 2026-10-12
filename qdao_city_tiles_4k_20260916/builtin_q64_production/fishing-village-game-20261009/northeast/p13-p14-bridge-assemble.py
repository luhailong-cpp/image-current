"""One-shot bridge import, exact candidate crop/paste and unscaled QA; no progress/selection writes."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import json,hashlib,shutil,datetime
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def save(p,o):
 assert not p.exists(),p
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def ref(p):return {"path":str(p),"sha256":sha(p),"generationRecord":str(p)+".generation.json" if Path(str(p)+".generation.json").exists() else None}
def derived(p,im,sources,operation,**kw):
 assert not p.exists(),p
 im.save(p)
 save(Path(str(p)+".derived.json"),{"file":str(p),"sha256":sha(p),"pixels":list(im.size),"derivedFrom":sources,"operation":operation,"formalAccepted":False,**kw})
 return {"path":str(p),"sha256":sha(p),"pixels":list(im.size),"provenanceRecord":str(p)+".derived.json",**kw}
source=Path(r"C:\Users\luyua\.codex\generated_images\01a1216d-bec0-72a3-ae22-ba97f839ea1e\exec-34193300-3265-46d1-9cee-e59e2ff617e9.png")
native=Z/"native/p13-p14-bridge-v1.png"
assert not native.exists()
shutil.copyfile(source,native)
im=Image.open(native)
assert im.size==(1254,1254),("Native output size mismatch; no resizing",im.size)
rp=Z/"records/p13-p14-bridge-v1.receipt.json";receipt=read(rp)
pp=Z/"records/p13-p14-bridge-v1.prompt.txt"
assert pp.read_text(encoding="utf-8-sig")==receipt["request"]["prompt"]
target=Z/"guides/p13-p14-bridge-target.png";targetrecord=read(Path(str(target)+".derived.json"))
roles=["only authoritative global layout","material/style only, not exact coordinate crop","primary approved Q Daoist painting style only; no UI/night/people copied","sole native 1:1 joint seam edit target; reconstruct interior paving across x=627 while preserving fish display and outer 180px on all four sides"]
refs=[{"path":p,"sha256":sha(Path(p)),"role":roles[i]}for i,p in enumerate(receipt["request"]["referenced_image_paths"])]
refs[3]["provenance"]=[{"path":str(target)+".derived.json","sha256":sha(Path(str(target)+".derived.json"))}]
save(Path(str(native)+".generation.json"),{"schemaVersion":1,"file":str(native),"sha256":sha(native),"generatedAt":None,"observedAtUtc":receipt["observedAtUtc"],"timeEvidence":"Tool observation time; exact generation timestamp undisclosed","width":1254,"height":1254,"format":im.format,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":targetrecord["configSnapshot"],"submittedParameters":{"model":None,"quality":None},"submittedModel":None,"submittedQuality":None,"actualModel":None,"actualQuality":None,"unverifiedReason":"Host-managed tool has no model/quality selectors; response and PNG metadata disclose neither actual value.","references":refs,"prompt":{"path":str(pp),"sha256":sha(pp)},"receipt":{"path":str(rp),"sha256":sha(rp)},"evidence":{"receipt":str(rp),"pngMetadataKeys":list(im.info),"returnedFields":receipt["response"]["keys"]},"source":{"path":str(source),"sha256":sha(source),"operation":"byte-for-byte copy; no transform"},"nativeGlobalBox":targetrecord["nativeGlobalBox"],"nativeResizePerformed":False,"dimensionValidation":{"expected":[1254,1254],"actual":list(im.size),"passed":True},"usableNative":False,"formalAccepted":False,"status":"single_attempt_bridge_pending_QA"})
a=Z/"native/r06_c12_p13-v2.png";b=Z/"native/r06_c12_p14-v3.png"
ia=Image.open(a);ib=Image.open(b);it=Image.open(target)
assert ia.size==ib.size==(1254,1254)
joined=Image.new("RGB",(2278,1254))
joined.paste(ia.crop((0,0,512,1254)),(0,0));joined.paste(im,(512,0));joined.paste(ib.crop((742,0,1254,1254)),(1766,0))
sources=[ref(p)for p in (a,native,b)]
candidates=[]
for name,box,globalbox in [
 ("r06_c12_p13-p14-bridge-p13-candidate",(0,0,1254,1254),[46989,20365,48243,21619]),
 ("r06_c12_p14-p13-bridge-p14-candidate",(1024,0,2278,1254),[48013,20365,49267,21619])]:
 p=Z/"native"/(name+".png")
 candidates.append(derived(p,joined.crop(box),sources,"1:1 opaque native crop/paste only; no resize, drawing, feathering or blend",nativeGlobalBox=globalbox,bridgeReplacementGlobalBox=targetrecord["nativeGlobalBox"],combinedNativeGlobalBox=[46989,20365,49267,21619],cropFromCombined=list(box),status="single_attempt_bridge_pending_QA"))
qa=[]
for name,x in (("left-boundary",512),("right-boundary",1766),("core-seam",1139)):
 box=(x-128,0,x+128,1254);p=Z/"qa"/("p13-p14-bridge-"+name+".png")
 qa.append(derived(p,joined.crop(box),sources,"Native 1:1 QA crop from the three-source exact pasted union; no scale or drawing",boxInCombined=list(box),seamLocalX=128))
metrics={}
for side,box in (("left180",(0,0,180,1254)),("right180",(1074,0,1254,1254)),("top180",(0,0,1254,180)),("bottom180",(0,1074,1254,1254))):
 d=ImageChops.difference(im.crop(box).convert("RGB"),it.crop(box).convert("RGB"))
 metrics[side]={"rgbMeanAbsoluteDifference":ImageStat.Stat(d).mean,"exactEqual":d.getbbox()is None,"allPixelsCompared":True,"box":list(box)}
for name,box in (("top-edge-compare",(0,0,1254,180)),("bottom-edge-compare",(0,1074,1254,1254))):
 pair=Image.new("RGB",(1254,360));pair.paste(it.crop(box),(0,0));pair.paste(im.crop(box),(0,180))
 p=Z/"qa"/("p13-p14-bridge-"+name+".png")
 qa.append(derived(p,pair,[ref(target),ref(native)],"Two unscaled crops stacked: original target above, AI output below; no drawing",sourceBox=list(box),order=["original_target","AI_output"]))
# Check the current lower neighbors at the actual native-core boundary y=1139.
downa=Z/"native/r06_c12_p23-v1.png";downb=Z/"native/r06_c12_p24-v2.png"
lower=Image.new("RGB",(2278,1254));lower.paste(Image.open(downa).crop((0,0,1139,1254)),(0,0));lower.paste(Image.open(downb).crop((115,0,1254,1254)),(1139,0))
pair=Image.new("RGB",(2278,256));pair.paste(joined.crop((0,1011,2278,1139)),(0,0));pair.paste(lower.crop((0,115,2278,243)),(0,128))
p=Z/"qa/p13-p14-bridge-bottom-neighbor-seam.png"
qa.append(derived(p,pair,sources+[ref(downa),ref(downb)],"Native 1:1 adjacent-core QA; top=bridge candidates local y1011..1139, bottom=existing p23/p24 local y115..243",seamLocalY=128,horizontalPatchBoundary=1139))
save(Z/"qa/p13-p14-bridge-check.json",{"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"nativeResult":ref(native),"singleImageGenerationCall":True,"candidates":candidates,"qaArtifacts":qa,"outerContextMetrics":metrics,"visualQA":"pending native-resolution inspection","formalAccepted":False,"usable":False,"originalsUnchanged":{"p13":sha(a)==targetrecord["derivedFrom"][0]["sha256"],"p14":sha(b)==targetrecord["derivedFrom"][1]["sha256"]},"upperNeighborUnavailable":"This is subrow 1; no northern tile pixels are available. Top edge is compared against the exact original target."})
print(json.dumps({"native":str(native),"sha256":sha(native),"size":list(im.size),"metadataKeys":list(im.info),"candidates":candidates,"metrics":metrics,"qa":[x["path"]for x in qa]}))

