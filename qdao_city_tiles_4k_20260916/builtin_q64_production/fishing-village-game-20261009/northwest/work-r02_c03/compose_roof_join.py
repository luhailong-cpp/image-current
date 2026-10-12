from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");sys.path.insert(0,str(B))
from assemble_r03_c03 import append_hard
from apply_r03_c03_repairs import minimum_path
w=B/"work-r02_c03";out=w/"roof-join-v2";out.mkdir(exist_ok=True)
names=["r02_c03_s04_s01_v01","r03_c03_s01_s01_v01","r02_c03_roof_join_v01"]
sources=[];arr=[]
for i,n in enumerate(names,1):
 p=B/"native"/(n+".png");meta=json.loads(Path(str(p)+".generation.json").read_text());arr.append(np.asarray(Image.open(p).convert("RGB")));sources.append({"sourceId":i,"file":str(p),"sha256":meta["sha256"],"globalNativeBox":meta["globalNativeBox"],"generationRecord":str(p)+".generation.json","generationRecordSha256":hashlib.sha256(Path(str(p)+".generation.json").read_bytes()).hexdigest()})
a,ids,oldpath=append_hard(arr[0].transpose(1,0,2),np.ones((1254,1254),np.uint16),arr[1].transpose(1,0,2),np.full((1254,1254),2,np.uint16),"v")
a=a.transpose(1,0,2);ids=ids.T
crop=a[547:1801];cost=((crop.astype(np.int64)-arr[2].astype(np.int64))**2).sum(2)
top,tc=minimum_path(cost.T,1,280)
blue=(crop[:,:,2].astype(int)>crop[:,:,0].astype(int)+30)&(crop[:,:,2].astype(int)>crop[:,:,1].astype(int)*0.9)
last_blue=np.array([np.where(blue[:,x])[0].max() for x in range(1254)])
lo=np.maximum(500,last_blue-220);hi=np.minimum(1190,last_blue-35)
bottom_cost=cost.T.copy();yy0=np.arange(1254)[None,:]
bottom_cost[(yy0<lo[:,None])|(yy0>hi[:,None])]=np.int64(1<<40)
bottom,bc=minimum_path(bottom_cost,500,1190)
assert np.all((bottom>=lo)&(bottom<=hi))
yy,xx=np.indices((1254,1254));m=(yy>=top[None,:])&(yy<bottom[None,:]);crop[m]=arr[2][m];ids[547:1801][m]=3
Image.fromarray(a).save(out/"r02_r03_first-column.native-pair.png");Image.fromarray(ids).save(out/"source-id.png");Image.fromarray(m.astype(np.uint8)*255).save(out/"bridge-mask.png")
proof=0;gy,gx=np.indices(ids.shape);gb=[8077,7053,9331,9331]
for s,img in zip(sources,arr):
 y,x=np.where(ids==s["sourceId"]);nb=s["globalNativeBox"];proof+=int(np.any(a[y,x]!=img[y+gb[1]-nb[1],x+gb[0]-nb[0]],axis=1).sum())
assert proof==0
record={"globalBox":gb,"sources":sources,"candidate":{"file":str(out/"r02_r03_first-column.native-pair.png"),"sha256":hashlib.sha256((out/"r02_r03_first-column.native-pair.png").read_bytes()).hexdigest()},"sourceIdMap":{"file":str(out/"source-id.png")},"mask":{"file":str(out/"bridge-mask.png")},"selectedBridgePixels":int(m.sum()),"proof":{"pixels":int(ids.size),"mismatches":proof},"topCut":top.tolist(),"bottomCut":bottom.tolist(),"baseJoin":oldpath,"formalAccepted":False,"status":"partial-column-pending-perimeter-QA"}
(out/"assembly.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
for name,box in [("north",(0,547,1254,887)),("south",(0,1447,1254,1851)),("former-seam",(0,910,1254,1190))]:
 Image.fromarray(a).crop(box).save(out/(name+".100pct.png"))
print(json.dumps({"pixels":int(ids.size),"mismatches":proof,"selectedBridgePixels":int(m.sum())}))

