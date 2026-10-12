from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[1];out=b/'audit/cast-final-review';out.mkdir(exist_ok=True)
d=json.loads((b/'audit/cast-selection.json').read_text(encoding='utf-8'))
errors=[]
for di in ['E','W']:
 fs=sorted([f for f in d['frames'] if f['direction']==di],key=lambda f:f['frame']);frames=[]
 sheet=Image.new('RGB',(1120,1200),(28,37,48));draw=ImageDraw.Draw(sheet)
 for f in fs:
  p=b/f['source'];im=Image.open(p).convert('RGBA')
  if im.size!=(1254,1254):errors.append(p.name+' dimensions')
  if hashlib.sha256(p.read_bytes()).hexdigest()!=f['sha256']:errors.append(p.name+' SHA')
  if not(b/f['generationRecord']).exists():errors.append(p.name+' record')
  if '-foot-' not in p.name and '-ground-' not in p.name:errors.append(p.name+' unrepaired')
  canvas=Image.new('RGBA',(1024,1024));canvas.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
  view=Image.new('RGBA',(384,420),(28,37,48,255));view.alpha_composite(canvas.resize((384,384)))
  dr=ImageDraw.Draw(view);dr.line((0,353,384,353),fill=(130,90,65));dr.text((8,390),f"CAST {di}{f['frame']:02d}",fill='white');frames.append(view.convert('RGBA'))
  x=(f['frame']-1)%4*280;y=(f['frame']-1)//4*300
  panel=Image.new('RGBA',(280,280),(28,37,48,255));panel.alpha_composite(canvas.resize((280,280)))
  sheet.paste(panel.convert('RGB'),(x,y));draw.line((x,y+258,x+280,y+258),fill=(145,95,65));draw.text((x+8,y+279),f"{di}{f['frame']:02d} {p.name}",fill='white')
 sheet.save(out/f'{di}-contact.png')
 frames[0].save(out/f'{di}-normal.apng',save_all=True,append_images=frames[1:],duration=45,loop=0,format='PNG')
 frames[0].save(out/f'{di}-slow.apng',save_all=True,append_images=frames[1:],duration=180,loop=0,format='PNG')
report={'verifiedAt':datetime.now(timezone.utc).isoformat(),'counts':{di:sum(f['direction']==di for f in d['frames']) for di in ['E','W']},'uniqueSHA':len(set(f['sha256'] for f in d['frames'])),'errors':errors,'passed':not errors,'scope':'file integrity only; visual conclusions in cast-foot-review.json'}
(b/'audit/cast-foot-integrity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))

