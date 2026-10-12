from pathlib import Path
from PIL import Image
import hashlib,json,re,shutil,datetime,sys,numpy as np
R=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");D=R/"work-r03_c02/west-final"
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
jobs=read(D/"jobs.json")
for j in jobs:
 name=j["id"]; req=read(D/(name+".request.json"));rec=read(D/(name+".receipt.json"));dst=D/(name+".png")
 original=Path(re.search(r" as (C:\\[^\n]+?\.png) by default",rec["output_hint"]).group(1))
 if not dst.exists():shutil.copy2(original,dst)
 im=Image.open(dst);assert im.size==(1254,1254)
 b=j["box"];g={"file":str(dst),"sha256":sha(dst),"generatedAt":rec["returnedAt"],"width":1254,"height":1254,"format":"PNG","tool":"image_gen.imagegen","route":"builtin","nativeScaleResampled":False,"actualModel":None,"actualQuality":None,"submittedParameters":{"model":None,"quality":None},"unverifiedReason":"Built-in tool has no model/quality selector and returns no model/quality value.","globalNativeBox":b,"globalCoreBox":[b[0]+115,b[1]+115,b[2]-115,b[3]-115],"nativeCoreCropBox":[115,115,1139,1139],"configSnapshot":read(Path("D:/work/image/config/image-generation.json")),"evidence":{"receipt":str(D/(name+".receipt.json")),"request":str(D/(name+".request.json")),"returnedFields":rec["resultKeys"]},"prompt":str(D/(name+".prompt.txt")),"references":req["references"],"toolOriginal":{"file":str(original),"sha256":sha(original)},"status":"pending-hardmask-and-edge-QA"}
 (D/(name+".png.generation.json")).write_text(json.dumps(g,indent=2),encoding="utf8")
sys.path.insert(0,str(R/"work-r03_c04"))
from apply_r03_c04_repairs import minimum_path
def rectangle_dp(base,native,L,RR,T,B):
 cost=np.sum((base.astype(np.int32)-native.astype(np.int32))**2,axis=2,dtype=np.int64)+1
 left,_=minimum_path(cost,*L);right,_=minimum_path(cost,*RR);top,_=minimum_path(cost.T,*T);bottom,_=minimum_path(cost.T,*B)
 yy,xx=np.indices(cost.shape);mask=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:])
 return mask,{"leftXByY":left.tolist(),"rightXByY":right.tolist(),"topYByX":top.tolist(),"bottomYByX":bottom.tolist(),"domain":[L,RR,T,B],"selectionRule":"intersection of 4 hard-cut inside inequalities"}
m=read(D/"joint0-assembly.json");pair=np.asarray(Image.open(m["candidate"])).copy();ids=np.asarray(Image.open(m["sourceIdFile"])).copy();overlays=[]
domains=[([370,475],[650,780],[10,85],[390,515]),([35,120],[800,915],[200,300],[800,955]),([120,240],[1180,1250],[165,275],[1130,1220])]
for j,dom,k in zip(jobs,domains,[1001,1002,1003]):
 p=D/(j["id"]+".png");native=np.asarray(Image.open(p));target=np.asarray(Image.open(j["target"]));mask,paths=rectangle_dp(target,native,*dom)
 if k==1003:
  yy,xx=np.indices(mask.shape)
  # Preserve all original lantern artwork and the foreground railing. Follow the actual red silhouette with a small fixed context margin.
  red=(target[:,:,0]>150)&(target[:,:,0].astype(np.int16)-target[:,:,1].astype(np.int16)>60)&(target[:,:,1]<145)&(xx<735)&(yy>440)
  for y in range(441,1190):
   xs=np.flatnonzero(red[y])
   if len(xs):mask[y,:min(740,int(xs.max())+7)]=False
  mask[400:495,:495]=False
  mask[275:445,265:405]=False
  # Original foreground gold/wood guardrail lies below this diagonal in the exposed window region.
  for y in range(930,1254):
   mask[y,:930]=False
 b=j["box"];x,y=b[0]-4096,b[1]-8192
 y0=max(0,y);x0=max(0,x);y1=min(4096,y+1254);x1=min(8192,x+1254)
 mm=mask[y0-y:y1-y,x0-x:x1-x];aa=native[y0-y:y1-y,x0-x:x1-x]
 pair[y0:y1,x0:x1][mm]=aa[mm];ids[y0:y1,x0:x1][mm]=k
 mp=D/(j["id"]+".mask.png");Image.fromarray(mask.astype(np.uint8)*255).save(mp)
 gen=Path(str(p)+".generation.json")
 m["sources"][str(k)]={"sourceId":k,"file":str(p),"sha256":sha(p),"globalNativeBox":b,"generationRecord":str(gen),"generationRecordSha256":sha(gen)}
 preview=target.copy();preview[y0-y:y1-y,x0-x:x1-x]=pair[y0:y1,x0:x1]
 qp=D/(j["id"]+".integrated.100pct.png");Image.fromarray(preview).save(qp)
 overlays.append({"sourceId":k,"globalNativeBox":b,"maskFile":str(mp),"maskSHA256":sha(mp),"selectedPixels":int(mm.sum()),"qa":str(qp),"paths":paths})
out=D/"internal1-pair.png";outid=D/"internal1-source-id.png";Image.fromarray(pair).save(out);Image.fromarray(ids).save(outid)
m.update(candidate=str(out),candidateSHA256=sha(out),sourceIdFile=str(outid),sourceIdSHA256=sha(outid),overlays=overlays,visualQA="pending")
(D/"internal1-assembly.json").write_text(json.dumps(m,indent=2),encoding="utf8")
print(json.dumps({"selected":[[o["sourceId"],o["selectedPixels"]] for o in overlays],"candidate":str(out)}))

