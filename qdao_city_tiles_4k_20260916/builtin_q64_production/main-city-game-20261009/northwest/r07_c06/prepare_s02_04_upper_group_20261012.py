from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');src=r/'layout-only/s02_04_orphanfix01.actual-1254.png';p=r/'layout-only/s02_04_orphanfix01.locator-guide.png'
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
d.line((226,364,230,360),fill=(238,30,35),width=11)
d.line((230,392,316,476),fill=(238,30,35),width=11)
d.line((316,488,230,563),fill=(238,30,35),width=11)
d.line((222,368,322,482),fill=(0,180,220),width=5)
for x,y in [(222,368),(322,482)]:d.ellipse((x-9,y-9,x+9,y+9),outline=(0,130,215),width=3)
im.save(p)
o=p.with_suffix('.png.derivation.json');assert not o.exists()
o.write_text(json.dumps(dict(worldBox=[23437,25485,24691,26739],guideOnly=True,notFinalArt=True,source=dict(file=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest()),ink=dict(cyanDesiredGrout=[[222,368],[322,482]],redBranchesToErase=[[[222,368],[230,360]],[[230,392],[322,482]],[[322,482],[230,563]]],blueFixedGoldVertices=[[222,368],[322,482]])),indent=2),encoding='utf-8')
