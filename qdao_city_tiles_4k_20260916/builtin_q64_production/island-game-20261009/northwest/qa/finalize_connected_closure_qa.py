"""Reopen final PNGs, replay the four disjoint raw masks and export native QA."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];O=Z/"qa/connected-closure-final-v1";O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=str(p),sha256=sha(p))
read=lambda p:json.loads(Path(p).read_text(encoding="utf8"))
initial=read(Z/"qa/connected-closure-current-v1.manifest.json")
final=read(Z/"qa/connected-closure-current-v5.manifest.json")
operations=[Z/f"tiles/connected-closure-cross-v{i}"/f"{name}.cross-native-operation.json" for i,name in enumerate(("cross-paving-upper-v1","cross-paving-middle-v1","cross-paving-lower-v1","cross-paving-left-v1"),1)]
ops=[read(p) for p in operations]
arrays={};proof=[]
for tile in final["tiles"]:
 tid=tile["tileId"];start=next(t for t in initial["tiles"] if t["tileId"]==tid)
 expected=np.array(Image.open(start["image"]["path"]).convert("RGB"));base=expected.copy();used=np.zeros((4096,4096),bool)
 for op in ops:
  for part in op["selectedParts"]:
   if part["tileId"]!=tid:continue
   raw=op["repairSource"];maskinfo=op["mask"]
   assert sha(raw["path"])==raw["sha256"] and sha(maskinfo["path"])==maskinfo["sha256"]
   a=np.array(Image.open(raw["path"]).convert("RGB"));m=np.array(Image.open(maskinfo["path"]))
   assert a.shape==(1254,1254,3) and m.shape==(1254,1254) and set(np.unique(m)).issubset({0,255})
   x0,y0,x1,y1=part["tileBox"];sx0,sy0,sx1,sy1=part["repairBox"];sel=m[sy0:sy1,sx0:sx1]==255
   assert not np.any(used[y0:y1,x0:x1]&sel),"repair masks unexpectedly overlap"
   expected[y0:y1,x0:x1][sel]=a[sy0:sy1,sx0:sx1][sel];used[y0:y1,x0:x1]|=sel
 assert sha(tile["image"]["path"])==tile["image"]["sha256"] and sha(tile["record"]["path"])==tile["record"]["sha256"]
 actual=np.array(Image.open(tile["image"]["path"]).convert("RGB"));assert np.array_equal(expected,actual)
 assert np.array_equal(actual[~used],base[~used])
 arrays[tid]=Image.fromarray(actual)
 row,col=(int(x[1:]) for x in tid.split("_"))
 checks={}
 if row==3:checks["north"]=np.array_equal(actual[0],base[0])
 if row==4:checks["south"]=np.array_equal(actual[-1],base[-1])
 if col==3:checks["west"]=np.array_equal(actual[:,0],base[:,0])
 if col==4:checks["east"]=np.array_equal(actual[:,-1],base[:,-1])
 assert all(checks.values())
 proof.append(dict(tileId=tid,output=tile["image"],record=tile["record"],verifiedPixels=4096*4096,selectedNativePixels=int(used.sum()),unchangedOtherPixels=True,clusterOuterEdgesIdentical=checks))
def crop(box):
 x0,y0,x1,y1=box;out=Image.new("RGB",(x1-x0,y1-y0))
 for tid,im in arrays.items():
  row,col=(int(x[1:]) for x in tid.split("_"));ox=(col-3)*4096;oy=(row-3)*4096
  a,b,c,d=max(x0,ox),max(y0,oy),min(x1,ox+4096),min(y1,oy+4096)
  if c>a and d>b:out.paste(im.crop((a-ox,b-oy,c-ox,d-oy)),(a-x0,b-y0))
 return out
cluster=read(Z/"tiles/connected-r03-r04-c03-c04-v1/connected-cluster.json")
crops=[]
for q in cluster["qa"]["nativeScaleCrops"]:
 old=Path(q["output"]["path"]);path=O/old.name;crop(q["box"]).save(path)
 crops.append(dict(box=q["box"],output=info(path),matchesPreviouslyViewedNativeCrop=np.array_equal(np.array(Image.open(old)),np.array(Image.open(path)))))
preview=Image.new("RGB",(1536,1536))
for tid,im in arrays.items():
 row,col=(int(x[1:]) for x in tid.split("_"));preview.paste(im.resize((768,768),Image.Resampling.LANCZOS),((col-3)*768,(row-3)*768))
preview_path=O/"PREVIEW_NOT_FOR_GAME_1536.png";preview.save(preview_path)
report=dict(schemaVersion=1,status="native pixel replay passed; final visual closure pending",manifest=info(Z/"qa/connected-closure-current-v5.manifest.json"),operations=[info(p) for p in operations],tiles=proof,verifiedPixelCount=4*4096*4096,repairMasksDisjoint=True,nativeScaleCrops=crops,previewOnly=info(preview_path),visualAccepted=False,formalAcceptedCount=0)
(O/"pixel-replay-and-qa.json").write_text(json.dumps(report,indent=2),encoding="utf8")
print(json.dumps(dict(report=str(O/"pixel-replay-and-qa.json"),changedQa=[Path(q["output"]["path"]).name for q in crops if not q["matchesPreviouslyViewedNativeCrop"]]),indent=2))

