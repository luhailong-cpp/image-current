from pathlib import Path
from PIL import Image
import json,hashlib
d=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/accelerated-yamen-north/r04_c04/column02-repair"); d.mkdir(exist_ok=True)
base=d.parent
guide=Image.new("RGB",(1254,1254))
ops=[]
for source,box,y in [(base/"native/s02_02_v1.png",[0,512,1254,1139],0),(base/"native/s03_02_v1.png",[0,115,1254,742],627)]:
 im=Image.open(source).convert("RGB")
 guide.paste(im.crop(box),(0,y))
 ops.append({"source":str(source),"sourceSha256":hashlib.sha256(source.read_bytes()).hexdigest(),"sourcePixels":list(im.size),"sourceBox":box,"targetBox":[0,y,1254,y+627],"resampled":False})
p=d/"seam-center-guide.png";guide.save(p)
meta={"file":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"pixels":[1254,1254],"worldBox":[13197,13709,14451,14963],"seamWorldY":14336,"seamLocalY":627,"internalDefectLocalY":512,"gameArt":False,"operations":ops}
(d/"seam-center-guide.provenance.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(meta,ensure_ascii=False,indent=2))

