from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
for direct in ('E','W'):
    out=Image.new('RGB',(1024,630),(235,236,231));d=ImageDraw.Draw(out)
    for i in range(1,7):
        im=Image.open(R/'hit'/direct/f'{i:02d}.png').convert('RGBA')
        crop=im.crop((0,680,1024,1024)).resize((512,172))
        x=((i-1)%2)*512;y=((i-1)//2)*210
        out.paste(crop,(x,y+25),crop)
        for j in range(0,1025,100):
            xx=x+j/2;d.line((xx,y+18,xx,y+196),fill=(195,203,195));d.text((xx+1,y+3),str(j),fill=(35,55,50))
        d.text((x+5,y+197),f'hit/{direct}/{i:02d}, source y680..1024',fill=(30,50,45))
    out.save(R/'preview'/f'hit-{direct}-registration-grid.jpg',quality=95)
