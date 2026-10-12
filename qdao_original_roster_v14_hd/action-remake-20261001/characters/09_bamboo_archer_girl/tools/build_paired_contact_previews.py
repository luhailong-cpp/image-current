from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for direction in ['N','NE','E','SE','S','SW','W','NW']:
 d=json.loads((ROOT/f'audit/run-{direction}-paired-ground-review.json').read_text(encoding='utf-8-sig'))
 orders=d.get('supportOrder') or {s['foot']:[x['frames'] for x in s['positions']] for s in d.get('segments',[])}
 if not orders:orders={name:s['pairs'] for name,s in zip(['A','B'],d.get('intendedSegments',[]))}
 if direction=='E':orders={name:pairs for name,pairs in zip(['A','B'],orders.values())}
 sheet=Image.new('RGB',(2048,564),(242,240,230));draw=ImageDraw.Draw(sheet);sources=[]
 for row,(foot,pairs) in enumerate(orders.items()):
  for col,number in enumerate(sum(pairs,[])):
   p=ROOT/f'runtime/run/{direction}/{number:02d}.png'
   im=Image.open(p).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS)
   sheet.paste(im,(col*256,row*282),im)
   draw.text((col*256+8,row*282+256),f'{direction} {foot} P{col//2+1} {number:02d}',font=font,fill=(24,70,50))
   sources.append({'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 out=ROOT/f'preview/qa/run-{direction}-paired-contact.png';sheet.save(out)
 out.with_suffix('.sources.json').write_text(json.dumps({'operation':'whole canvas thumbnails ordered by support pairs; no runtime image changes','sources':sources,'dynamicApproval':False},indent=2),encoding='utf-8')
print('Built eight current paired contact sheets with source hashes.')

