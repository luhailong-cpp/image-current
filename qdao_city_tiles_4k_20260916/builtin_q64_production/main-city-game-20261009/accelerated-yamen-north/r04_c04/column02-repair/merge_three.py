from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/accelerated-yamen-north/r04_c04/column02-repair")
ROOT=D.parent.parent
sys.path.insert(0,str(ROOT))
import pipeline
out=D/"merged-three-v1";out.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
specs=[
 (D/"upper-shaft-work/shaft-v3-native.png",[13197,12173,14451,13427],D/"upper-shaft-work/shaft-v3-evidence.json","s01_02 width-corrected native generation"),
 (D.parent/"native/s02_02_v1.png",[13197,13197,14451,14451],D.parent/"native/s02_02_v1.png.generation.json","original selected s02_02"),
 (D.parent/"native/s03_02_v1.png",[13197,14221,14451,15475],D.parent/"native/s03_02_v1.png.generation.json","original selected s03_02"),
 (D/"upper-shaft-work/upper-repair-v1-native.png",[13197,12685,14451,13939],D/"upper-shaft-work/upper-repair-v1-evidence.json","upper seam-centered native repair"),
 (D/"repair-v1-native.png",[13197,13709,14451,14963],D/"repair-v1-evidence.json","lower seam-centered native repair")]
sources=[];arrays=[]
for p,box,e,role in specs:
 im=Image.open(p).convert("RGB");assert im.size==(1254,1254)
 arrays.append(np.array(im));sources.append({"path":str(p),"sha256":sha(p),"pixels":[1254,1254],"worldBox":box,"generationEvidence":str(e),"generationEvidenceSha256":sha(e),"role":role})
canvas=np.empty((3302,1254,3),np.uint8);labels=np.empty((3302,1254),np.uint8)
for y0,y1,idx,sy in [(0,1139,0,0),(1139,2163,1,115),(2163,3302,2,115)]:
 canvas[y0:y1]=arrays[idx][sy:sy+y1-y0];labels[y0:y1]=idx+1
joins=[]
for idx in [3,4]:
 offset=sources[idx]["worldBox"][1]-12173;repair=arrays[idx];old=canvas[offset:offset+1254].copy()
 topBand=[180,370] if idx==3 else [180,350];bottomBand=[975,1180]
 ta,tb=topBand;ba,bb=bottomBand
 top=pipeline.minimum_seam(old[ta:tb].transpose(1,0,2),repair[ta:tb].transpose(1,0,2))+ta
 bottom=pipeline.minimum_seam(repair[ba:bb].transpose(1,0,2),old[ba:bb].transpose(1,0,2))+ba
 ys=np.arange(1254)[:,None];choose=(ys>=top[None,:])&(ys<bottom[None,:])
 canvas[offset:offset+1254]=np.where(choose[...,None],repair,old)
 labels[offset:offset+1254]=np.where(choose,idx+1,labels[offset:offset+1254])
 joins.append({"sourceId":idx+1,"worldBox":sources[idx]["worldBox"],"offsetY":offset,"topCandidateBand":topBand,"bottomCandidateBand":bottomBand,"topPath":top.tolist(),"bottomPath":bottom.tolist()})
for idx,(meta,a) in enumerate(zip(sources,arrays)):
 y0=meta["worldBox"][1]-12173;region=canvas[y0:y0+1254];selected=labels[y0:y0+1254]==idx+1
 assert np.array_equal(region[selected],a[selected])
assert np.array_equal(canvas[:512],arrays[0][:512])
assert np.array_equal(canvas[-512:],arrays[2][-512:])
strip=out/"column02-context.png";Image.fromarray(canvas).save(strip)
mask=out/"column02-source-index.png";Image.fromarray(labels).save(mask)
qa=[]
for j in joins:
 for label,cy,radius in [("entry",j["offsetY"]+int(np.median(j["topPath"])),180),("center",j["offsetY"]+627,230),("exit",j["offsetY"]+int(np.median(j["bottomPath"])),180)]:
  box=[0,cy-radius,1254,cy+radius];p=out/f"repair-{j['sourceId']}-{label}-QA.png";Image.fromarray(canvas[box[1]:box[3]]).save(p)
  qa.append({"file":str(p),"sha256":sha(p),"cropBox":box,"nativePixelScale":1,"actuallyViewed":False})
# Explicitly retain the lower source's former internal defect region.
cy=1536+512;p=out/"lower-old-defect-QA.png";Image.fromarray(canvas[cy-220:cy+220]).save(p)
qa.append({"file":str(p),"sha256":sha(p),"cropBox":[0,cy-220,1254,cy+220],"nativePixelScale":1,"actuallyViewed":False})
manifest={"recordType":"multi_source_native_pixel_derivation","nativeToolOutput":False,"worldBox":[13197,12173,14451,15475],"pixels":[1254,3302],"file":str(strip),"sha256":sha(strip),"sources":sources,"sourceMap":str(mask),"sourceMapSha256":sha(mask),"sourceMapLegend":{str(i+1):s for i,s in enumerate(sources)},"joins":joins,"resampled":False,"blended":False,"colorCorrected":False,"pixelProvenanceCheck":"PASS: every final pixel equals a recorded native source at identical world coordinate","northContext":"Top512px preserved from corrected-width native s01_02 shaft-v3, intentionally superseding incorrect original width","south512pxPreservedFromOriginal":True,"formalAccepted":False,"QA":qa}
patches=[]
for row,y0 in [(1,0),(2,1024),(3,2048)]:
 p=out/f"s{row:02d}_02-derived.png";Image.fromarray(canvas[y0:y0+1254]).save(p)
 pm=out/f"s{row:02d}_02-source-index.png";Image.fromarray(labels[y0:y0+1254]).save(pm)
 rec={"recordType":"multi_source_native_pixel_derivation","nativeToolOutput":False,"tool":None,"route":"derived_from_builtin_native_pixels","file":str(p),"width":1254,"height":1254,"sha256":sha(p),"worldBoxWithHalo":[13197,12173+y0,14451,13427+y0],"resizedAfterGeneration":False,"finalArtUpscaled":False,"actualModel":None,"actualQuality":None,"formalAccepted":False,"sources":sources,"sourceMap":str(pm),"sourceMapSha256":sha(pm),"derivationManifest":str(out/"derivation.json"),"generationEvidence":"Unscaled multi-source native pixel assembly; all original generation evidence retained and linked."}
 p.with_suffix(".png.generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 patches.append(rec)
a=[np.array(Image.open(p["file"])) for p in patches]
assert np.array_equal(a[0][-230:],a[1][:230])
assert np.array_equal(a[1][-230:],a[2][:230])
manifest["overlaps230pxExact"]=True;manifest["derivedPatches"]=patches
(out/"derivation.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
checks=[pipeline.native_info(p["file"]) for p in patches]
print(json.dumps({"directory":str(out),"checks":checks,"pixelProvenance":"passed","overlaps230pxExact":True},indent=2))

