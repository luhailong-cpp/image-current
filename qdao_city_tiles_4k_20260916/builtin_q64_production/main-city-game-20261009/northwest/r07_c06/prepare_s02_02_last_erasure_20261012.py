from PIL import Image,ImageDraw
from pathlib import Path
import hashlib,json
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');src=r/'qa/s02_02_orphanfix02-proposal01/proposal-native-1254.png';p=r/'layout-only/s02_02_orphanfix03.locator-guide.png'
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im);d.line((261,778,230,804),fill=(238,30,35),width=13);d.ellipse((258,763,276,781),outline=(0,130,215),width=3);im.save(p)
o=p.with_suffix('.png.derivation.json');assert not o.exists()
o.write_text(json.dumps(dict(worldBox=[21389,25485,22643,26739],guideOnly=True,notFinalArt=True,source=dict(file=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),proof=str(r/'qa/s02_02_orphanfix02-proposal01/proposal-proof.json')),redBranchToErase=[[267,772],[230,804]],fixedBlueGoldVertex=[267,772]),indent=2),encoding='utf-8')
