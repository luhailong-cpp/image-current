from pathlib import Path
from PIL import Image
import json,hashlib
O=Path(__file__).resolve().parent
for d in sorted(O.glob('g0*-*')):
 p=d/'manifest.json'
 if not p.exists():continue
 q=json.loads(p.read_text(encoding='utf-8'))
 if 'seams' not in q or len(q['seams'])!=16:continue
 for ori in 'hv':
  dest=d/f'{ori}-seams-board-100pct.png'
  if dest.exists():continue
  board=Image.new('RGB',(2048,2048))
  seq=[e for e in q['seams'] if Path(e['file']).name.startswith(ori+'-')]
  for i,e in enumerate(seq):
   pos=((i%2)*1024,(i//2)*512) if ori=='h' else ((i%4)*512,(i//4)*1024)
   with Image.open(e['file']) as im:board.paste(im,pos)
  board.save(dest);board.close()
 print(d.name)
