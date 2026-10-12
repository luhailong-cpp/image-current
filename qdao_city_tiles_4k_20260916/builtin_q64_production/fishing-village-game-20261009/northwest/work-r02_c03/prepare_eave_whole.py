from pathlib import Path
import json,hashlib
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");w=B/"work-r02_c03";up=B/"native/r02_c03_roof_join_v01.png";down=B/"native/r03_c03_s01_s01_v01.png"
im=Image.new("RGB",(1254,1254));im.paste(Image.open(up).crop((0,250,1254,1254)),(0,0));im.paste(Image.open(down).crop((0,777,1254,1027)),(0,1004))
p=w/"guides/r02_c03_eave_whole_join_v01.native-target.png";im.save(p)
d={"file":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"globalNativeBox":[8077,7850,9331,9104],"sources":[{"file":str(up),"sourceCrop":[0,250,1254,1254],"destination":[0,0]},{"file":str(down),"sourceCrop":[0,777,1254,1027],"destination":[0,1004]}],"resampled":False,"guideOnly":True}
Path(str(p)+".derivation.json").write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")

