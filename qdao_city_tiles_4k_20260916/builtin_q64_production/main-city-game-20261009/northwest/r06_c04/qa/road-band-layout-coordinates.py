from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c04")
c=json.loads((t.parent.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
p=Path(c['layoutReference']);im=Image.open(p).convert('RGB')
cropbox=(285,398,346,435)
crop=im.crop(cropbox).resize((976,592),Image.Resampling.NEAREST)
canvas=Image.new('RGB',(976,642),'white');canvas.paste(crop,(0,50));d=ImageDraw.Draw(canvas)
d.text((10,10),'LAYOUT ANALYSIS ONLY: overview x285..346 y398..435; nearest16x; cyan tile boundary',fill='black')
bx=(16384*1254/65536-285)*16
d.line((bx,50,bx,642),fill='cyan',width=2)
for y,col in [(21669,'yellow'),(21719,'cyan'),(21989,'cyan'),(22039,'yellow')]:
 sy=y*1254/65536
 yy=50+(sy-398)*16
 d.line((0,yy,975,yy),fill=col,width=1)
 d.text((2,yy+2),f'worldY {y} / sourceY {sy:.3f}',fill='black')
out=t/'qa/road-band-layout-coordinates.png';canvas.save(out)
print(json.dumps({'sourceSize':im.size,'sourceBox':cropbox,'boundarySourceX':16384*1254/65536,'yCoords':{y:y*1254/65536 for y in [21669,21719,21989,22039]},'image':str(out)}))

