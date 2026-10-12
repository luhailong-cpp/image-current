"""Read-only art QA layouts; never modifies sprite pixels or runtime images."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1]; out=R/'hand-review-20261005';out.mkdir(exist_ok=True)
fontpath='C:/Windows/Fonts/arial.ttf'
from PIL import ImageFont
font=ImageFont.truetype(fontpath,20)
manifest=[]
for direction in ['E','SE','S','SW']:
 for start in [1,9]:
  canvas=Image.new('RGB',(1200,1320),(234,230,217));dr=ImageDraw.Draw(canvas)
  for j,n in enumerate(range(start,start+8)):
   p=R/f'runtime/run/{direction}/{n:02}.png';im=Image.open(p).convert('RGBA')
   # Fixed crop for legible shoulder-to-grip QA, display only.
   crop=im.crop((100,290,950,700));crop.thumbnail((580,286),Image.Resampling.LANCZOS)
   x=(j%2)*600+10;y=(j//2)*330+30;canvas.paste(crop,(x,y),crop)
   dr.text((x,y-24),f'{direction} {n:02}  shoulder / wrist / grip',fill=(28,53,46),font=font)
   manifest.append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  canvas.save(out/f'qa-hands-{direction}-{start:02}.jpg',quality=94)
(out/'qa-inputs.json').write_text(json.dumps({'displayOnly':True,'fixedCrop':[100,290,950,700],'files':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
print('8 inspection sheets from 64 current run frames')
