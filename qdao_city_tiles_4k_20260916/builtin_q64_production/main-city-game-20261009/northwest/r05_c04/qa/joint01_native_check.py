from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
import numpy as np
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c04")
source=Path(r"C:/Users/luyua/.codex/generated_images/01a12555-a3c9-7951-957c-40d92bde68ae/exec-4777d8a3-f720-4676-b8a2-fc32e808cc52.png")
pid="s04_02_joint01"
target=B/"native"/(pid+".png")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
assert not target.exists()
shutil.copyfile(source,target)
reqpath=B/"receipts"/(pid+".request.json")
request=json.loads(reqpath.read_text(encoding="utf-8-sig"))
im=Image.open(target); im.load()
refs=request["references"]
for ref in refs: assert sha(Path(ref["file"]))==ref["sha256"]
record={"schemaVersion":2,"file":str(target),"sha256":sha(target),"width":im.width,"height":im.height,"mode":im.mode,"generatedAt":datetime.now(timezone.utc).isoformat(),"route":"builtin_image_gen","logicalPatch":"s04_02","resizedAfterGeneration":False,"finalArtUpscaled":False,"actualModel":None,"actualQuality":None,"configurationTarget":request["configurationSnapshot"],"submittedParameters":request["parameters"],"prompt":str(B/"prompts"/(pid+".txt")),"promptSha256":sha(B/"prompts"/(pid+".txt")),"references":refs,"evidence":{"request":str(reqpath),"receipt":str(B/"receipts"/(pid+".tool-result.json")),"hostOutputPath":str(source),"pngInfo":im.info,"modelQualityEvidence":"Tool exposes no model/quality selectors or returned version; configuration is not proof of actual backend."},"worldBoxWithHalo":request["worldBoxWithHalo"],"coreWorldBox":request["coreWorldBox"],"coreCrop":[115,115,1139,1139],"nativeDimensionsMatchPlan":im.size==(1254,1254),"status":"native_candidate_pending_parent_selection"}
put(target.with_suffix(".png.generation.json"),record)
assert im.size==(1254,1254)
old=np.array(Image.open(B/"native/s04_02.png").convert("RGB")); new=np.array(im.convert("RGB"))
north=np.array(Image.open(B/"native/s03_02.png").convert("RGB"))
def diff(a,b):
 d=np.abs(a.astype(float)-b.astype(float))
 return {"mae":float(d.mean()),"p95":float(np.percentile(d,95)),"max":float(d.max()),"identicalPixelFraction":float(np.all(a==b,axis=2).mean())}
sys.path.insert(0,str(B.parent)); import assemble_native as asm
arrays,sources,missing=asm.load_sources(B,[12288,16384,16384,20480])
arrays[3,1]=new
whole,paths=asm.minimum_error_assembly(arrays)
out=B/"qa"/(pid+"-trial-minimum-error.png"); whole.save(out)
tiles=np.array(whole)
Image.fromarray(new[:420,590:710]).save(B/"qa"/(pid+"-full-joint-native.png"))
Image.fromarray(tiles[2800:3400,1400:1750]).save(B/"qa"/(pid+"-assembled-joint-native.png"))
for name,box in {"north":(1024,2912,2048,3232),"west":(864,3072,1184,4096),"east":(1888,3072,2208,4096),"south":(1024,3866,2048,4096)}.items():
 crop=whole.crop(box)
 if name in ("west","east"): crop=crop.transpose(Image.Transpose.ROTATE_90)
 crop.save(B/"qa"/(pid+"-"+name+"-native.png"))
def profiles(a,ys,x0,x1):
 result=[]
 for y in ys:
  l=a[y,x0:x1].mean(axis=1); bg=np.median(np.r_[l[:5],l[-5:]]); inds=np.flatnonzero(l<bg-25)
  result.append({"y":y,"darkRange":[int(x0+inds[0]),int(x0+inds[-1])] if len(inds) else None,"darkCount":len(inds),"darkestX":int(x0+l.argmin())})
 return result
report={"id":pid,"nativeFile":str(target),"nativeSha256":sha(target),"nativePixels":list(im.size),"south230ComparisonToOriginal":diff(new[1024:],old[1024:]),"below400ComparisonToOriginal":diff(new[400:],old[400:]),"north230ComparisonToNeighbor":diff(new[:230],north[1024:]),"nativeJointProfiles":profiles(new,[0,10,38,50,100,150,200,225,230,240,250,275,290,310],615,655),"assembledJointProfiles":profiles(tiles,[2970,2990,2995,3000,3020,3050,3080,3100,3150,3200],1530,1560),"trialAssembly":{"file":str(out),"sha256":sha(out),"size":list(whole.size),"sourceOverride":{"s04_02":str(target)},"selectionFileChanged":False,"allOtherSources":sources,"minimumErrorPaths":paths},"visualReviewPending":True}
put(B/"qa"/(pid+"-measurements.json"),report)
print(json.dumps({k:v for k,v in report.items() if k not in ("trialAssembly",)},ensure_ascii=False,indent=2))

