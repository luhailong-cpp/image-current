"""Make visual review sheets from candidates without changing runtime."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops
import json, sys, hashlib
ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'provenance/contact-pairs-20261004'
selection={}
for name in ['east', 'south-east', 'north', 'south', 'west']:
    path=BATCH/(name+'-selection.json')
    if not path.exists(): continue
    data=json.loads(path.read_text(encoding='utf-8-sig'))
    for slot,chosen in data.items():
        assert slot not in selection, (slot,path)
        selection[slot]=chosen
directions=sys.argv[1:] or ['N','NE','E','SE','S','SW','W','NW']
metrics=[]
for direction in directions:
    sheet=Image.new('RGB',(1024,1128),'#e9e4d5');draw=ImageDraw.Draw(sheet)
    outdir=BATCH/direction;outdir.mkdir(exist_ok=True)
    for i in range(16):
        slot=f'run/{direction}/{i+1:02}'
        original=ROOT/'runtime'/(slot+'.png')
        path=ROOT/selection[slot]['source'] if slot in selection else original
        im=Image.open(path).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
        a=im.getchannel('A').point(lambda x:255 if x>=128 else 0).crop((0,0,1024,650))
        b=Image.open(original).getchannel('A').point(lambda x:255 if x>=128 else 0).crop((0,0,1024,650))
        union=sum(ImageChops.lighter(a,b).histogram()[128:])
        inter=sum(ImageChops.darker(a,b).histogram()[128:])
        metrics.append({'slot':slot,'source':path.relative_to(ROOT).as_posix(),
            'selected':slot in selection,'upperSilhouetteIoU':round(inter/union,4),
            'diagnosticOnly':True})
        small=im.resize((256,256),Image.Resampling.LANCZOS)
        x=i%4*256;y=i//4*282;sheet.paste(small,(x,y+24),small)
        draw.text((x+8,y+5),f'{direction} {i+1:02} '+('new' if slot in selection else 'retained'),fill='#173c31')
    sheet.save(outdir/'selected-contact.png')
(BATCH/'selected-registration-metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'directions':directions,'selected':len(selection),'runtimeWritten':False}))
