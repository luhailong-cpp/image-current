from PIL import Image
from pathlib import Path
import json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast");a=Z/"native/r04_c14_p41-v1.png";b=Z/"native/r05_c14_p11-v3.png";o=Z/"guides/r04_c14_p41_southbridge01-v1.native-context.png"
im=Image.new("RGB",(1254,1254));im.paste(Image.open(a).convert("RGB").crop((0,512,1254,1139)),(0,0));im.paste(Image.open(b).convert("RGB").crop((0,115,1254,742)),(0,627));im.save(o)
d={"purpose":"native1:1 central south-join repair bridge context ONLY","nativeWorldBox":[53133,15757,54387,17011],"size":[1254,1254],"operation":"exact integer crop/paste of actual north/south native sources; noresize/paint/feather","sources":[{"path":str(a).replace("\\","/"),"sha256":hashlib.sha256(a.read_bytes()).hexdigest(),"cropBox":[0,512,1254,1139],"pasteAt":[0,0],"role":"upper unsuccessful registration to repair"},{"path":str(b).replace("\\","/"),"sha256":hashlib.sha256(b.read_bytes()).hexdigest(),"cropBox":[0,115,1254,742],"pasteAt":[0,627],"role":"pinned south groundtruth; source must not be modified"}],"trueJoinY":627,"resized":False,"finalArt":False}
Path(str(o)+".derived.json").write_text(json.dumps(d,indent=2),encoding="utf-8");print(hashlib.sha256(o.read_bytes()).hexdigest())

