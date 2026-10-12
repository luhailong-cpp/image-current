from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent.parent
D=R/'provenance/ground-contact-20261004'
rows=json.loads((D/'SWNW-candidate-map.json').read_text(encoding='utf-8'))
for d in ['SW','NW']:
 a=[x for x in rows if x['direction']==d]
 full=Image.new('RGB',(1280,1400),(210,217,220));feet=Image.new('RGB',(2000,1280),(210,217,220))
 for i,row in enumerate(a):
  p=R/row['sourceFile'];im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',im.size,(210,217,220,255));bg.alpha_composite(im)
  x=(i%4)*320;y=(i//4)*350
  full.paste(bg.convert('RGB').resize((320,320)),(x,y+25))
  label=f'{d}{row["targetFrame"]:02} {row["supportLeg"]} P{row["positionSegment"]}.{row["pairOrdinal"]}'
  ImageDraw.Draw(full).text((x+5,y+5),label,fill='black')
  x=(i%4)*500;y=(i//4)*320
  feet.paste(bg.convert('RGB').crop((260,685,760,980)),(x,y+25))
  ImageDraw.Draw(feet).text((x+5,y+5),label,fill='black')
 for kind,im in [('full',full),('feet',feet)]: im.save(D/f'{d}-position-{kind}.jpg',quality=95)
print('QA saved')

