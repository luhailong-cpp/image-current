from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");D=R/"work-r03_c02/west-final"
read=lambda p:json.loads(Path(p).read_text(encoding="utf8"));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(D/"textile1-assembly.json");pair=np.asarray(Image.open(m["candidate"])).copy();ids=np.asarray(Image.open(m["sourceIdFile"])).copy()
base=np.asarray(Image.open(D/"joint0-pair.png"));baseid=np.asarray(Image.open(D/"joint0-source-id.png"))
o=next(o for o in m["overlays"] if o["sourceId"]==1003);p=o["paths"];yy,xx=np.indices((1254,1254))
mask=(xx>=np.array(p["leftXByY"])[:,None])&(xx<np.array(p["rightXByY"])[:,None])&(yy>=np.array(p["topYByX"])[None,:])&(yy<np.array(p["bottomYByX"])[None,:])
b=o["globalNativeBox"];x,y=b[0]-4096,b[1]-8192;target=base[y:y+1254,x:x+1254];ti=target.astype(np.int16)
red=(ti[:,:,0]>150)&(ti[:,:,0]-ti[:,:,1]>60)&(ti[:,:,1]<145)&(xx<735)&(yy>440)
for row in range(441,1190):
 xs=np.flatnonzero(red[row])
 if len(xs):mask[row,:min(740,int(xs.max())+7)]=False
mask[400:495,:495]=False;mask[275:445,265:405]=False;mask[1130:,:540]=False
foreground=(yy>900)&(xx<950)&(ti[:,:,0]>95)&(ti[:,:,1]>65)&(ti[:,:,0]-ti[:,:,1]>20)
mask[foreground]=False
region=pair[y:y+1254,x:x+1254];ri=ids[y:y+1254,x:x+1254];old=ri==1003
region[old]=target[old];ri[old]=baseid[y:y+1254,x:x+1254][old]
src=np.asarray(Image.open(m["sources"]["1003"]["file"]));region[mask]=src[mask];ri[mask]=1003
mf=D/"M2-native-object-mask-v2.png";Image.fromarray(mask.astype(np.uint8)*255).save(mf);o.update(maskFile=str(mf),maskSHA256=sha(mf),selectedPixels=int(mask.sum()),foregroundPreservation="Original actual lantern body/caps and warm foreground rail pixels retained; dark window remains one coherent source.")
op=D/"repair2-pair.png";ip=D/"repair2-source-id.png";Image.fromarray(pair).save(op);Image.fromarray(ids).save(ip)
m.update(candidate=str(op),candidateSHA256=sha(op),sourceIdFile=str(ip),sourceIdSHA256=sha(ip))
(D/"repair2-assembly.json").write_text(json.dumps(m,indent=2))
Image.fromarray(region).save(D/"M2-integrated-v2.100pct.png")
Image.fromarray(pair).crop((6450-4096,10480-8192,7170-4096,10820-8192)).save(D/"M2-bottom-v2.100pct.png")
print("saved repaired M2 with object-boundary foreground preservation")

