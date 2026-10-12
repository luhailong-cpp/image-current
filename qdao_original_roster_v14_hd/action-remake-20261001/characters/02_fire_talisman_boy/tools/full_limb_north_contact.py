from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
for d in ['N','W']:
 c=Image.new('RGB',(2048,2176),(235,234,225)); dr=ImageDraw.Draw(c)
 for f in range(1,17):
  im=Image.open(R/f'frames/run/{d}/{f:02}.png').convert('RGBA').resize((512,512),Image.Resampling.LANCZOS)
  x=((f-1)%4)*512;y=((f-1)//4)*544
  c.paste(im,(x,y),im);dr.text((x+10,y+518),f'{d}{f:02}',fill=(0,0,0))
 c.save(R/f'reviews/full-limb-{d}-contact-20261005.jpg',quality=96)
 for start in [1,9]:
  c=Image.new('RGB',(1024,1148),(235,234,225));dr=ImageDraw.Draw(c)
  for j,f in enumerate(range(start,start+8)):
   im=Image.open(R/f'frames/run/{d}/{f:02}.png').convert('RGBA').crop((0,300,1024,810)).resize((512,255),Image.Resampling.LANCZOS)
   x=j%2*512;y=j//2*287;c.paste(im,(x,y),im);dr.text((x+5,y+260),f'{d}{f:02}',fill=(0,0,0))
  c.save(R/f'reviews/full-limb-{d}-arms-{start:02}-{start+7:02}-20261005.jpg',quality=96)
print('full canvas contact sheets and arm QA sheets created')

