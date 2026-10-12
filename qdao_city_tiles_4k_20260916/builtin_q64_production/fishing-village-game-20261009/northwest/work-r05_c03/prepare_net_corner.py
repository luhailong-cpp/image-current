from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");sys.path.insert(0,str(B))
from assemble_r03_c03 import append_hard
names=["r05_c03_s01_s02_v01","r05_c03_s01_s03_v01","r05_c03_s02_s02_v01","r05_c03_s02_s03_v01"]
arr=[np.asarray(Image.open(B/"native"/(n+".png")).convert("RGB")) for n in names]
rows=[];ids=[];paths=[]
for i in [0,2]:
 a,s,r=append_hard(arr[i],np.full(arr[i].shape[:2],i+1,np.uint8),arr[i+1],np.full(arr[i+1].shape[:2],i+2,np.uint8),"h")
 rows.append(a);ids.append(s);paths.append(r)
a,s,r=append_hard(rows[0].transpose(1,0,2),ids[0].T,rows[1].transpose(1,0,2),ids[1].T,"v")
a=a.transpose(1,0,2);s=s.T;paths.append(r)
g=[9580,16750,10834,18004];local=[g[0]-9101,g[1]-16269,g[2]-9101,g[3]-16269]
w=B/"work-r05_c03";p=w/"guides/net-corner-whole-native.png";Image.fromarray(a).crop(local).save(p)
Image.fromarray(s).crop(local).save(w/"guides/net-corner-whole-native.source-id.png")
meta={"globalNativeBox":g,"sourceFiles":[str(B/"native"/(n+".png")) for n in names],"paths":paths,"resampled":False,"guideOnly":True}
Path(str(p)+".derivation.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
print(p)

