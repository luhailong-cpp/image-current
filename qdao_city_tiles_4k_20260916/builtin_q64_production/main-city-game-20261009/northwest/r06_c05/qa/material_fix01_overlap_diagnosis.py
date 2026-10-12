import json,sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest");sys.path.insert(0,str(z));import assemble_native as a
out=z/"r06_c05/qa/material-fix01-overlap-diagnosis";out.mkdir(exist_ok=True)
p=z/"r06_c04/native/s02_04_road01.png";q=z/"r06_c05/native/s02_01_material02_fix01.png"
A=np.asarray(Image.open(p).convert("RGB"));B=np.asarray(Image.open(q).convert("RGB"))
base,seam=a.append_with_minimum_seam(A,B)
path=seam.copy();path[348:604]=230
overlap=np.where((np.arange(230)[None,:]>=path[:,None])[...,None],B[:,:230],A[:,-230:])
candidate=np.concatenate([A[:,:-230],overlap,B[:,230:]],axis=1)
imgs={}
for name,arr in [("minimum-error",base),("blue-body-west-to230",candidate)]:
 im=Image.fromarray(arr)
 imgs[name+"-pair"]=im.crop((979,0,1299,1254)).transpose(Image.Transpose.ROTATE_90)
 imgs[name+"-blue-detail"]=im.crop((1100,335,1380,620))
 imgs[name+"-seam-native"]=im.crop((979,115,1299,1139)).transpose(Image.Transpose.ROTATE_90)
imgs["fix01-native-joint-and-paper"]=Image.fromarray(B).crop((150,420,350,620))
imgs["stonefix01-native-joint-and-paper"]=Image.open(z/"r06_c05/native/s02_01_stonefix01.png").crop((150,420,350,620))
imgs["material02-native-joint-and-paper"]=Image.open(z/"r06_c05/native/s02_01_material02.png").crop((150,420,350,620))
entries=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,im in imgs.items():
 op=out/(name+".png");im.save(op);entries.append({"name":name,"file":str(op),"sha256":sha(op),"pixels":list(im.size)})
report={"purpose":"Diagnostic native pixel selection only; no source file or final assembly modified","sourceReferences":[{"file":str(x),"sha256":sha(x)} for x in [p,q]],"hypothesis":{"cutYNativeHalfOpen":[348,604],"overlapCutX":230,"otherwise":"unchanged minimum-error seam"},"entries":entries,"sourceResampled":False}
(out/"mechanical-evidence.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))

