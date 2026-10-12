"""Produce inspection-only sheets of current runtime; never rewrite sprite pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,json,hashlib
B=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('action');p.add_argument('directions',nargs='+');args=p.parse_args()
folder=B/f'review/full-body-audit-{args.action}-20261005';folder.mkdir(parents=True,exist_ok=True)
rows=[]
for direction in args.directions:
    files=sorted((B/'runtime'/args.action/direction).glob('*.png'))
    height=((len(files)+3)//4)*300
    full=Image.new('RGB',(1120,height),'#e2e5db');hands=Image.new('RGB',(1440,height),'#e2e5db');legs=Image.new('RGB',(1440,height),'#e2e5db')
    df=ImageDraw.Draw(full);dh=ImageDraw.Draw(hands);dl=ImageDraw.Draw(legs)
    for i,f in enumerate(files):
        with Image.open(f) as im:
            tile=im.resize((280,280),Image.Resampling.LANCZOS);x=i%4*280;y=i//4*300
            full.paste(tile,(x,y+20),tile);df.text((x+5,y+4),f'{direction} {f.stem}',fill='black')
            for dest,draw,box,name in [(hands,dh,(60,250,1000,750),'upper-body'),(legs,dl,(200,620,960,1024),'legs')]:
                crop=im.crop(box);crop.thumbnail((360,270),Image.Resampling.LANCZOS);x=i%4*360;y=i//4*300
                dest.paste(crop,(x,y+24),crop);draw.text((x+5,y+4),f'{direction} {f.stem} {name}',fill='black')
        rows.append({'slot':f'{args.action}-{direction}-{f.stem}','file':f.relative_to(B).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    for name,im in [('whole',full),('hands',hands),('legs',legs)]:im.save(folder/f'{direction}-{name}.jpg',quality=96)
(folder/'input-sha256.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'action':args.action,'frames':len(rows),'folder':str(folder)}))
