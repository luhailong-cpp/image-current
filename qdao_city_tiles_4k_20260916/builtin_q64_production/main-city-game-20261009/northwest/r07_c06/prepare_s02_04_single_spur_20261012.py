from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');src=r/'native/s02_04_orphanfix02.png';p=r/'layout-only/s02_04_orphanfix03.locator-guide.png'
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im);d.line((322,482,230,563),fill=(238,30,35),width=25);im.save(p)
p.with_suffix('.png.derivation.json').write_text(json.dumps(dict(worldBox=[23437,25485,24691,26739],guideOnly=True,notFinalArt=True,source=dict(file=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest()),redBranchToEraseEntirely=[[322,482],[230,563]],markerWidth=25),indent=2),encoding='utf-8')
