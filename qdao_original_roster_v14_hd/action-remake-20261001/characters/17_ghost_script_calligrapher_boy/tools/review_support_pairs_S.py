from pathlib import Path
from PIL import Image,ImageDraw
b=Path(__file__).resolve().parents[1]
vs=[3,2,1,4,3,5,7,5,3,2,3,2,3,3,6,5]
for mode in ['240','feet']:
 w,h=(240,265) if mode=='240' else (330,290)
 out=Image.new('RGB',(4*w,4*h),(220,222,220));d=ImageDraw.Draw(out)
 for j,v in enumerate(vs):
  key=f'run-S-{j+1:02}-v{v}';im=Image.open(b/'staging'/(key+'.png')).convert('RGBA')
  if mode=='feet':im=im.crop((320,720,1000,1254))
  im.thumbnail((w,h-25));x=j%4*w+(w-im.width)//2;y=j//4*h+25;out.paste(im,(x,y),im);d.text((j%4*w+5,j//4*h+5),key,fill='black')
 out.save(b/'review'/f'support-pairs-S-current-{mode}.png')

