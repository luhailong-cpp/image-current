"""Read-only full-canvas proof sheets; never exports or modifies sprite assets."""
from pathlib import Path
from PIL import Image, ImageDraw
import re, argparse
BASE=Path(__file__).resolve().parents[1]
def build(action, direction):
    files={}
    for p in (BASE/'staging').glob(f'{action}-{direction}-*-v*.png'):
        m=re.match(r'.*-(\d+)-v(\d+)\.png',p.name)
        n,v=map(int,m.groups())
        if n not in files or v>files[n][0]: files[n]=(v,p)
    count={'run':16,'cast':16,'attack':12,'hit':6}[action]
    sheet=Image.new('RGB',(4*320,((count+3)//4)*350),(33,43,44))
    dr=ImageDraw.Draw(sheet)
    for n in range(1,count+1):
        x=((n-1)%4)*320;y=((n-1)//4)*350
        if n in files:
            p=files[n][1];im=Image.open(p).convert('RGBA');im.thumbnail((310,310))
            sheet.paste(im,(x+(320-im.width)//2,y+25),im)
            dr.text((x+10,y+5),p.stem,fill='white')
        else:dr.text((x+10,y+5),f'{action}-{direction}-{n:02} MISSING',fill='white')
    out=BASE/'preview'/f'proof-{action}-{direction}.jpg';sheet.save(out,quality=94)
    print(out)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action');p.add_argument('direction');a=p.parse_args();build(a.action,a.direction)
