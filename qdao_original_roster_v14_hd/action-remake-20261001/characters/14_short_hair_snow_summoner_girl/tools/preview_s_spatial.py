"""Register S candidates with preserved whole-canvas roots for visual comparison."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
from export_frame import run
from apply_registration import apply
R=Path(__file__).resolve().parents[1]
sel={4:('south-bamboo-contact-S-04-v1',[529,960]),5:('run-S-05-root-spatial-v1',[529,960]),6:('run-S-06-root-spatial-v1',[534,960]),7:('run-S-07-root-spatial-v1',[556,960]),8:('south-bamboo-contact-S-08-v2',[556,960]),12:('south-bamboo-contact-S-12-v1',[526,960]),13:('run-S-13-root-spatial-v1',[526,960]),14:('run-S-14-root-spatial-v1',[528,960]),15:('run-S-15-root-spatial-v1',[533,960]),16:('run-S-16-root-spatial-v1',[526,960])}
override=R/'audit/root-S-spatial-selection.json'
if override.exists():sel={int(n):v for n,v in json.loads(override.read_text(encoding='utf-8-sig')).items()}
rows=[];paths={}
for n in range(1,17):
 if n not in sel:paths[n]=R/'run/S'/f'{n:02d}.png';continue
 slot,root=sel[n];src=R/'run/staging'/f'{slot}.png';dest=R/'run/staging'/f'{slot}-registered.png'
 run(src,dest);paths[n]=dest
 rows.append({'file':dest.relative_to(R).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'srcRoot':root,'basis':'Existing anatomical registration inherited from target; no foot alignment, per-frame fitting or pose synthesis.'})
reg=R/'run/staging/root-S-spatial-candidate-registration.json'
reg.write_text(json.dumps({'globalScale':.8,'targetRoot':[512,942],'frames':rows},indent=2),encoding='utf-8');apply(reg)
for kind,box,scale in [('full',(0,0,1024,1024),.28),('legs',(240,650,800,1000),.65)]:
 w,h=round((box[2]-box[0])*scale),round((box[3]-box[1])*scale)
 sheet=Image.new('RGB',(4*w,4*(h+26)),(225,229,237));draw=ImageDraw.Draw(sheet)
 for n,p in paths.items():
  im=Image.open(p).convert('RGBA').crop(box).resize((w,h),Image.Resampling.LANCZOS)
  x=(n-1)%4*w;y=(n-1)//4*(h+26)
  draw.text((x+8,y+6),f'{n:02d} P{((n-1)%8)//2+1} '+('LEFT' if n<=8 else 'RIGHT')+(' candidate' if n in sel else ' retained'),fill=(20,20,20))
  sheet.paste(im,(x,y+26),im)
 sheet.save(R/'run/staging'/f'root-S-spatial-{kind}.jpg',quality=94)
(R/'audit/root-S-spatial-candidate-files.json').write_text(json.dumps({str(n):{'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'candidate':n in sel} for n,p in paths.items()},indent=2),encoding='utf-8')
(R/'audit/root-S-spatial-selection.json').write_text(json.dumps(sel,indent=2),encoding='utf-8')

