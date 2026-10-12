from pathlib import Path
from PIL import Image
import numpy as np, json,hashlib,sys
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/accelerated-yamen-north/r04_c04/column02-repair")
ROOT=D.parent.parent
sys.path.insert(0,str(ROOT))
import pipeline
out=D/"merged-v1"
out.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
specs=[
 (D.parent/"native/s02_02_v1.png",[13197,13197,14451,14451],D.parent/"native/s02_02_v1.png.generation.json"),
 (D.parent/"native/s03_02_v1.png",[13197,14221,14451,15475],D.parent/"native/s03_02_v1.png.generation.json"),
 (D/"repair-v1-native.png",[13197,13709,14451,14963],D/"repair-v1-evidence.json")]
sources=[];arrays=[]
for p,box,e in specs:
 im=Image.open(p).convert("RGB"); assert im.size==(1254,1254)
 arrays.append(np.array(im))
 sources.append({"path":str(p),"sha256":sha(p),"pixels":[1254,1254],"worldBox":box,"generationEvidence":str(e),"generationEvidenceSha256":sha(e)})
canvas=np.concatenate([arrays[0][:1139],arrays[1][115:]],axis=0)
labels=np.concatenate([np.ones((1139,1254),np.uint8),np.full((1139,1254),2,np.uint8)])
offset=512; repair=arrays[2]; old=canvas[offset:offset+1254].copy()
topBand=[180,350];bottomBand=[975,1180]
ta,tb=topBand;ba,bb=bottomBand
top=pipeline.minimum_seam(old[ta:tb].transpose(1,0,2),repair[ta:tb].transpose(1,0,2))+ta
bottom=pipeline.minimum_seam(repair[ba:bb].transpose(1,0,2),old[ba:bb].transpose(1,0,2))+ba
ys=np.arange(1254)[:,None]
choose=(ys>=top[None,:])&(ys<bottom[None,:])
canvas[offset:offset+1254]=np.where(choose[...,None],repair,old)
labels[offset:offset+1254]=np.where(choose,3,labels[offset:offset+1254])
for idx,(s,a) in enumerate(zip(sources,arrays)):
 y0=s["worldBox"][1]-13197
 region=canvas[y0:y0+1254];selected=labels[y0:y0+1254]==idx+1
 assert np.array_equal(region[selected],a[selected])
assert np.array_equal(canvas[:512],arrays[0][:512])
assert np.array_equal(canvas[-512:],arrays[1][-512:])
strip=out/"column02-context.png";Image.fromarray(canvas).save(strip)
sm=out/"column02-source-index.png";Image.fromarray(labels).save(sm)
qa=[]
for label,cy,radius in [("entry",offset+int(np.median(top)),170),("old-defect",offset+512,220),("seam-center",offset+627,230),("exit",offset+int(np.median(bottom)),170)]:
 box=[0,cy-radius,1254,cy+radius]
 p=out/(label+"-QA.png");Image.fromarray(canvas[box[1]:box[3]]).save(p)
 qa.append({"file":str(p),"sha256":sha(p),"cropBox":box,"nativePixelScale":1,"actuallyViewed":False})
manifest={"recordType":"multi_source_native_pixel_derivation","nativeToolOutput":False,"worldBox":[13197,13197,14451,15475],"pixels":[1254,2278],"file":str(strip),"sha256":sha(strip),"sources":sources,"sourceMap":str(sm),"sourceMapSha256":sha(sm),"sourceMapLegend":{"1":"original s02_02_v1","2":"original s03_02_v1","3":"builtin seam-centered repair-v1"},"repairWorldBox":[13197,13709,14451,14963],"repairOffsetY":512,"topCandidateBand":topBand,"bottomCandidateBand":bottomBand,"topPath":top.tolist(),"bottomPath":bottom.tolist(),"resampled":False,"blended":False,"colorCorrected":False,"pixelProvenanceCheck":"PASS: every output pixel equals a recorded native source at identical world coordinate","outerNorth512pxPreserved":True,"outerSouth512pxPreserved":True,"formalAccepted":False,"QA":qa}
patches=[]
for row,y0 in [(2,0),(3,1024)]:
 p=out/f"s{row:02d}_02-derived.png";Image.fromarray(canvas[y0:y0+1254]).save(p)
 sp=out/f"s{row:02d}_02-source-index.png";Image.fromarray(labels[y0:y0+1254]).save(sp)
 rec={"recordType":"multi_source_native_pixel_derivation","nativeToolOutput":False,"tool":None,"route":"derived_from_builtin_native_pixels","file":str(p),"width":1254,"height":1254,"sha256":sha(p),"worldBoxWithHalo":[13197,13197+y0,14451,14451+y0],"resizedAfterGeneration":False,"finalArtUpscaled":False,"actualModel":None,"actualQuality":None,"formalAccepted":False,"sources":sources,"derivationManifest":str(out/"derivation.json"),"sourceMap":str(sp),"sourceMapSha256":sha(sp),"generationEvidence":"This is an unscaled multi-source pixel assembly, not a single imagegen output; original evidence linked for all sources."}
 p.with_suffix(".png.generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 patches.append(rec)
assert np.array_equal(np.array(Image.open(patches[0]["file"]))[-230:],np.array(Image.open(patches[1]["file"]))[:230])
manifest["overlap230pxExact"]=True
manifest["derivedPatches"]=patches
(out/"derivation.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
checks=[pipeline.native_info(p["file"]) for p in patches]
print(json.dumps({"outputDirectory":str(out),"checks":checks,"pixelProvenanceCheck":"passed","overlap230pxExact":True,"outerNorth512pxPreserved":True,"outerSouth512pxPreserved":True},indent=2))

