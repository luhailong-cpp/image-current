from PIL import Image,ImageDraw
from pathlib import Path
import json
t=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c07');im=Image.open(t/'layout-only/s01_02_seam02.edit-guide.png').convert('RGB');d=ImageDraw.Draw(im)
d.rectangle((230,0,1038,1253),fill=(232,228,218))
for slope,anchors in [(0.70,[-56,314,676,1045]),(-0.70,[155,524,915,1285,1655])]:
 for y in anchors:
  end=y+slope*(1038-230);d.line([(230,y),(1038,end)],fill=(255,250,232),width=8);d.line([(230,y),(1038,end)],fill=(130,99,58),width=3)
# Preserve LEFT230 actual native neighbor and fixed cream-curb/blue-road right boundary.
im.paste(Image.open(t/'native/s01_01.png').crop((1024,0,1254,1254)),(0,0))
im.paste(Image.open(t/'native/s01_02.png').crop((1039,0,1254,1254)),(1039,0))
target=t/'layout-only/s01_02_geometry05.continuation-guide.png';assert not target.exists();im.save(target)
(target.with_suffix('.png.derivation.json')).write_text(json.dumps({'operation':'LAYOUT ONLY native band anchors and simple geometry lines; not final artwork','leftAnchor':'native/s01_01.png right230','rightAnchor':'native/s01_02.png x1039..1254','interior':'flat placeholder with grout directions extending actual LEFT230 endpoint positions','sourceResampled':False,'finalArt':False},indent=2)+'\n')
print(target)

