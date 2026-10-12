"""Exact 2x2 native junction target; integer crop/paste only."""
from pathlib import Path
from PIL import Image
import hashlib,json,datetime
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sel=json.loads((Z/"records/r06_c12.selection.json").read_text(encoding="utf-8-sig"))
patches=("p22","p23","p32","p33")
source_boxes=((0,0,1139,1139),(115,0,1254,1139),(0,115,1139,1254),(115,115,1254,1254))
dest_boxes=((0,0,1139,1139),(1139,0,2278,1139),(0,1139,1139,2278),(1139,1139,2278,2278))
global_boxes=((45965,21389,47219,22643),(46989,21389,48243,22643),(45965,22413,47219,23667),(46989,22413,48243,23667))
combined=Image.new("RGB",(2278,2278));sources=[]
for name,sb,db,gb in zip(patches,source_boxes,dest_boxes,global_boxes):
 p=(Z/sel["patches"]["r06_c12_"+name]).resolve()
 rec=Path(str(p)+".derived.json")
 if not rec.exists():rec=Path(str(p)+".generation.json")
 r=json.loads(rec.read_text(encoding="utf-8-sig"))
 assert sha(p)==r["sha256"]
 actual=r.get("nativeGlobalBox",r.get("coordinates",{}).get("nativeGlobalBox"))
 assert actual==list(gb),(name,actual)
 im=Image.open(p);assert im.size==(1254,1254)
 combined.paste(im.crop(sb),db[:2])
 sources.append({"patchId":"r06_c12_"+name,"path":str(p),"sha256":sha(p),"sourceRecord":{"path":str(rec),"sha256":sha(rec)},"sourceNativeGlobalBox":list(gb),"sourceBox":list(sb),"targetBoxInCombined":list(db)})
target=Z/"guides/junction-r2c2-target.png";assert not target.exists()
combined.crop((512,512,1766,1766)).save(target)
data={"file":str(target),"sha256":sha(target),"pixels":[1254,1254],"nativeGlobalBox":[46477,21901,47731,23155],"combinedNativeGlobalBox":[45965,21389,48243,23667],"combinedPixels":[2278,2278],"junctionInCombined":[1139,1139],"junctionInTarget":[627,627],"cropFromCombined":[512,512,1766,1766],"derivedFrom":sources,"operation":"Four native integer quadrant crops and opaque paste, then 1254 crop; no drawing, resampling, blending or feathering","purpose":"Single-attempt 2x2 junction joint reconstruction target; not final accepted art","configSnapshot":json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"formalAccepted":False}
Path(str(target)+".derived.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"target":str(target),"sha256":sha(target),"nativeGlobalBox":data["nativeGlobalBox"],"sources":sources}))

