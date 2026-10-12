"""Inspection preview only; no final art files are changed."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw,ImageFont

z=Path(__file__).resolve().parent
index=json.loads((z/'delivery-20261011/index.json').read_text(encoding='utf-8-sig'))
rows={r['tile']:r for r in index['tiles']}
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
out=z/'review-notes'/('six-core-preview-'+stamp); out.mkdir(parents=True)
tile_size=512
canvas=Image.new('RGB',(1536,1608),(27,32,34))
draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
draw.text((18,12),'SOUTHEAST: 6 / 64 candidates | 0 formally accepted',font=font,fill=(245,245,240))
draw.text((18,43),'PREVIEW ONLY - scaled 1:8; rows 13-15, columns 13-15; missing tiles remain blank',font=small,fill=(191,205,209))
sources=[]
for r in range(13,16):
    for c in range(13,16):
        name=f'r{r:02d}_c{c:02d}'
        x,y=(c-13)*tile_size,72+(r-13)*tile_size
        row=rows[name]
        if row['candidate']:
            p=Path(row['candidate']['path'])
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            assert digest==row['candidate']['sha256']
            im=Image.open(p).convert('RGB'); assert im.size==(4096,4096)
            canvas.paste(im.resize((512,512),Image.Resampling.LANCZOS),(x,y))
            sources.append({'tile':name,'path':str(p),'sha256':digest})
        else:
            draw.rectangle((x,y,x+511,y+511),fill=(45,50,52),outline=(78,88,93))
            draw.text((x+170,y+246),'NOT STARTED',font=font,fill=(139,150,154))
        draw.rectangle((x+8,y+8,x+122,y+35),fill=(25,30,34))
        draw.text((x+15,y+11),name,font=small,fill=(255,255,255))
preview=out/'six-core-preview-only.png'; canvas.save(preview)
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'previewOnly':True,'previewScale':0.125,'sources':sources,'finalArtModified':False,'formalAccepted':False,'preview':str(preview)}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(manifest))
