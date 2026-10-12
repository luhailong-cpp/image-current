import json,sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c05");sys.path.insert(0,str(B.parent));import assemble_native as a
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cur=B/"native/s02_01_stonefix01.png"
pairs=[("north",B/"native/s01_01.png",cur,True),("west",B.parent/"r06_c04/native/s02_04_road01.png",cur,False),("east",cur,B/"native/s02_02_fix01.png",False),("south",cur,B/"native/s03_01.png",True)]
rep=[]
for name,p,q,horizontal in pairs:
 A=np.asarray(Image.open(p).convert("RGB"));C=np.asarray(Image.open(q).convert("RGB"))
 if horizontal:A=A.transpose(1,0,2);C=C.transpose(1,0,2)
 joint,seam=a.append_with_minimum_seam(A,C)
 hard=np.concatenate([A[:,939:1139],C[:,115:315]],axis=1).transpose(1,0,2)
 minimum=joint[:,939:1339].transpose(1,0,2)
 out=B/"qa"/f"s02_01-stonefix-audit-{name}.png"
 canvas=Image.new("RGB",(1254,848),"#202020");canvas.paste(Image.fromarray(hard),(0,24));canvas.paste(Image.fromarray(minimum),(0,448))
 d=ImageDraw.Draw(canvas);d.text((5,5),name.upper()+" FULL1254 NATIVE PAIR / HARD CUT",fill="white");d.text((5,429),"MINIMUM-ERROR BINARY NATIVE SOURCE SELECTION (NO RESIZE/BLEND)",fill="white");canvas.save(out)
 rep.append({"side":name,"sources":[str(p),str(q)],"sourceSha256":[sha(p),sha(q)],"qa":str(out),"qaSha256":sha(out),"nativeBoundaryLength":1254,"actuallyViewed":False,"seamMinMax":[int(seam.min()),int(seam.max())]})
(B/"qa/s02_01-stonefix-audit-evidence.json").write_text(json.dumps(rep,indent=2),encoding="utf-8")
print(json.dumps(rep,indent=2))

