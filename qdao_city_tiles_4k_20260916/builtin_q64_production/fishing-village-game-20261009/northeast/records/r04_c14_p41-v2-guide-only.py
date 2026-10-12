from PIL import Image
from pathlib import Path
import json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast")
a=Z/"native/r04_c14_p41-v1.png";b=Z/"native/r05_c14_p11-v3.png";out=Z/"guides/r04_c14_p41-v2.native-south-repair-guide.png"
im=Image.open(a).convert("RGB");im.paste(Image.open(b).convert("RGB").crop((0,0,1254,230)),(0,1024));im.save(out)
d={"purpose":"native1:1 repair guide ONLY; bottom real southanchor reinstated in exact registration","operation":"originaltarget copy plus native south230crop/paste; noresize/paint/feather","sources":[{"path":str(a).replace("\\","/"),"sha256":hashlib.sha256(a.read_bytes()).hexdigest(),"role":"original unsuccessful target"},{"path":str(b).replace("\\","/"),"sha256":hashlib.sha256(b.read_bytes()).hexdigest(),"role":"pinned actual southern neighbor","cropBox":[0,0,1254,230],"pasteAt":[0,1024]}],"size":[1254,1254],"resized":False,"finalArt":False}
Path(str(out)+".derived.json").write_text(json.dumps(d,indent=2),encoding="utf-8");print(hashlib.sha256(out.read_bytes()).hexdigest())

