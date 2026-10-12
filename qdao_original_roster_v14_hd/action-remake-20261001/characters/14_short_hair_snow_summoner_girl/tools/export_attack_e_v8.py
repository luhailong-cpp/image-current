from pathlib import Path
from PIL import Image,ImageDraw
import sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from export_frame import run
for n in range(1,13):
 suffix='v7-arm' if n in [4,5] else 'v9-pin' if n==8 else 'v8-arm'
 run(R/'attack/staging'/f'attack-E-{n:02d}-{suffix}.png',R/'attack/E'/f'{n:02d}.png')
out=Image.new('RGB',(1024,1260),(235,236,231));d=ImageDraw.Draw(out)
for i in range(1,13):
 im=Image.open(R/'attack/E'/f'{i:02d}.png').convert('RGBA')
 crop=im.crop((0,680,1024,1024)).resize((512,172))
 x=((i-1)%2)*512;y=((i-1)//2)*210
 out.paste(crop,(x,y+25),crop)
 for j in range(0,1025,100):
  xx=x+j/2;d.line((xx,y+18,xx,y+196),fill=(195,203,195));d.text((xx+1,y+3),str(j),fill=(35,55,50))
 d.text((x+5,y+197),f'attack/E/{i:02d}, source y680..1024',fill=(30,50,45))
out.save(R/'preview/attack-E-registration-grid.jpg',quality=95)

