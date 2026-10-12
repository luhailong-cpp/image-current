from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
IDLE=Path('D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/06-final/runtime/idle')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
canvas=Image.new('RGB',(8*220,3*250),'#e0e5e2');draw=ImageDraw.Draw(canvas);refs=[]
for col,d in enumerate(['N','NE','E','SE','S','SW','W','NW']):
 for row,name in enumerate(['idle','00','08']):
  p=IDLE/(d+'.png') if row==0 else R/'runtime'/'run'/d/(name+'.png')
  if not p.exists():continue
  im=Image.open(p).convert('RGBA').resize((220,220),Image.Resampling.LANCZOS)
  canvas.paste(im,(col*220,row*250),im);draw.text((col*220+8,row*250+226),d+' '+name,font=font,fill='#234439')
  refs.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
canvas.save(R/'review/cross_direction_idle_00_08.png')
(R/'review/cross_direction_idle_00_08.json').write_text(json.dumps({'operation':'same fullcanvas220 presentation only, no runtime change','sources':refs},ensure_ascii=False,indent=2),encoding='utf-8')
