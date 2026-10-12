from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast")
src=Z/"native/r05_c14_p34-v2.png";out=Z/"guides/r05_c14_p34-v4.edit-scope-layout-only.png"
im=Image.open(src).convert("RGB");d=ImageDraw.Draw(im)
d.rectangle((205,995,255,1250),outline=(255,0,180),width=4)
d.line((380,930,262,1016),fill=(255,0,180),width=5)
im.save(out)
Path(str(out)+".derived.json").write_text(json.dumps({"purpose":"annotated edit scope guide ONLY, no final art pixels","source":{"path":str(src).replace("\\","/"),"sha256":hashlib.sha256(src.read_bytes()).hexdigest()},"operation":"native1:1 target copy plus magenta scope border for existing straight tonal edge x230 below1024; do not output annotation","resized":False,"finalArt":False},indent=2),encoding="utf-8")
print(hashlib.sha256(out.read_bytes()).hexdigest())

