from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
from export_frame import run
ROOT=Path(__file__).resolve().parents[1]
for d in ['N','NE','NW']:
 out=ROOT/'run'/d
 out.mkdir(exist_ok=True)
 frames=[]
 for i in range(1,17):
  variants=list((ROOT/'run/staging').glob(f'run-{d}-{i:02d}-v*.png'))
  if not variants:continue
  src=max(variants,key=lambda p:int(p.stem.split('-v')[-1]))
  dst=out/f'{i:02d}.png'
  run(src,dst)
  frames.append((i,dst))
 if not frames:continue
 sheet=Image.new('RGB',(1200,1320),'#262d3b')
 draw=ImageDraw.Draw(sheet)
 for i,p in frames:
  im=Image.open(p).convert('RGBA').resize((300,300))
  x=((i-1)%4)*300;y=((i-1)//4)*330
  sheet.paste(im,(x,y),im)
  draw.text((x+8,y+300),f'{d}/{i:02d}',fill='white')
 sheet.save(out/'contact.jpg',quality=92)
 print(d,len(frames))
