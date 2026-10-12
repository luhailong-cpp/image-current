from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
BASE=Path(__file__).resolve().parents[1]
out=BASE/'review'/'grounding-S';out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
selected={f['frame']:BASE/f['file'] for f in json.loads((BASE/'review/review-run-S.json').read_text(encoding='utf-8'))['frames']}
for size in [240,480]:
    sheet=Image.new('RGB',(size*4,(size+28)*4),(37,42,44));d=ImageDraw.Draw(sheet)
    for i in range(16):
        x=(i%4)*size;y=(i//4)*(size+28);n=i+1;p=selected.get(n,BASE/'missing.png')
        d.text((x+6,y+4),f'S{n:02d}'+(' - MISSING' if not p.exists() else ' - pending'),font=font,fill='white')
        if p.exists():
            im=Image.open(p).convert('RGBA');im.thumbnail((size,size),Image.Resampling.LANCZOS)
            sheet.paste(im,(x,y+28),im)
        d.line((x,y+28+round(size*.92),x+size-1,y+28+round(size*.92)),fill=(160,115,74))
    sheet.save(out/f'contact-{size}.png')
print(str(out))
