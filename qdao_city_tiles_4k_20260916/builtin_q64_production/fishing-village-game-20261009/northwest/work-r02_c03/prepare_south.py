from pathlib import Path
import json,hashlib
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");p=B/"work-r02_c03/guides/r02_c03_s04_s01.layout-and-native-overlap.png";im=Image.open(p)
s=B/"native/r03_c03_s01_s01_v01.png";im.paste(Image.open(s).crop((0,0,1254,230)),(0,1024))
out=p.with_name("r02_c03_s04_s01.authoritative-south-guide.png");im.save(out)
r=json.loads(Path(str(p)+".derivation.json").read_text());r.update(file=str(out),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),neighbors=[{"file":str(s),"sha256":hashlib.sha256(s.read_bytes()).hexdigest(),"sourceCrop":[0,0,1254,230],"destinationBox":[0,1024,1254,1254]}],note="Diagonal corner overlays excluded; single same-column native supplies continuous roof phase across south230.")
Path(str(out)+".derivation.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")

