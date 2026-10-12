"""Read-only diagnostic sheets from current formal run PNGs; never alters sprites."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse
B=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('directions',nargs='+');args=p.parse_args()
for d in args.directions:
    full=Image.new('RGB',(1120,1200),'#e2e5db');feet=Image.new('RGB',(1440,1080),'#e2e5db')
    fd=ImageDraw.Draw(full);pd=ImageDraw.Draw(feet)
    for n in range(1,17):
        f=B/f'runtime/run/{d}/{n:02d}.png'
        with Image.open(f) as im:
            tile=im.resize((280,280),Image.Resampling.LANCZOS)
            x=((n-1)%4)*280;y=((n-1)//4)*300
            full.paste(tile,(x,y+20),tile);fd.text((x+8,y+4),f'{d} {n:02d}',fill='#182927')
            crop=im.crop((200,610,920,1024)).resize((360,207),Image.Resampling.LANCZOS)
            x=((n-1)%4)*360;y=((n-1)//4)*270
            feet.paste(crop,(x,y+30),crop);pd.text((x+8,y+5),f'{d} {n:02d} fixed-crop x200:920 y610:1024',fill='#182927')
    target=B/f'review/axis-W-SE';target.mkdir(parents=True,exist_ok=True)
    full.save(target/f'{d}-whole.jpg',quality=94);feet.save(target/f'{d}-feet.jpg',quality=94)
    print(str(target/f'{d}-whole.jpg'))
