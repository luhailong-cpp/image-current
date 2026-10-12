from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys
R=Path(__file__).resolve().parents[1]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for direction in sys.argv[1:] or ['E','SE']:
 order=[7,8,9,10,11,12,13,14,15,16,1,2,3,4,5,6]
 out=Image.new('RGB',(1280,770),'#f5efdf');d=ImageDraw.Draw(out)
 for i,n in enumerate(order):
  x=i%8*160;y=i//8*380
  im=Image.open(R/'frames'/'run'/direction/f'{n:02}.png').convert('RGBA')
  small=im.resize((160,160),Image.Resampling.LANCZOS);out.paste(small,(x,y+26),small)
  # Fixed identical lower-half crop for QA only; no manipulation of formal sprite.
  lower=im.crop((0,580,1024,1024)).resize((160,150),Image.Resampling.LANCZOS);out.paste(lower,(x,y+202),lower)
  d.text((x+6,y+4),f'{direction} {n:02} pair{i%8//2+1}',font=font,fill='#21443d')
 out.save(R/'previews'/f'run-{direction}-position-pairs-review.png')
print('contact previews written')
