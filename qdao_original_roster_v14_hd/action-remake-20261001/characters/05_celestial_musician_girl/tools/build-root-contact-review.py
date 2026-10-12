from pathlib import Path
from PIL import Image,ImageDraw
import json,sys
root=Path(__file__).resolve().parent.parent
registered='--registered' in sys.argv
rows=json.loads((root/('registered-selection.json' if registered else 'candidate-selection.json')).read_text(encoding='utf-8-sig'))
for action,direction in [('run',d) for d in ['N','NE','E','SE','S','SW','W','NW']]+[(a,d) for a in ['hit','attack','cast'] for d in ['E','W']]:
    items=[e for e in rows if e['action']==action and e['direction']==direction]
    width=320; height=352
    sheet=Image.new('RGB',(width*4,height*((len(items)+3)//4)),(210,216,219))
    draw=ImageDraw.Draw(sheet)
    for n,e in enumerate(items):
        im=Image.open(root/e['file']).convert('RGBA');im.thumbnail((width,width),Image.Resampling.LANCZOS)
        x=(n%4)*width;y=(n//4)*height
        sheet.paste(im,(x,y),im)
        draw.text((x+8,y+325),f"{action}-{direction}-{e['frame']:02} {Path(e['file']).name}",fill=(20,25,29))
    dest=root/'preview'/f'qa-{action}-{direction}-{"registered" if registered else "current"}.jpg';sheet.save(dest,quality=96)
    print(dest)

