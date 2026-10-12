from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');src=r/'native/s02_02_resume02.png';p=r/'layout-only/s02_02_orphanfix01.locator-guide.png'
im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
branches=[((225,364),(230,359),(219,370)),((201,692),(230,671),(195,698)),((167,1084),(230,1024),(161,1090)),((261,778),(230,804),(267,772))]
for a,z,g in branches:
 d.line((*a,*z),fill=(238,30,35),width=11)
 x,y=g;d.ellipse((x-9,y-9,x+9,y+9),outline=(0,130,215),width=3)
im.save(p)
m=json.loads(src.with_suffix('.png.generation.json').read_text(encoding='utf-8'))
o=p.with_suffix('.png.derivation.json');assert not o.exists()
o.write_text(json.dumps(dict(worldBox=m['worldBoxWithHalo'],guideOnly=True,notFinalArt=True,source=dict(file=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest()),ink=dict(redBranchesToErase=[dict(line=[list(a),list(z)],fixedGoldVertex=list(g)) for a,z,g in branches])),indent=2),encoding='utf-8')
