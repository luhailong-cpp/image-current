from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
b=Path(__file__).resolve().parents[1]
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
for di in ['NE','W']:
 d=json.loads((b/'audit'/f'run-{di}-selection.json').read_text(encoding='utf8'))
 sheet=Image.new('RGB',(1440,920),(223,230,236))
 for i,r in enumerate(d['frames']):
  im=Image.open(b/r['source']).convert('RGBA')
  # Diagnostic crop only: keep entire lower-left to lower-right legs, no artwork mutation.
  crop=im.crop((130,805,1130,1254)).resize((350,157),Image.Resampling.LANCZOS)
  tile=Image.new('RGB',(360,230),(223,230,236));tile.paste(crop,(5,38),crop);dr=ImageDraw.Draw(tile);dr.text((8,8),f"{di}{i+1:02d} "+Path(r['source']).stem.replace('run-'+di+'-',''),font=font,fill=(20,43,55));sheet.paste(tile,((i%4)*360,(i//4)*230))
 sheet.save(b/'audit'/f'run-{di}-foot-direction-atlas.png')
print('created NE/W diagnostic crops')

