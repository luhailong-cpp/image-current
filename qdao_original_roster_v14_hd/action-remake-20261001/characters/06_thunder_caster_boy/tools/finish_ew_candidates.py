from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/06_thunder_caster_boy')
for d in ['E','W']:
 canvas=Image.new('RGB',(1280,1400),'#d9e2df');dr=ImageDraw.Draw(canvas);sources=[]
 for i in range(16):
  candidate=R/'work'/f'run_{d}_{i:02}_progress_v1.png';p=candidate if candidate.exists() else R/f'runtime/run/{d}/{i:02}.png'
  sources.append({'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generationRecord':p.relative_to(R).as_posix()+'.generation.json'})
  im=Image.open(p).convert('RGBA')
  if candidate.exists():
   layer=Image.new('RGBA',(1024,1024));layer.alpha_composite(im.resize((901,901),Image.Resampling.LANCZOS),(61,97));im=layer
  im=im.resize((320,320),Image.Resampling.LANCZOS);x=i%4*320;y=i//4*350;canvas.paste(im,(x,y),im);dr.text((x+10,y+325),f'{d}{i:02} {"candidate" if candidate.exists() else "current"}',fill='black')
 out=R/'review'/f'run_{d}_finish_candidates.png';canvas.save(out)
 out.with_name(out.name+'.generation.json').write_text(json.dumps({'file':out.relative_to(R).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'derivedFrom':sources,'operation':'Diagnostic candidate contact table;1254 native candidates uniformly901 then fixed(61,97),full canvas320 thumbnails;not selected runtime nor current acceptance','actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
