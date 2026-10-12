from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
out=Image.new('RGB',(1280,1376),(232,235,231));d=ImageDraw.Draw(out)
for i in range(1,17):
    im=Image.open(R/'run'/'E'/f'{i:02d}.png').convert('RGBA')
    x=((i-1)%4)*320;y=((i-1)//4)*344
    th=im.resize((320,320));out.paste(th,(x,y),th)
    for j in (400,500,600,700,800):
        xx=x+j*320/1024;d.line((xx,y+208,xx,y+320),fill=(162,189,173));d.text((xx,y+210),str(j),fill=(45,76,68))
    d.line((x,y+980*320/1024,x+320,y+980*320/1024),fill=(186,129,102))
    d.text((x+8,y+324),f'run/E/{i:02d}',fill=(30,45,40))
out.save(R/'preview'/'run-E-registration-grid.jpg',quality=95)
