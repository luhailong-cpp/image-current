from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06')
src=r/'layout-only/west-seam-r3-fix01.actual-1254.png';p=r/'layout-only/west-seam-r3-fix03.locator-guide.png'
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
d.line((627,691,733,599),fill=(238,30,35),width=11)
d.line((627,628,752,582),fill=(0,180,220),width=5)
d.ellipse((618,619,636,637),outline=(210,0,185),width=3)
d.ellipse((743,573,761,591),outline=(210,0,185),width=3)
im.save(p)
der=json.loads(src.with_suffix('.png.derivation.json').read_text(encoding='utf-8'))
o=p.with_suffix('.png.derivation.json');assert not o.exists()
o.write_text(json.dumps(dict(worldBox=der['worldBox'],guideOnly=True,notFinalArt=True,source=dict(file=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest()),ink=dict(cyanDesiredGrout=[[627,628],[752,582]],redGroutToErase=[[627,691],[733,599]],magentaFixedAnchors=[[627,628],[752,582]])),indent=2),encoding='utf-8')
