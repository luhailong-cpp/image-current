from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
sources=[]
for action,n in [('run',16),('hit',6),('attack',12),('cast',16)]:
 direction='N' if action=='run' else 'E'
 tile=350; height=374
 paths=[ROOT/'runtime'/action/direction/f'{i:02d}.png' for i in range(1,n+1)]
 sheet=Image.new('RGB',(4*tile,((n+3)//4)*(height+26)),(235,237,228))
 draw=ImageDraw.Draw(sheet)
 for idx,p in enumerate(paths):
  im=Image.open(p).convert('RGBA').crop((350,650,700,1024))
  x=(idx%4)*tile;y=(idx//4)*(height+26)
  sheet.paste(im,(x,y),im)
  draw.text((x+8,y+height),f'{action}/{direction}/{idx+1:02d}',font=font,fill=(25,65,45))
  sources.append({'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 sheet.save(ROOT/'audit'/f'feet-{action}-{direction}-current.jpg',quality=94)
(ROOT/'audit/feet-root-crops.sources.json').write_text(json.dumps({'operation':'inspection-only crops; runtime images unchanged','sources':sources},indent=2),encoding='utf-8')
