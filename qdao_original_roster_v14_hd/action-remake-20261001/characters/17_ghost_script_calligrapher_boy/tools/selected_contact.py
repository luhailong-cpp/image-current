from pathlib import Path
from PIL import Image, ImageDraw
import json
b=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy')
m=json.loads((b/'preview/manifest-preview.json').read_text(encoding='utf-8'))
for d in ['E','N','S','W','NE','NW','SW','SE']:
 seq=[s for s in m['slots'] if s['action']=='run' and s['direction']==d]
 canvas=Image.new('RGB',(960,1080),'#d5d9d2');draw=ImageDraw.Draw(canvas)
 for n,s in enumerate(seq):
  if s['selected'] is None: continue
  p=b/'preview'/s['selected']['path']
  with Image.open(p) as im:
   im.thumbnail((240,240))
   canvas.paste(im,(n%4*240,n//4*270),im)
  draw.text((n%4*240+8,n//4*270+244),s['selected']['key'],fill='#111111')
 canvas.save(b/'preview'/f'selected-run-{d}.jpg',quality=94)
print('Selected full-canvas proof sheets refreshed.')

