from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib
BASE=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
cell=384
margin=12
sheet=Image.new('RGB',(4*(cell+margin)+margin,4*(cell+46+margin)+margin),(222,231,223))
draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
report=[]
for n in range(1,17):
    name=f'{n:02d}'
    p=BASE/'runtime/cast/W'/f'{name}.png'
    im=Image.open(p).convert('RGBA')
    a=im.getchannel('A'); bbox=a.getbbox()
    opaque_bbox=a.point(lambda v:255 if v>=128 else 0).getbbox()
    sha=hashlib.sha256(p.read_bytes()).hexdigest()
    rec=json.loads((BASE/'records/cast/W'/f'{name}.generation.json').read_text(encoding='utf-8'))
    report.append({'frame':n,'file':str(p),'size':im.size,'alphaExtrema':a.getextrema(),'alphaBounds':bbox,'opaqueBounds':opaque_bbox,'sha256':sha,'recordShaMatches':rec['sha256']==sha})
    x=margin+(n-1)%4*(cell+margin); y=margin+(n-1)//4*(cell+46+margin)
    tile=Image.new('RGBA',(cell,cell),(73,87,81,255))
    tile.alpha_composite(im.resize((cell,cell),Image.Resampling.LANCZOS))
    sheet.paste(tile.convert('RGB'),(x,y))
    draw.text((x+8,y+cell+10),f'cast W {name}  /  45 ms'+('  RELEASE' if n==11 else ''),font=font,fill=(26,50,43))
sheet.save(OUT/'contact.png')
result={'expected':16,'present':len(report),'uniqueSha256':len(set(r['sha256'] for r in report)),'allRecordShaMatches':all(r['recordShaMatches'] for r in report),'frames':report,'contact':'qa/cast/W/contact.png','purpose':'static review only, not playback verification'}
(OUT/'technical-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result))
