from pathlib import Path
from PIL import Image,ImageFilter,ImageDraw
import numpy as np,json,hashlib
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
f=D/"roof-horizontal-join-v01";q=json.loads((f/"request.json").read_text());rec=json.loads((f/"receipt.json").read_text())
old=np.array(Image.open(f/"input.png").convert("RGB"));new=np.array(Image.open(f/"native.png").convert("RGB"))
points=[(0,815),(200,745),(560,390),(810,340),(1139,370),(1139,1000),(1030,1254),(0,1254)]
mi=Image.new("L",(1254,1254));ImageDraw.Draw(mi).polygon(points,fill=255);m=np.array(mi)>0
alpha=np.zeros(m.shape,float);er=m.copy()
for k in range(48):
 alpha+=er/48.0
 pad=np.pad(er,1,mode="edge")
 er=pad[:-2,1:-1]&pad[2:,1:-1]&pad[1:-1,:-2]&pad[1:-1,2:]&er
ap=np.rint(old.astype(float)*(1-alpha[:,:,None])+new.astype(float)*alpha[:,:,None]).clip(0,255).astype("uint8")
assert np.array_equal(ap[~m],old[~m])
Image.fromarray(ap).save(f/"applied-crop-v02.png");Image.fromarray(m.astype("uint8")*255).save(f/"copy-mask-v02.png");Image.fromarray(np.rint(alpha*255).astype("uint8")).save(f/"alpha-v02.png")
box=q["sourceCrop"];src=Path(q["sourceContext"]["file"]);assert sha(src)==q["sourceContext"]["sha256"]
ctx=np.array(Image.open(src).convert("RGB"));region=ctx[box[1]:box[3],box[0]:box[2]];assert np.array_equal(region,old);region[m]=ap[m]
out=D/"integrated-local-v02";out.mkdir(exist_ok=False);Image.fromarray(ctx).save(out/"r12_c05.candidate.context.png");Image.fromarray(ctx[115:4211,115:4211]).save(out/"r12_c05.candidate.png")
ys,xs=np.where(m);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
p={"operation":"native generated gold seam localized composite","input":q["sourceContext"],"sourceCrop":box,"cropWorldBox":q["cropWorldBox"],"request":{"file":str(f/"request.json"),"sha256":sha(f/"request.json")},"receipt":{"file":str(f/"receipt.json"),"sha256":sha(f/"receipt.json")},"native":rec["savedNativePath"],"nativeSha256":rec["savedNativeSha256"],"patch":{"file":str(f/"applied-crop-v02.png"),"sha256":sha(f/"applied-crop-v02.png")},"copyMask":{"file":str(f/"copy-mask-v02.png"),"sha256":sha(f/"copy-mask-v02.png")},"alpha":{"file":str(f/"alpha-v02.png"),"sha256":sha(f/"alpha-v02.png")},"maskRule":"explicit polygon around actual gold rail join with48px bounded alpha feather; no color threshold holes; excludes far-right tile exterior","copyRule":"copy applied-crop pixels where copy-mask>0, no second blend","maskLocalBox":bbox,"maskWorldBox":[bbox[0]+q["cropWorldBox"][0],bbox[1]+q["cropWorldBox"][1],bbox[2]+q["cropWorldBox"][0],bbox[3]+q["cropWorldBox"][1]],"outsideMaskUnchanged":True,"sourceResampling":False,"actualModel":None,"actualQuality":None,"localGeometry":"duplicated upper tongue removed; single smooth rising rail, local improvement","remaining":"lower-left vertical roof join remains; patch edges and whole tile QA pending","formalAccepted":False,"internalAccepted":False}
(f/"proposal-v02.json").write_text(json.dumps(p,indent=2))
a={"sourceAssembly":q["sourceAssembly"],"appliedProposals":[str(f/"proposal-v02.json")],"contextOutput":{"file":str(out/"r12_c05.candidate.context.png"),"sha256":sha(out/"r12_c05.candidate.context.png")},"output":{"file":str(out/"r12_c05.candidate.png"),"sha256":sha(out/"r12_c05.candidate.png")},"formalAccepted":False,"internalAccepted":False,"sourceResampling":False}
(out/"assembly.json").write_text(json.dumps(a,indent=2));print(json.dumps(a))

