"""Read-only, fixed-crop contact sheets for visible arm / grip review."""
from pathlib import Path
import json
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parent.parent
EV=ROOT/'provenance/foot-axis-20261004'
rows=json.loads((ROOT/'final-selection.json').read_text(encoding='utf-8-sig'))
for direction in ['E','W','N','NE','SE','S','SW','NW']:
    seq=sorted([r for r in rows if r['action']=='run' and r['direction']==direction], key=lambda r:r['frame'])
    for part in range(2):
        sheet=Image.new('RGB',(2048,984),(48,52,61))
        draw=ImageDraw.Draw(sheet)
        for i,row in enumerate(seq[part*8:part*8+8]):
            src=Image.open(ROOT/row['file']).convert('RGBA')
            crop=src.crop((140,290,908,982)).resize((512,461),Image.Resampling.LANCZOS)
            x=(i%4)*512;y=(i//4)*492
            sheet.paste(crop,(x,y+26),crop)
            draw.text((x+8,y+5),f"run {direction} {row['frame']:02d}",fill='white')
        sheet.save(EV/f'root-run-arms-{direction}-{part+1}.jpg',quality=94)
print('16 fixed-crop sheets generated for all 128 run frames')
