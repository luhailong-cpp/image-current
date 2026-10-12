from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
b=Path(__file__).resolve().parents[1];out=b/'review/full-body-audit-hit-20261005';out.mkdir(parents=True,exist_ok=True);rows=[]
for dr in ['E','W']:
 sheet=Image.new('RGB',(1560,590),(42,46,52));d=ImageDraw.Draw(sheet)
 for n in range(1,7):
  p=b/'runtime/hit'/dr/f'{n:02d}.png';im=Image.open(p).convert('RGBA')
  x=(n-1)*260;t=im.resize((240,240),Image.Resampling.LANCZOS);sheet.paste(t,(x+10,25),t);d.text((x+10,6),f'hit {dr} {n:02d} whole240',fill='white')
  crop=im.crop((180,690,890,1024)).resize((260,122),Image.Resampling.LANCZOS);sheet.paste(crop,(x,285),crop);d.text((x+8,268),'common leg crop',fill='white')
  hands=im.crop((180,440,840,735)).resize((260,116),Image.Resampling.LANCZOS);sheet.paste(hands,(x,443),hands);d.text((x+8,425),'common shoulder / wrist crop',fill='white')
  rows.append({'action':'hit','direction':dr,'frame':n,'file':p.relative_to(b).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size)})
 sheet.save(out/f'hit-{dr}-neighbors.jpg',quality=97)
(out/'runtime-evidence.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)

