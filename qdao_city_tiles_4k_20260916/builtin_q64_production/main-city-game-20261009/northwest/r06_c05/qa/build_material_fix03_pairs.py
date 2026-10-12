import json,sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest");sys.path.insert(0,str(z));import assemble_native as a
B=z/"r06_c05";cur=B/"native/s02_01_material02_fix03.png";out=B/"qa/s02_01_material02_fix03";out.mkdir(exist_ok=True)
pairs=[("north",B/"native/s01_01.png",cur,True),("west",z/"r06_c04/native/s02_04_road01.png",cur,False),("east",cur,B/"native/s02_02_fix01.png",False),("south",cur,B/"native/s03_01.png",True)]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
entries=[]
for name,p,q,hor in pairs:
 A=np.asarray(Image.open(p).convert("RGB"));C=np.asarray(Image.open(q).convert("RGB"))
 if hor:A=A.transpose(1,0,2);C=C.transpose(1,0,2)
 joint,seam=a.append_with_minimum_seam(A,C)
 strip=Image.fromarray(joint[:,979:1299])
 strip=strip.transpose(Image.Transpose.TRANSPOSE) if hor else strip.transpose(Image.Transpose.ROTATE_90)
 dst=out/(name+"-mincut.png");strip.save(dst)
 entries.append({"name":name,"file":str(dst),"sha256":sha(dst),"sources":[{"file":str(x),"sha256":sha(x)} for x in [p,q]]})
im=Image.open(cur)
im.crop((150,420,350,620)).save(out/"joint-and-paper.png")
im.crop((0,452,500,470)).save(out/"midgrout.png")
(out/"mechanical-evidence.json").write_text(json.dumps({"candidate":str(cur),"candidateSha256":sha(cur),"entries":entries,"sourceResampled":False},indent=2),encoding="utf-8")
print(out)

