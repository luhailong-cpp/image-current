from pathlib import Path
import json,hashlib
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");w=B/"work-r02_c03";up=B/"native/r02_c03_s04_s01_v01.png";down=B/"native/r03_c03_s01_s01_v01.png"
box=[8077,7600,9331,8854];im=Image.new("RGB",(1254,1254))
im.paste(Image.open(up).crop((0,547,1254,1254)),(0,0))
im.paste(Image.open(down).crop((0,0,1254,777)),(0,477))
p=w/"guides/r02_c03_roof_join_v01.native-target.png";im.save(p)
r={"file":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"globalNativeBox":box,"role":"native edit target with visible phase defect; no resampled pixels","sources":[{"file":str(up),"sourceCrop":[0,547,1254,1254],"destination":[0,0]},{"file":str(down),"sourceCrop":[0,0,1254,777],"destination":[0,477]}],"resampled":False}
Path(str(p)+".derivation.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")

