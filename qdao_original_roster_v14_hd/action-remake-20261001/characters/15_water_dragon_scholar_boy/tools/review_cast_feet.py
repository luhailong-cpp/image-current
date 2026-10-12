from pathlib import Path
from PIL import Image,ImageDraw
import json
b=Path(__file__).resolve().parents[1]
d=json.loads((b/'audit/cast-selection.json').read_text(encoding='utf-8-sig'))
print(type(d),d.keys() if isinstance(d,dict) else len(d))
for di in ['E','W']:
 fs=sorted([f for f in d['frames'] if f['direction']==di],key=lambda f:f['frame'])
 sheet=Image.new('RGB',(1280,800),(25,35,45));dr=ImageDraw.Draw(sheet)
 for f in fs:
  im=Image.open(b/f['source']).convert('RGBA')
  feet=im.crop((200,960,1100,1254)).resize((320,105))
  j=f['frame']-1;x=j%4*320;y=j//4*200
  sheet.paste(feet,(x,y+35),feet);dr.text((x+6,y+10),f"{di}{f['frame']:02d} {f['source'].split('/')[-1]}",fill='white')
 sheet.save(b/'audit'/f'cast-foot-contact-{di}.png')

