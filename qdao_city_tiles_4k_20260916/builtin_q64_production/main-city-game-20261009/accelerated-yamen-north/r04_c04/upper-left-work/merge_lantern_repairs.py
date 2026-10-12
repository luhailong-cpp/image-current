from pathlib import Path
import sys,json,hashlib,argparse
from PIL import Image
import numpy as np
ROOT=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/accelerated-yamen-north")
D=ROOT/"r04_c04"/"upper-left-work"
sys.path.insert(0,str(ROOT))
import pipeline
parser=argparse.ArgumentParser()
parser.add_argument("--run",required=True)
parser.add_argument("--lower")
args=parser.parse_args()
out=D/args.run
out.mkdir(exist_ok=False)
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source(path,box,role):
 p=Path(path)
 im=Image.open(p).convert("RGB")
 assert im.size==(1254,1254)
 return {"path":str(p),"sha256":digest(p),"pixels":[1254,1254],"worldBox":box,"role":role},np.array(im)
specs=[
 (D/"s01_01-raw-v1.png",[12173,12173,13427,13427],"original s01_01 generated artwork"),
 (ROOT/"r04_c04/native/s02_01_v4.png",[12173,13197,13427,14451],"original s02_01 selected generated artwork"),
 (ROOT/"r04_c04/native/s03_01_v1.png",[12173,14221,13427,15475],"original s03_01 selected generated artwork"),
 (D/"seam01-work/repair-v1-native.png",[12173,12685,13427,13939],"builtin seam-centered upper repair")]
if args.lower: specs.append((Path(args.lower),[12173,13709,13427,14963],"builtin seam-centered lower repair"))
sources=[]; arrays=[]
for spec in specs:
 meta,pix=source(*spec); sources.append(meta); arrays.append(pix)
canvas=np.empty((3302,1254,3),dtype=np.uint8)
labels=np.empty((3302,1254),dtype=np.uint8)
baselineCuts=[(0,1139,0,0),(1139,2163,1,115),(2163,3302,2,115)]
for y0,y1,idx,sy in baselineCuts:
 canvas[y0:y1]=arrays[idx][sy:sy+y1-y0]
 labels[y0:y1]=idx+1
joins=[]
for idx in range(3,len(arrays)):
 repair=arrays[idx]
 offset=sources[idx]["worldBox"][1]-12173
 old=canvas[offset:offset+1254].copy()
 topBand=[180,420]; bottomBand=[840,1120]
 ta,tb=topBand; ba,bb=bottomBand
 top=pipeline.minimum_seam(old[ta:tb].transpose(1,0,2),repair[ta:tb].transpose(1,0,2))+ta
 bottom=pipeline.minimum_seam(repair[ba:bb].transpose(1,0,2),old[ba:bb].transpose(1,0,2))+ba
 ys=np.arange(1254)[:,None]
 choose=(ys>=top[None,:])&(ys<bottom[None,:])
 canvas[offset:offset+1254]=np.where(choose[...,None],repair,old)
 labels[offset:offset+1254]=np.where(choose,idx+1,labels[offset:offset+1254])
 joins.append({"sourceId":idx+1,"worldBox":sources[idx]["worldBox"],"localFrameOffsetY":offset,"topCandidateBand":topBand,"bottomCandidateBand":bottomBand,"topPath":top.tolist(),"bottomPath":bottom.tolist(),"pixelSelection":"binary, no blending, feathering, color change or resampling"})
 for name,path in [("entry",top),("exit",bottom)]:
  middle=int(np.median(path))+offset
  cropBox=[0,max(0,middle-160),1254,min(3302,middle+160)]
  Image.fromarray(canvas[cropBox[1]:cropBox[3]]).save(out/f"repair-{idx+1}-{name}-boundary-QA.png")
 center=offset+627
 Image.fromarray(canvas[center-230:center+230]).save(out/f"repair-{idx+1}-original-seam-QA.png")
# Every output pixel must be copied directly from a recorded original image at its exact world position.
for idx,(meta,pix) in enumerate(zip(sources,arrays)):
 y0=meta["worldBox"][1]-12173
 region=canvas[y0:y0+1254]
 labelRegion=labels[y0:y0+1254]
 selected=labelRegion==idx+1
 assert np.array_equal(region[selected],pix[selected]),f"Pixel provenance mismatch for source {idx+1}"
# Baseline outer context remains source-native.
assert np.array_equal(canvas[:512],arrays[0][:512])
assert np.array_equal(canvas[-512:],arrays[2][-512:])
strip=out/"lantern-column-context.png"
Image.fromarray(canvas).save(strip)
mask=out/"lantern-column-source-index.png"
Image.fromarray(labels).save(mask)
manifest={"recordType":"multi_source_native_pixel_derivation","nativeToolOutput":False,"worldBox":[12173,12173,13427,15475],"pixels":[1254,3302],"file":str(strip),"sha256":digest(strip),"sourceMap":str(mask),"sourceMapSha256":digest(mask),"sourceMapLegend":{str(i+1):s for i,s in enumerate(sources)},"sources":sources,"baselineSourceCuts":baselineCuts,"repairJoins":joins,"resampled":False,"colorCorrected":False,"blended":False,"pixelProvenanceCheck":"PASS: each output pixel exactly equals recorded source pixel at identical world coordinate","formalAccepted":False,"QA":"pending visual review of generated seam bands and entry/exit boundaries"}
patches=[]
for row,y0 in [(1,0),(2,1024),(3,2048)]:
 p=out/f"s{row:02d}_01-derived.png"
 Image.fromarray(canvas[y0:y0+1254]).save(p)
 pm=out/f"s{row:02d}_01-source-index.png"
 Image.fromarray(labels[y0:y0+1254]).save(pm)
 record={"recordType":"multi_source_native_pixel_derivation","nativeToolOutput":False,"tool":None,"route":"derived_from_builtin_native_pixels","file":str(p),"width":1254,"height":1254,"sha256":digest(p),"worldBoxWithHalo":[12173,12173+y0,13427,13427+y0],"resizedAfterGeneration":False,"finalArtUpscaled":False,"actualModel":None,"actualQuality":None,"formalAccepted":False,"derivationManifest":str(out/"derivation.json"),"sourceMap":str(pm),"sourceMapSha256":digest(pm),"sources":sources,"generationEvidence":"All generated source evidence retained separately; this PNG is an unscaled mult-source assembly, not a single tool output."}
 p.with_suffix(".png.generation.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
 patches.append(record)
manifest["derivedPatches"]=patches
(out/"derivation.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"directory":str(out),"strip":str(strip),"derivedPatches":[p["file"] for p in patches],"pixelProvenanceCheck":"passed","formalAccepted":False},indent=2))

