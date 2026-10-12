from pathlib import Path
from PIL import Image,ImageDraw
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy')
R=B.parent/'09_bamboo_archer_girl'
for d in ['W','SE']:
 c=Image.new('RGB',(960,1080),'#d5d9d2');q=ImageDraw.Draw(c)
 for i in range(1,17):
  im=Image.open(R/'runtime'/'run'/d/f'{i:02}.png');im.thumbnail((240,240));x=(i-1)%4*240;y=(i-1)//4*270;c.paste(im,(x,y),im);q.text((x+5,y+242),f'{d} {i:02}',fill='black')
 c.save(B/'review'/f'ref09-{d}-current.jpg',quality=95)

