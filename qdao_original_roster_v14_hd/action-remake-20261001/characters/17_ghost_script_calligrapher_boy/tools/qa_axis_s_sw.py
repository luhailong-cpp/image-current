from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
b=Path(__file__).resolve().parents[1]
out=b/'review'/'axis-S-SW';out.mkdir(parents=True,exist_ok=True)
proof=[]
for dr in ['S','SW']:
 sheet=Image.new('RGB',(1040,1120),(40,44,50));sd=ImageDraw.Draw(sheet)
 for start in [1,9]:
  legs=Image.new('RGB',(1600,600),(55,59,65));ld=ImageDraw.Draw(legs)
  for n in range(start,start+8):
   p=b/'runtime'/'run'/dr/f'{n:02d}.png';im=Image.open(p).convert('RGBA')
   proof.append({'direction':dr,'frame':n,'file':str(p.relative_to(b)).replace('\\','/'),'size':list(im.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
   crop=im.crop((230,620,880,1024)).resize((400,249),Image.Resampling.LANCZOS);i=n-start;x=(i%4)*400;y=(i//4)*300+27;legs.paste(crop,(x,y),crop);ld.text((x+12,y-20),f'{dr} {n:02d} actual runtime / common leg crop',fill='white')
   thumb=im.resize((240,240),Image.Resampling.LANCZOS);j=n-1;x=(j%4)*260+10;y=(j//4)*280+28;sheet.paste(thumb,(x,y),thumb);sd.text((x,y-20),f'{dr} {n:02d}',fill='white')
  legs.save(out/f'{dr}-legs-{start:02d}-{start+7:02d}.jpg',quality=97)
 sheet.save(out/f'{dr}-full-240.jpg',quality=97)
(out/'runtime-evidence.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)

