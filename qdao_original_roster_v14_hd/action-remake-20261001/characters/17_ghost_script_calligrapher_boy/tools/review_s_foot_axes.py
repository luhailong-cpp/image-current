from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
BASE=Path(__file__).resolve().parents[1]
selected={f['frame']:BASE/f['file'] for f in json.loads((BASE/'review/review-run-S.json').read_text(encoding='utf-8'))['frames']}
sheet=Image.new('RGB',(400*4,350*4),(46,50,52));draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for n in range(1,17):
 p=selected[n];im=Image.open(p).convert('RGBA').crop((380,830,880,1230));im=im.resize((400,320),Image.Resampling.LANCZOS);x=((n-1)%4)*400;y=((n-1)//4)*350;sheet.paste(im,(x,y+30),im);draw.text((x+8,y+3),p.stem,font=font,fill='white')
out=BASE/'review'/'grounding-S'/'foot-axes-current.png';sheet.save(out);print(str(out))
