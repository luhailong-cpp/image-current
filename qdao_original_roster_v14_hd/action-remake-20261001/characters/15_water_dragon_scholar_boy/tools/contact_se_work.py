from pathlib import Path
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[1]
out=Image.new('RGB',(1280,4*348),(43,50,61)); d=ImageDraw.Draw(out)
for n in range(1,17):
 key=f'run-SE-{n:02}-v'+('2' if n in [1,9] else '1')
 p=B/'sources/new'/f'{key}.png'
 x=((n-1)%4)*320;y=((n-1)//4)*348
 d.text((x+8,y+6),key,fill='white')
 if p.exists():
  im=Image.open(p).convert('RGBA');im.thumbnail((316,316));out.paste(im,(x,y+28),im)
out.save(B/'preview/run-SE-work-contact.jpg')
