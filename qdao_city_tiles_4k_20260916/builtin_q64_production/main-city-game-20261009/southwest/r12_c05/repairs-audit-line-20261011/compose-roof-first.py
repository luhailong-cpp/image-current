from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
f=D/"roof-horizontal-join-v01";q=json.loads((f/"request.json").read_text());rec=json.loads((f/"receipt.json").read_text())
old=np.array(Image.open(f/"input.png").convert("RGB"));new=np.array(Image.open(f/"native.png").convert("RGB"))
def gold(a):
 a=a.astype(float);return (a[:,:,0]>110)&(a[:,:,1]>65)&(a[:,:,0]>a[:,:,1]*1.08)&(a[:,:,2]<a[:,:,0]*0.70)
m=gold(old)|gold(new);yy,xx=np.indices(m.shape);m &= (yy>=410)&(xx<1040)
mi=Image.fromarray((m*255).astype("uint8")).filter(ImageFilter.MaxFilter(25))
m=np.array(mi)>0;m[:,1040:]=False;m[:405]=False
er1=np.array(Image.fromarray(m.astype("uint8")*255).filter(ImageFilter.MinFilter(3)))>0
er2=np.array(Image.fromarray(er1.astype("uint8")*255).filter(ImageFilter.MinFilter(3)))>0
alpha=.25*m+.5*er1+.25*er2
ap=np.rint(old.astype(float)*(1-alpha[:,:,None])+new.astype(float)*alpha[:,:,None]).clip(0,255).astype("uint8")
assert np.array_equal(ap[~m],old[~m])
Image.fromarray(ap).save(f/"applied-crop.png");Image.fromarray(m.astype("uint8")*255).save(f/"copy-mask.png");Image.fromarray(np.rint(alpha*255).astype("uint8")).save(f/"alpha.png")
box=q["sourceCrop"];src=Path(q["sourceContext"]["file"]);assert sha(src)==q["sourceContext"]["sha256"]
ctx=np.array(Image.open(src).convert("RGB"));region=ctx[box[1]:box[3],box[0]:box[2]];assert np.array_equal(region,old);region[m]=ap[m]
out=D/"integrated-local-v01";out.mkdir(exist_ok=False);Image.fromarray(ctx).save(out/"r12_c05.candidate.context.png");Image.fromarray(ctx[115:4211,115:4211]).save(out/"r12_c05.candidate.png")
ys,xs=np.where(m);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
p={"operation":"native generated gold seam localized composite","input":q["sourceContext"],"sourceCrop":box,"cropWorldBox":q["cropWorldBox"],"request":{"file":str(f/"request.json"),"sha256":sha(f/"request.json")},"receipt":{"file":str(f/"receipt.json"),"sha256":sha(f/"receipt.json")},"native":rec["savedNativePath"],"nativeSha256":rec["savedNativeSha256"],"patch":{"file":str(f/"applied-crop.png"),"sha256":sha(f/"applied-crop.png")},"copyMask":{"file":str(f/"copy-mask.png"),"sha256":sha(f/"copy-mask.png")},"alpha":{"file":str(f/"alpha.png"),"sha256":sha(f/"alpha.png")},"maskRule":"union of existing/generated golden rail silhouette, explicitly ROI y>=410 x<1040; 12px dilation, bounded2px feather; excludes far-right tile exterior","copyRule":"copy applied-crop pixels where copy-mask>0, no second blend","maskLocalBox":bbox,"maskWorldBox":[bbox[0]+q["cropWorldBox"][0],bbox[1]+q["cropWorldBox"][1],bbox[2]+q["cropWorldBox"][0],bbox[3]+q["cropWorldBox"][1]],"outsideMaskUnchanged":True,"sourceResampling":False,"actualModel":None,"actualQuality":None,"localGeometry":"duplicated upper tongue removed; single smooth rising rail, local improvement","remaining":"lower-left vertical roof join remains; patch edges and whole tile QA pending","formalAccepted":False,"internalAccepted":False}
(f/"proposal.json").write_text(json.dumps(p,indent=2))
a={"sourceAssembly":q["sourceAssembly"],"appliedProposals":[str(f/"proposal.json")],"contextOutput":{"file":str(out/"r12_c05.candidate.context.png"),"sha256":sha(out/"r12_c05.candidate.context.png")},"output":{"file":str(out/"r12_c05.candidate.png"),"sha256":sha(out/"r12_c05.candidate.png")},"formalAccepted":False,"internalAccepted":False,"sourceResampling":False}
(out/"assembly.json").write_text(json.dumps(a,indent=2));print(json.dumps(a))

