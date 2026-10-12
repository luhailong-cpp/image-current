import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from PIL import Image,ImageDraw
b=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy')
keys=['run-NW-01-v3', 'run-NW-02-v4', 'run-NW-03-v1', 'run-NW-04-v1', 'run-NW-05-v5', 'run-NW-06-v2', 'run-NW-07-v3', 'run-NW-08-v2', 'run-NW-09-v5', 'run-NW-10-v1', 'run-NW-11-v1', 'run-NW-12-v1', 'run-NW-13-v2', 'run-NW-14-v1', 'run-NW-15-v2', 'run-NW-16-v1']
for mode in ['full','legs']:
 w,h=(320,345) if mode=='full' else (400,300)
 sheet=Image.new('RGB',(w*4,h*4),(215,219,220));draw=ImageDraw.Draw(sheet)
 for i,k in enumerate(keys):
  im=Image.open(b/'staging'/(k+'.png')).convert('RGBA')
  if mode=='legs': im=im.crop((280,710,1130,1254))
  im.thumbnail((w,h-25))
  x=(i%4)*w+(w-im.width)//2;y=(i//4)*h+25
  sheet.paste(im,(x,y),im);draw.text(((i%4)*w+8,(i//4)*h+5),k,fill='black')
 out=b/'review'/('reference09-NW-current-'+mode+'.png');sheet.save(out);print(out)

