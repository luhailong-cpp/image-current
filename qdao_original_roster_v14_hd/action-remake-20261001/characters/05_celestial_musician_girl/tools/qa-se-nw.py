from pathlib import Path
import json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent.parent
selection=json.loads((root/'provenance/run/selection-SE-NW.json').read_text(encoding='utf-8'))
for direction in ['SE','NW']:
    sheet=Image.new('RGB',(1280,1440),(52,61,71))
    dr=ImageDraw.Draw(sheet)
    for frame in range(1,17):
        chosen=next((r for r in selection if r['direction']==direction and r['frame']==frame),None)
        if not chosen: continue
        p=root/chosen['file']
        im=Image.open(p).convert('RGBA').resize((320,320))
        x=((frame-1)%4)*320;y=((frame-1)//4)*360
        sheet.paste(im,(x,y),im)
        dr.line((x,y+294,x+320,y+294),fill=(80,140,110))
        dr.text((x+10,y+328),p.stem,fill='white')
    sheet.save(root/'tools'/f'qa-{direction}.jpg')
