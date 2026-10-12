from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
S=R.parents[2]/'recovery-20260921'/'14-delivery-preview'/'assets'/'idle'
out=Image.new('RGB',(1280,688),(234,237,233));d=ImageDraw.Draw(out)
for i,direct in enumerate(('N','NE','E','SE','S','SW','W','NW')):
    p=S/f'{direct}.png'
    im=Image.open(p).convert('RGBA')
    x=(i%4)*320;y=(i//4)*344;t=im.resize((320,320));out.paste(t,(x,y),t)
    for j in (300,400,500,600,700):
        xx=x+j*320/1024;d.line((xx,y+214,xx,y+315),fill=(173,194,180));d.text((xx,y+214),str(j),fill=(45,76,68))
    d.text((x+8,y+324),direct,fill=(30,45,40))
out.save(R/'preview'/'idle-registration-grid.jpg',quality=95)
