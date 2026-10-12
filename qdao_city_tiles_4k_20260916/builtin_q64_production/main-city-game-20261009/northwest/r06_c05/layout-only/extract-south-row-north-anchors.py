from pathlib import Path
from PIL import Image
import json, hashlib
import numpy as np
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c05")
selection=json.loads((b/"selection.json").read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[]
for c in range(1,5):
 key=f"s04_{c:02}"
 p=Path(selection[key])
 im=Image.open(p).convert("RGB")
 out=b/"layout-only"/(p.stem+".north-overlap-native.png")
 im.crop((0,0,1254,230)).save(out)
 x=16384+(c-1)*1024-115
 deriv={"role":"exact unscaled generated native north230 anchor","gameArtSource":str(p),"sourceSha256":sha(p),"sourceBox":[0,0,1254,230],"overlapWorldBox":[x,23437,x+1254,23667],"targetPatch":f"s03_{c:02}","targetBox":[0,1024,1254,1254],"resampled":False,"sha256":sha(out)}
 out.with_suffix(".png.derivation.json").write_text(json.dumps(deriv,indent=2),encoding="utf-8")
 sources.append({"patch":key,"source":str(p),"sha256":sha(p),"northAnchor":str(out),**{k:deriv[k] for k in ("sourceBox","overlapWorldBox","targetPatch","targetBox")}})
p=Path(selection["s04_03"])
a=np.array(Image.open(p).convert("RGB")).astype(int)
measure=[]
for y in [0,115,229,627,1139,1253]:
 v=a[max(0,y-2):min(1254,y+3)].mean(axis=0)
 xs=np.where((v[:,2]-v[:,0]>10)&(v[:,0]<205))[0]
 measure.append({"nativeY":y,"blueRangeApproxInclusive":[int(xs.min()),int(xs.max())],"worldXApproxInclusive":[18317+int(xs.min()),18317+int(xs.max())]})
report={"sources":sources,"blueColorMeasurement":measure,"blueEdgeCaveat":"edge antialias/joints make +-3px variations; visually straight and same width top to bottom","targetGeometry":{"bodyX":[585,935],"outerX":[515,1005]},"visualActualApprox":{"bodyX":[610,958],"outerX":[523,1045]},"actualModel":None,"actualQuality":None,"formalAccepted":False,"northAndWholeTileQA":"pending root assembly"}
(b/"qa/south-row-handoff.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))

