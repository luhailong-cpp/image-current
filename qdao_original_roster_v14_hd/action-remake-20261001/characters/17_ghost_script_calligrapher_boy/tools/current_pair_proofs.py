from pathlib import Path
from PIL import Image,ImageDraw
import json
B=Path(__file__).resolve().parents[1]
choices={'W':[3,1,2,5,3,5,6,5,6,4,6,5,4,5,6,5],'SE':[3,2,2,5,3,6,3,3,4,3,1,5,5,4,4,3]}
for d,vs in choices.items():
 c=Image.new('RGB',(1280,1440),'#d5d9d2');q=ImageDraw.Draw(c);rows=[]
 for i,v in enumerate(vs,1):
  key=f'run-{d}-{i:02}-v{v}';p=B/'staging'/f'{key}.png';im=Image.open(p).convert('RGBA');a=im.getchannel('A');w,h=im.size
  edges={s:sum(a.crop(r).histogram()[129:]) for s,r in {'l':(0,0,1,h),'r':(w-1,0,w,h),'t':(0,0,w,1),'b':(0,h-1,w,h)}.items()}
  rows.append({'key':key,'edges':edges})
  im.thumbnail((320,320));x=(i-1)%4*320;y=(i-1)//4*360;c.paste(im,(x,y),im);q.text((x+5,y+327),key,fill='black')
 c.save(B/'review'/f'latest-pairs-{d}.jpg',quality=95)
 print(json.dumps({'direction':d,'edges':rows}))
keys=['run-W-01-v2','run-W-01-v3','run-W-09-v5','run-W-09-v6','run-W-06-v5','run-W-06-v6','run-W-14-v4','run-W-14-v5']
c=Image.new('RGB',(1280,720),'#d5d9d2');q=ImageDraw.Draw(c)
for j,k in enumerate(keys):
 im=Image.open(B/'staging'/f'{k}.png');im.thumbnail((320,320));x=j%4*320;y=j//4*360;c.paste(im,(x,y),im);q.text((x+5,y+327),k,fill='black')
c.save(B/'review'/'latest-W-alternates.jpg',quality=95)

