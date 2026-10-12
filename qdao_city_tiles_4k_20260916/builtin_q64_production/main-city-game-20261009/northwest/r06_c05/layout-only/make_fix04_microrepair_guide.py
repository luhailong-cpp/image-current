import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest");b=z/"r06_c05"
target=b/"native/s02_01_material02_fix01.png";paper=b/"native/s02_01_stonefix01.png";west=z/"r06_c04/native/s02_04_road01.png"
A=np.array(Image.open(target).convert("RGB"));P=np.array(Image.open(paper).convert("RGB"));W=np.array(Image.open(west).convert("RGB"))
# This explicitly modified target is a layout/edit instruction guide only.
G=A.copy()
G[456:467,:230]=W[456:467,1024:1254]
for x in range(230,401):
 t=(x-230)/170
 G[456:467,x]=np.rint((1-t)*W[456:467,1253].astype(float)+t*A[456:467,x].astype(float)).astype(np.uint8)
box=(218,577,245,600);l,t,r,bm=box
patch=P[t:bm,l:r];mask=(patch[:,:,0]>140)&(patch[:,:,0]>patch[:,:,1]*1.3)&(patch[:,:,0]>patch[:,:,2]*1.3)
Gp=G[t:bm,l:r];Gp[mask]=patch[mask]
out=z/"r06_c05/layout-only/s02_01_material02_fix04.microrepair-guide.png"
Image.fromarray(G).save(out)
view=z/"r06_c05/qa/material-fix01-overlap-diagnosis/fix04-guide-microrepair.png"
Image.fromarray(G).crop((0,420,450,620)).save(view)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
der={"purpose":"NON-PRODUCTION layout-only microrepair guide for built-in image editing. This file MUST NOT be selected, assembled, or treated as native art.","base":{"file":str(target),"sha256":sha(target)},"references":[{"file":str(p),"sha256":sha(p)} for p in [paper,west]],"operations":[{"region":[0,456,230,467],"method":"native west reference last230px joint band copied to matching target coordinates"},{"region":[230,456,401,467],"method":"narrow instruction-guide joint gradually transitions from west reference end to target current dark joint; only guideline band, not final art"},{"region":list(box),"method":"copy only saturated red paper pixels from former complete same-coordinate native source; background is unchanged"}],"output":{"file":str(out),"sha256":sha(out),"pixels":[1254,1254]},"finalArt":False}
Path(str(out)+".derivation.json").write_text(json.dumps(der,indent=2),encoding="utf-8")
print(json.dumps({"guide":str(out),"detail":str(view)}))

