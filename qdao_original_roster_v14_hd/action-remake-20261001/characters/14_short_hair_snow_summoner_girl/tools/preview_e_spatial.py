"""Export current E candidates with existing anatomical registration for visual comparison."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
from export_frame import run
from apply_registration import apply
R=Path(__file__).resolve().parents[1]
inputs=json.loads((R/'audit/root-E-spatial-inputs.json').read_text(encoding='utf-8-sig'))
selection={4:2,5:2,6:2,7:1,8:1,10:1,12:1,13:1,14:1,15:1,16:1}
override=R/'audit/root-E-spatial-selection.json'
if override.exists(): selection={int(n):v for n,v in json.loads(override.read_text(encoding='utf-8-sig')).items()}
rows=[]; paths={}
for n in range(1,17):
 if n not in selection:
  paths[n]=R/'run/E'/f'{n:02d}.png';continue
 slot=f'run-E-{n:02d}-spatial-v{selection[n]}'
 src=R/'run/staging'/f'{slot}.png';dest=R/'run/staging'/f'{slot}-registered.png'
 run(src,dest);paths[n]=dest
 rows.append({'file':dest.relative_to(R).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'srcRoot':inputs[str(n)]['sourceRoot'],'basis':'Existing anatomical registration inherited from target; no foot alignment, per-frame fitting or pose synthesis.'})
reg=R/'run/staging/root-E-spatial-candidate-registration.json'
reg.write_text(json.dumps({'globalScale':.8,'targetRoot':[512,942],'frames':rows},indent=2),encoding='utf-8');apply(reg)
for kind,box,scale in [('full',(0,0,1024,1024),.28),('legs',(250,670,910,995),.65)]:
 w,h=round((box[2]-box[0])*scale),round((box[3]-box[1])*scale)
 sheet=Image.new('RGB',(4*w,4*(h+26)),(225,229,237));draw=ImageDraw.Draw(sheet)
 for n,p in paths.items():
  im=Image.open(p).convert('RGBA').crop(box).resize((w,h),Image.Resampling.LANCZOS)
  x=(n-1)%4*w;y=(n-1)//4*(h+26)
  draw.text((x+8,y+6),f'{n:02d} P{((n-1)%8)//2+1} '+('LEFT' if n<=8 else 'RIGHT')+(' candidate' if n in selection else ' retained'),fill=(20,20,20))
  sheet.paste(im,(x,y+26),im)
 sheet.save(R/'run/staging'/f'root-E-spatial-{kind}.jpg',quality=94)
manifest={str(n):{'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'candidate':n in selection} for n,p in paths.items()}
(R/'audit/root-E-spatial-candidate-files.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
