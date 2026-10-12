from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];W=R/'work/full-limb-cast-ne-nw';W.mkdir(exist_ok=True)
for action,d in [('cast','E'),('cast','W'),('run','NE'),('run','NW')]:
    frames=[Image.open(R/f'frames/{action}/{d}/{f:02d}.png').convert('RGBA') for f in range(1,17)]
    can=Image.new('RGB',(1600,1728),(36,52,64));draw=ImageDraw.Draw(can)
    for i,im in enumerate(frames):
        x=i%4*400;y=i//4*432;pic=im.resize((400,400),Image.Resampling.LANCZOS);can.paste(pic,(x,y),pic);draw.text((x+10,y+406),f'{action} {d} {i+1:02}',fill='white')
    can.save(W/f'{action}-{d}-contact.jpg',quality=97)
print(str(W))
