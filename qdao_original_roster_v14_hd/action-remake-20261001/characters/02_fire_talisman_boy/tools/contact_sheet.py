from pathlib import Path
import argparse
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('action'); p.add_argument('direction'); args=p.parse_args()
source=(ROOT/'frames'/args.action/args.direction).resolve()
if not source.is_relative_to(ROOT): raise ValueError('outside role')
files=sorted(source.glob('*.png'))
size=320; columns=4; rows=(len(files)+columns-1)//columns
out=Image.new('RGB',(columns*size,max(1,rows)*(size+28)),(45,54,64)); draw=ImageDraw.Draw(out)
for i,f in enumerate(files):
    x=(i%columns)*size; y=(i//columns)*(size+28)
    for cy in range(0,size,20):
        for cx in range(0,size,20):
            c=185 if ((cx+cy)//20)%2 else 207
            draw.rectangle((x+cx,y+28+cy,x+cx+19,y+28+cy+19),fill=(c,c,c))
    im=Image.open(f).convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)
    out.paste(im,(x,y+28),im); draw.text((x+8,y+7),f'{args.action}/{args.direction}/{f.stem}',fill='white')
dest=ROOT/'previews'/f'{args.action}-{args.direction}-contact.png';dest.parent.mkdir(exist_ok=True)
out.save(dest); print(dest)
