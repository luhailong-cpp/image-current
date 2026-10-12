from pathlib import Path
from PIL import Image,ImageDraw
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/seam-qa/independent-20261010/repair-candidates');a=Image.open(D/'r12c08-rail-v2-actual-core-preview/input-actual-cores.png');b=Image.open(D/'r12c08-rail-joint-v4.png')
out=Image.new('RGB',(1024,580),'white');draw=ImageDraw.Draw(out)
for i,x in enumerate([600,650,750,850]):
 p=a.copy();p.paste(b.crop((320,125,x,650)),(320,125));crop=p.crop((x-128,125,x+128,675));out.paste(crop,(i*256,30));draw.text((i*256+10,10),str(x),fill='black')
out.save(D/'r12c08-rail-v4-cut-options.png')

