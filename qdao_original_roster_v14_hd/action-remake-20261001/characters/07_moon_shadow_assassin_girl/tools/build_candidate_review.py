"""Contact sheets for native-candidate visual QA; never edits source pixels."""
from pathlib import Path
import argparse,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('selection');p.add_argument('--group');args=p.parse_args()
doc=json.loads((R/args.selection).read_text(encoding='utf-8-sig'))
selected=doc['selected']
if isinstance(selected,list):selected={f['id']:f['selected'] for f in selected}
groups={}
for key,rel in selected.items():
    action,direction,num=key.split('_');groups.setdefault((action,direction),{})[num]=rel
for (action,direction),seq in groups.items():
    if args.group and args.group!=action+'-'+direction:continue
    count={'run':16,'attack':12,'hit':6,'cast':16}[action]
    sheet=Image.new('RGB',(1200,326*((count+3)//4)),(233,236,241));draw=ImageDraw.Draw(sheet)
    for i in range(count):
        num=f'{i+1:02d}';rel=seq.get(num,f'frames/{action}/{direction}/{num}.png')
        with Image.open(R/rel) as im:thumb=im.convert('RGBA').resize((300,300),Image.Resampling.LANCZOS)
        x=(i%4)*300;y=(i//4)*326;sheet.paste(thumb,(x,y),thumb)
        draw.text((x+5,y+302),f'{action}/{direction}/{num} '+('EDIT' if num in seq else 'retained'),fill=(20,25,35))
    target=(R/args.selection).parent/f'candidate-{action}-{direction}-contact.jpg';sheet.save(target,quality=94)
    print(target)
