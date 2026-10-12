from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib

b=Path(__file__).resolve().parents[1]
out=b/'review/full-body-audit-hit-20261005'
out.mkdir(parents=True, exist_ok=True)
files=['runtime/hit/W/05.png','runtime/hit/W/06.png','staging/hit-W-06-v3.png']
sheet=Image.new('RGB',(1080,650),(42,46,52)); d=ImageDraw.Draw(sheet)
stats=[]
for i,f in enumerate(files):
    p=b/f; im=Image.open(p).convert('RGBA')
    im1024=im.resize((1024,1024),Image.Resampling.LANCZOS)
    row={'file':f,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':list(im.size),'edges':{}}
    for name,img in [('native',im),('export1024',im1024)]:
        a=img.getchannel('A'); w,h=img.size
        ring=list(a.crop((0,0,w,1)).getdata())+list(a.crop((0,h-1,w,h)).getdata())+list(a.crop((0,1,1,h-1)).getdata())+list(a.crop((w-1,1,w,h-1)).getdata())
        row['edges'][name]={'maxAlpha':max(ring),'alphaAbove128':sum(v>128 for v in ring)}
    stats.append(row)
    x=i*360
    d.text((x+8,8),f,fill='white')
    im240=im1024.resize((240,240),Image.Resampling.LANCZOS); sheet.paste(im240,(x+60,35),im240)
    crop=im1024.crop((220,690,790,1024)).resize((342,200),Image.Resampling.LANCZOS)
    sheet.paste(crop,(x+9,315),crop)
    d.text((x+8,285),'Common leg crop; no repositioning',fill='white')
    d.text((x+8,540),'Native/1024 edge alpha >128: '+str(row['edges']['native']['alphaAbove128'])+'/'+str(row['edges']['export1024']['alphaAbove128']),fill='white')
sheet.save(out/'hit-W-06-v3-compare.jpg',quality=97)
(out/'hit-W-06-v3-validation.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(stats,ensure_ascii=False,indent=2))
