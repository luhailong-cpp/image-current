from pathlib import Path
import json,hashlib,sys
from PIL import Image
import numpy as np
root=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/accelerated-yamen-north")
d=root/"r04_c04"/"upper-left-work"
sys.path.insert(0,str(root))
import pipeline
for tag,prefix in [("v1","s02_01"),("v2","s02_01-v2")]:
 p=d/f"s02_01-raw-{tag}.png"
 im=Image.open(p)
 params=json.loads((d/(prefix+"-parameters.json")).read_text(encoding="utf-8"))
 info={"file":str(p),"size":list(im.size),"mode":im.mode,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"actualModel":None,"actualQuality":None,"route":"builtin","resized":False,"formalAccepted":False,"references":[{"file":r,"sha256":hashlib.sha256(Path(r).read_bytes()).hexdigest(),"size":list(Image.open(r).size)} for r in params["referenced_image_paths"]]}
 if tag=="v1": (d/"s02_01-v1-native-evidence.json").write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
a=np.array(Image.open(d/"s02_01-raw-v2.png").convert("RGB"))
b=np.array(Image.open(root/"r04_c04"/"native"/"s03_01_v1.png").convert("RGB"))
joined,seam=pipeline.append_native(a.transpose(1,0,2),b.transpose(1,0,2),230)
joined=joined.transpose(1,0,2)
Image.fromarray(joined[900:1380]).save(d/"s02_01-s03_01-native-seam-review.png")
info={"operation":"QA preview only, binary minimum-error seam, no resampling","sourceA":str(d/"s02_01-raw-v2.png"),"sourceB":str(root/"r04_c04"/"native"/"s03_01_v1.png"),"crop":[0,900,1254,1380],"seamPath":seam.tolist(),"formallyAccepted":False}
(d/"s02_01-s03_01-native-seam-review.json").write_text(json.dumps(info,indent=2),encoding="utf-8")

