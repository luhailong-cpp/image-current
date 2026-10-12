from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast")
src=Z/"native/r05_c14_p34-v2.png"
out=Z/"guides/r05_c14_p34-v3.corner-detail-layout-only.png"
im=Image.open(src).crop((150,940,390,1140)).resize((720,600),Image.Resampling.NEAREST)
d=ImageDraw.Draw(im)
d.ellipse((170,182,310,322),outline=(255,0,180),width=6)
d.line((80,110,205,217),fill=(255,0,180),width=6)
im.save(out)
Path(str(out)+".derived.json").write_text(json.dumps({"purpose":"ANNOTATED DETAIL GUIDE ONLY; never final pixels","source":{"path":str(src).replace("\\","/"),"sha256":hashlib.sha256(src.read_bytes()).hexdigest()},"sourceCropBox":[150,940,390,1140],"operation":"exact crop plus nearest3x solely for readability, magenta circle points to unwanted artificial water corner; annotations must not be output","resized":True,"finalArt":False},indent=2),encoding="utf-8")
print(str(out))

