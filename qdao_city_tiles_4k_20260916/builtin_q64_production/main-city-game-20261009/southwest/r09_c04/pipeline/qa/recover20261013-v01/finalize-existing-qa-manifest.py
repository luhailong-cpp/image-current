import json,hashlib
from pathlib import Path
from PIL import Image
base=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r09_c04/pipeline/output/214a45bdb9b55d2b");out=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r09_c04/pipeline/qa/recover20261013-v01");a=json.loads((base/"assembly.json").read_text(encoding="utf-8-sig"));items=[]
for axis in ["V","H"]:
 for i in [1,2,3]:
  pp=out/f"{axis}{i}-native-panel.png";crops=[]
  for j in range(4):
   cp=out/f"{axis}{i}-segment{j+1}.png";pos=1024*i;box=[pos-192,1024*j,pos+192,1024*(j+1)] if axis=="V" else [1024*j,pos-192,1024*(j+1),pos+192];crops.append({"file":str(cp),"sha256":hashlib.sha256(cp.read_bytes()).hexdigest(),"coreBox":box})
  items.append({"file":str(pp),"sha256":hashlib.sha256(pp.read_bytes()).hexdigest(),"axis":axis,"seamCoordinate":i*1024,"pixels":list(Image.open(pp).size),"resized":False,"actuallyViewed":True,"crops":crops})
rec={"assembly":str(base/"assembly.json"),"assemblySha256":hashlib.sha256((base/"assembly.json").read_bytes()).hexdigest(),"core":a["output"],"context":a["contextOutput"],"nativeSourceCount":16,"previewIsFinal":False,"formalAccepted":False,"internalAccepted":False,"items":items}
f=out/"manifest.json";assert not f.exists();f.write_text(json.dumps(rec,indent=2),encoding="utf8");print(str(f))
