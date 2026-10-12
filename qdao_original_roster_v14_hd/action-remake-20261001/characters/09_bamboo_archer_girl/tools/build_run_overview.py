from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
dirs=['N','NE','E','SE','S','SW','W','NW']
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
frames=[];sources=[]
for number in range(1,17):
 sheet=Image.new('RGB',(1024,572),(235,237,228));draw=ImageDraw.Draw(sheet)
 for idx,direction in enumerate(dirs):
  p=ROOT/'runtime/run'/direction/f'{number:02d}.png'
  im=Image.open(p).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS)
  x=(idx%4)*256;y=(idx//4)*286
  sheet.paste(im,(x,y),im)
  draw.text((x+10,y+258),f'{direction}   {number:02d}/16   1200ms',font=font,fill=(25,65,45))
  sources.append({'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 frames.append(sheet)
out=ROOT/'preview/qa/run-eight-directions-1200.apng'
frames[0].save(out,save_all=True,append_images=frames[1:],duration=75,loop=0,format='PNG',disposal=0,blend=0)
with Image.open(out) as gif:
 times=[]
 for i in range(gif.n_frames):
  gif.seek(i);times.append(gif.info['duration'])
 assert len(times)==16 and sum(times)==1200
(ROOT/'preview/qa/run-eight-directions.sources.json').write_text(json.dumps({'atUtc':datetime.now(timezone.utc).isoformat(),'sources':sources,'operation':'whole 1024 canvas scaled to 256 for display only; no frame motion or root edits','durationsMs':times,'visualDynamicAcceptance':False},indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'frames':16,'cycleMs':sum(times)}))
