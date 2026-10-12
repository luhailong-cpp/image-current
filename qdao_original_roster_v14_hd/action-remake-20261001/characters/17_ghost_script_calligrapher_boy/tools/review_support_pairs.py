from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
b=Path(__file__).resolve().parents[1]
for direction in ['N','NW']:
 report=json.loads((b/f'review-run-{direction}.json').read_text(encoding='utf-8-sig'))
 keys=[Path(f['file']).stem for f in report['selectedForSequenceReview']]
 for mode in ['240','feet']:
  w,h=(240,265) if mode=='240' else (330,290)
  sheet=Image.new('RGB',(4*w,4*h),(218,221,222));d=ImageDraw.Draw(sheet)
  for ii,k in enumerate(keys):
   p=b/'staging'/(k+'.png')
   d.text(((ii%4)*w+5,(ii//4)*h+5),k,fill='black')
   if not p.exists():continue
   im=Image.open(p).convert('RGBA')
   if mode=='feet':im=im.crop((300,740,1000,1254))
   im.thumbnail((w,h-25));x=(ii%4)*w+(w-im.width)//2;y=(ii//4)*h+25
   sheet.paste(im,(x,y),im)
  sheet.save(b/'review'/f'support-pairs-{direction}-current-{mode}.png')
print('rendered N/NW explicit current pick diagnostic sheets')
