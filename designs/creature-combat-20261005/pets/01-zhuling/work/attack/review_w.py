from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
B=Path(r'D:/work/image/designs/creature-combat-20261005/pets/01-zhuling')
Q=B/'qa/attack/W';Q.mkdir(parents=True,exist_ok=True)
technical=[]
for part in range(3):
 sheet=Image.new('RGB',(1536,1584),(48,57,62));d=ImageDraw.Draw(sheet)
 for i in range(4):
  n=part*4+i+1;p=B/f'runtime/attack/W/{n:02}.png';im=Image.open(p).convert('RGBA');a=im.getchannel('A');w,h=im.size
  x=(i%2)*768;y=(i//2)*792
  tile=Image.new('RGBA',(768,768),(48,57,62,255));tile.alpha_composite(im.resize((768,768),Image.Resampling.LANCZOS));sheet.paste(tile.convert('RGB'),(x,y));d.text((x+20,y+768),f'attack W {n:02} / 12 | 30ms',fill=(255,255,255))
  technical.append({'frame':n,'file':p.relative_to(B).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':[w,h],'alphaExtrema':a.getextrema(),'alphaBBox':a.getbbox(),'solidBBox32':a.point(lambda v:255 if v>32 else 0).getbbox()})
 sheet.save(Q/f'contact-{part+1}.jpg',quality=95)
(Q/'technical-review.json').write_text(json.dumps({'frames':technical,'uniqueShaCount':len(set(x['sha256'] for x in technical)),'all1024RGBA':all(x['size']==[1024,1024] and x['alphaExtrema']==(0,255) for x in technical)},indent=2),encoding='utf-8')
print('W12 contacts and technical checks written')
