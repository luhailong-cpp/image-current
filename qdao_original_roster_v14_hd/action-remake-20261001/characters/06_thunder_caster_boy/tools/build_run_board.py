"""Exact-timing eight-direction preview, fixed full-canvas resize only."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
dirs=['N','NE','E','SE','S','SW','W','NW'];w=256;h=286
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=[]
for d in dirs:
 for n in range(16):
  p=R/f'runtime/run/{d}/{n:02d}.png'
  if not p.exists():raise SystemExit('Incomplete run set: '+str(p))
  sources.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p)})
boards=[]
for n in range(16):
 board=Image.new('RGB',(w*4,h*2),'#eeeee6');draw=ImageDraw.Draw(board)
 for col,d in enumerate(dirs):
  x=(col%4)*w;y=(col//4)*h
  im=Image.open(R/f'runtime/run/{d}/{n:02d}.png').convert('RGBA').resize((w,w),Image.Resampling.LANCZOS)
  board.paste(im,(x,y),im)
  draw.text((x+12,y+w+5),f'{d}  ·  {n:02d} / 15',font=font,fill='#2b443b')
 boards.append(board)
for cycle in [960,3840]:
 p=R/f'preview/run-eight-directions-{cycle}.webp'
 boards[0].save(p,save_all=True,append_images=boards[1:],duration=cycle//16,loop=0,lossless=True,method=4)
 rec={'file':p.relative_to(R).as_posix(),'sha256':sha(p),'operation':'same phase-index grid, each full runtime canvas uniformly resized256, labels only; no sprite editing','durationMs':[cycle//16]*16,'cycleMs':cycle,'derivedFrom':sources,'clientVerified':False}
 p.with_name(p.name+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 print(p.relative_to(R).as_posix())
