from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');src=r/'qa/s02_02_orphanfix01-proposal01/proposal-native-1254.png';p=r/'layout-only/s02_02_orphanfix02.locator-guide.png'
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
d.line((167,1084,230,1024),fill=(238,30,35),width=13)
d.ellipse((152,1081,170,1099),outline=(0,130,215),width=3)
im.save(p)
o=p.with_suffix('.png.derivation.json');assert not o.exists()
o.write_text(json.dumps(dict(worldBox=[21389,25485,22643,26739],guideOnly=True,notFinalArt=True,source=dict(file=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),proof=str(r/'qa/s02_02_orphanfix01-proposal01/proposal-proof.json')),redBranchToErase=[[161,1090],[230,1024]],fixedBlueGoldVertex=[161,1090]),indent=2),encoding='utf-8')
