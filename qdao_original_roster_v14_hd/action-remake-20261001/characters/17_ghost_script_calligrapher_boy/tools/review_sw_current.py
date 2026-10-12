from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy');O=B/'review/reference09-SW';versions=[1,1,1,1,2,4,2,2,4,1,2,2,2,2,1,2];files=[B/'staging'/f'run-SW-{i+1:02d}-v{v}.png' for i,v in enumerate(versions)]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for size in [240,480]:
 sheet=Image.new('RGB',(size*4,(size+28)*4),(41,47,50));d=ImageDraw.Draw(sheet)
 for i,p in enumerate(files):
  x=(i%4)*size;y=(i//4)*(size+28);im=Image.open(p).convert('RGBA').resize((size,size),Image.Resampling.LANCZOS);d.text((x+5,y+4),p.stem+' pending',font=font,fill='white');sheet.paste(im,(x,y+28),im)
 sheet.save(O/f'selected-{size}.png')
print(json.dumps({'selected':[p.name for p in files],'pngCount':len(list((B/'staging').glob('run-SW-*.png')))}))

