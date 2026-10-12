from pathlib import Path
from PIL import Image
import json, hashlib
d=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/accelerated-yamen-north/r04_c04/upper-left-work")
out=d/"seam01-work"
out.mkdir(exist_ok=True)
sources=[d/"s01_01-raw-v1.png",d.parent/"native"/"s02_01_v4.png"]
boxes=[[0,512,1254,1139],[0,115,1254,742]]
guide=Image.new("RGB",(1254,1254))
ops=[]
for source,box,y in zip(sources,boxes,[0,627]):
 im=Image.open(source).convert("RGB")
 guide.paste(im.crop(box),(0,y))
 ops.append({"source":str(source),"sourceSha256":hashlib.sha256(source.read_bytes()).hexdigest(),"sourceSize":list(im.size),"sourceBox":box,"targetBox":[0,y,1254,y+627],"resampled":False})
path=out/"seam01-center-guide.png"
guide.save(path)
record={"gameArt":False,"purpose":"real seam-centered native context for repair","file":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"pixels":[1254,1254],"worldBox":[12173,12685,13427,13939],"seamWorldY":13312,"seamLocalY":627,"operations":ops,"formalAccepted":False}
(out/"seam01-center-guide.provenance.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(record,ensure_ascii=False,indent=2))

