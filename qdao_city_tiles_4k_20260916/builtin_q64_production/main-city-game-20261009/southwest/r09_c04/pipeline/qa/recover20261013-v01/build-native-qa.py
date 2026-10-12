import json,hashlib
from pathlib import Path
from PIL import Image
base=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r09_c04/pipeline/output/214a45bdb9b55d2b");out=Path(__file__).parent
assert not (out/"manifest.json").exists()
a=json.loads((base/"assembly.json").read_text(encoding="utf-8-sig"));p=Path(a["output"]["file"]);assert hashlib.sha256(p.read_bytes()).hexdigest()==a["output"]["sha256"]
im=Image.open(p).convert("RGB");assert im.size==(4096,4096)
items=[]
for axis in ["V","H"]:
 for i in [1,2,3]:
  pos=1024*i;panel=Image.new("RGB",(768,2048) if axis=="V" else (2048,768));crops=[]
  for j in range(4):
   box=(pos-192,1024*j,pos+192,1024*(j+1)) if axis=="V" else (1024*j,pos-192,1024*(j+1),pos+192)
   crop=im.crop(box);cp=out/f"{axis}{i}-segment{j+1}.png";crop.save(cp);loc=((j%2)*384,(j//2)*1024) if axis=="V" else ((j%2)*1024,(j//2)*384);panel.paste(crop,loc)
   crops.append({"file":str(cp),"sha256":hashlib.sha256(cp.read_bytes()).hexdigest(),"coreBox":box,"panelBox":[*loc,loc[0]+crop.width,loc[1]+crop.height]})
  pp=out/f"{axis}{i}-native-panel.png";panel.save(pp);items.append({"file":str(pp),"sha256":hashlib.sha256(pp.read_bytes()).hexdigest(),"axis":axis,"seamCoordinate":pos,"pixels":panel.size,"resized":False,"crops":crops})
rec={"assembly":str(base/"assembly.json"),"assemblySha256":hashlib.sha256((base/"assembly.json").read_bytes()).hexdigest(),"core":a["output"],"context":a["context"],"nativeSourceCount":16,"previewIsFinal":False,"formalAccepted":False,"internalAccepted":False,"items":items}
(out/"manifest.json").write_text(json.dumps(rec,indent=2),encoding="utf8");print(json.dumps({"manifest":str(out/"manifest.json"),"panels":[x["file"] for x in items]}))
