from pathlib import Path
from PIL import Image
import hashlib,json,re,shutil,numpy as np,sys
R=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");D=R/"work-r03_c02/west-final"
read=lambda p:json.loads(Path(p).read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
names=["r03_c02_c03_E2_rolls_v01","r03_c02_c03_E2_folds_v01"]
for name in names:
 req=read(D/(name+".request.json"));rec=read(D/(name+".receipt.json"));dst=D/(name+".png");orig=Path(re.search(r" as (C:\\[^\n]+?\.png) by default",rec["output_hint"]).group(1))
 if not dst.exists():shutil.copy2(orig,dst)
 assert Image.open(dst).size==(1254,1254)
 refs=[{"file":p,"sha256":sha(p),"role":r} for p,r in zip(req["referenced_image_paths"],req["referenceRoles"])]
 box=req["globalNativeBox"]
 g={"file":str(dst),"sha256":sha(dst),"generatedAt":rec["returnedAt"],"width":1254,"height":1254,"format":"PNG","tool":"image_gen.imagegen","route":"builtin","nativeScaleResampled":False,"actualModel":None,"actualQuality":None,"submittedParameters":{"model":None,"quality":None},"unverifiedReason":"Builtin exposes no model/quality selectors and returns no actual model/quality metadata.","globalNativeBox":box,"globalCoreBox":[box[0]+115,box[1]+115,box[2]-115,box[3]-115],"nativeCoreCropBox":[115,115,1139,1139],"configSnapshot":read("D:/work/image/config/image-generation.json"),"references":refs,"prompt":str(D/(name+".prompt.txt")),"evidence":{"request":str(D/(name+".request.json")),"receipt":str(D/(name+".receipt.json"))},"toolOriginal":{"file":str(orig),"sha256":sha(orig)}}
 (D/(name+".png.generation.json")).write_text(json.dumps(g,indent=2),encoding="utf8")
sys.path.insert(0,str(R/"work-r03_c04"))
from apply_r03_c04_repairs import minimum_path
def mask_dp(a,b,dom):
 c=np.sum((a.astype(np.int32)-b.astype(np.int32))**2,axis=2,dtype=np.int64)+1
 left,_=minimum_path(c,*dom[0]);right,_=minimum_path(c,*dom[1]);top,_=minimum_path(c.T,*dom[2]);bottom,_=minimum_path(c.T,*dom[3]);yy,xx=np.indices(c.shape)
 return (xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:]),{"leftXByY":left.tolist(),"rightXByY":right.tolist(),"topYByX":top.tolist(),"bottomYByX":bottom.tolist(),"domains":dom}
m=read(D/"internal1-assembly.json");pair=np.asarray(Image.open(m["candidate"])).copy();ids=np.asarray(Image.open(m["sourceIdFile"])).copy()
domains=[[[35,115],[1060,1230],[120,240],[1000,1139]],[[1,90],[1210,1252],[1,100],[1150,1252]]]
for name,key,dom in zip(names,[1004,1005],domains):
 p=D/(name+".png");gp=Path(str(p)+".generation.json");g=read(gp);b=g["globalNativeBox"];x,y=b[0]-4096,b[1]-8192;a=np.asarray(Image.open(p));target=pair[y:y+1254,x:x+1254]
 mask,paths=mask_dp(target,a,dom);target[mask]=a[mask];ids[y:y+1254,x:x+1254][mask]=key
 mf=D/(name+".mask.png");Image.fromarray(mask.astype(np.uint8)*255).save(mf)
 m["sources"][str(key)]={"sourceId":key,"file":str(p),"sha256":sha(p),"globalNativeBox":b,"generationRecord":str(gp),"generationRecordSha256":sha(gp)}
 m["overlays"].append({"sourceId":key,"globalNativeBox":b,"maskFile":str(mf),"maskSHA256":sha(mf),"selectedPixels":int(mask.sum()),"paths":paths})
out=D/"textile1-pair.png";oi=D/"textile1-source-id.png";Image.fromarray(pair).save(out);Image.fromarray(ids).save(oi)
m.update(candidate=str(out),candidateSHA256=sha(out),sourceIdFile=str(oi),sourceIdSHA256=sha(oi))
(D/"textile1-assembly.json").write_text(json.dumps(m,indent=2),encoding="utf8")
Image.fromarray(pair).crop((7500-4096,11050-8192,9000-4096,12288-8192)).save(D/"textile1-whole.100pct.png")
print(json.dumps({"candidate":str(out),"selectedNew":[o["selectedPixels"] for o in m["overlays"][-2:]]}))

