from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
b=Path(__file__).resolve().parents[1]
versions=json.loads((b/'review/grounded-pair-working-selection.json').read_text())
metrics=[]
for direction,vs in versions.items():
    sheet=Image.new('RGB',(8*240,2*270),(35,41,45))
    d=ImageDraw.Draw(sheet)
    for i,v in enumerate(vs,1):
        key=f'run-{direction}-{i:02d}-v{v}'
        p=b/'staging'/f'{key}.png'
        im=Image.open(p).convert('RGBA')
        a=im.getchannel('A');w,h=im.size
        sides={'left':sum(x>128 for x in a.crop((0,0,1,h)).getdata()),'right':sum(x>128 for x in a.crop((w-1,0,w,h)).getdata()),'top':sum(x>128 for x in a.crop((0,0,w,1)).getdata()),'bottom':sum(x>128 for x in a.crop((0,h-1,w,h)).getdata())}
        metrics.append({'key':key,'width':w,'height':h,'edgeAlphaGT128':sides,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        thumb=im.resize((240,240),Image.Resampling.LANCZOS)
        x=(i-1)%8*240;y=(i-1)//8*270
        sheet.paste(thumb,(x,y),thumb)
        d.text((x+5,y+245),key,fill=(240,240,240))
    sheet.save(b/'review'/f'grounded-pair-working-{direction}-240.png')
(b/'review'/'grounded-pair-working-metrics.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps([m for m in metrics if any(m['edgeAlphaGT128'].values())]))

