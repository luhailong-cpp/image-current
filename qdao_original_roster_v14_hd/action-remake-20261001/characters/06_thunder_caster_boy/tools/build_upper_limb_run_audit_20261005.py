from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1];out=R/'review/upper-limb-run-details-20261005';out.mkdir(exist_ok=True)
sources=[]
for direction in ['S','SE','SW','W']:
 full=Image.new('RGB',(1280,1376),(225,229,227));fd=ImageDraw.Draw(full)
 for batch in range(4):
  board=Image.new('RGB',(1840,1088),(225,229,227));draw=ImageDraw.Draw(board);refs=[]
  lower=Image.new('RGB',(1840,936),(225,229,227));ld=ImageDraw.Draw(lower)
  for idx in range(4):
   n=batch*4+idx;p=R/'runtime/run'/direction/f'{n:02}.png';im=Image.open(p).convert('RGBA');h=hashlib.sha256(p.read_bytes()).hexdigest()
   crop=im.crop((60,280,980,800));x=idx%2*920;y=idx//2*544;board.paste(crop,(x,y),crop);draw.text((x+8,y+525),f'run {direction} {n:02} upper limbs / actual crop 1:1',fill='black')
   legcrop=im.crop((60,580,980,1024));ly=idx//2*468;lower.paste(legcrop,(x,ly),legcrop);ld.text((x+8,ly+449),f'run {direction} {n:02} hips-knees-ankles-toes / 1:1',fill='black')
   thumb=im.resize((320,320));fx=n%4*320;fy=n//4*344;full.paste(thumb,(fx,fy),thumb);fd.text((fx+8,fy+325),f'{direction} {n:02}',fill='black')
   source={'file':str(p),'sha256':h,'frame':n,'direction':direction,'crop':[60,280,980,800]};sources.append(source);refs.append(source)
  q=out/f'{direction}-{batch}.jpg';board.save(q,quality=97);q.with_name(q.name+'.generation.json').write_text(json.dumps({'operation':'audit only 1:1 crop montage; runtime not edited','sources':refs},ensure_ascii=False,indent=2),encoding='utf-8')
  lower.save(out/f'{direction}-legs-{batch}.jpg',quality=97)
 full.save(out/f'{direction}-sequence.jpg',quality=95)
(out/'inputs.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'directions':4,'frames':len(sources),'directory':str(out)}))
