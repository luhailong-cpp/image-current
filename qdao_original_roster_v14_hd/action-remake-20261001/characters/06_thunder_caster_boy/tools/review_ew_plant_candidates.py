from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for d in ['E','W']:
 out=Image.new('RGB',(1400,590),(224,229,230));draw=ImageDraw.Draw(out);sources=[]
 for j,tag in enumerate(['06','07','plant','08','09']):
  p=R/'work'/f'run_{d}_07_plant_v1.png' if tag=='plant' else R/'runtime/run'/d/f'{tag}.png'
  im=Image.open(p).convert('RGBA')
  if tag=='plant':
   canvas=Image.new('RGBA',(1024,1024));canvas.alpha_composite(im.resize((901,901),Image.Resampling.LANCZOS),(61,97));im=canvas
  preview=im.resize((280,280),Image.Resampling.LANCZOS);out.paste(preview,(j*280,0),preview)
  draw.text((j*280+8,280),f'{d} {tag}',fill=(0,0,0),font=font)
  feet=im.crop((0,680,1024,1024)).resize((560,188),Image.Resampling.LANCZOS)
  # Diagnostic feet crop is displayed at half width; no runtime writes.
  feet=feet.resize((280,188),Image.Resampling.LANCZOS);out.paste(feet,(j*280,330),feet)
  sources.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p)})
 p=R/'review'/f'run_{d}_07_plant_comparison.png';out.save(p)
 p.with_suffix('.png.generation.json').write_text(json.dumps({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'derivedFrom':sources,'operation':'Fixed full canvas preview plus explicitly diagnostic lower-canvas crop; no game-frame mutation','actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2),encoding='utf-8')
 print(p)
