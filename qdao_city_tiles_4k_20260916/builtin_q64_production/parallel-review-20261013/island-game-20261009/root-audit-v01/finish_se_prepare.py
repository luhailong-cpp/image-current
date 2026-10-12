from pathlib import Path
from PIL import Image
import json
O=Path(__file__).resolve().parent/'se-finishing-v01';O.mkdir(exist_ok=True)
S=O.parent.parent/'southeast-audit-v01'
for group in ['g01-r09-r10-c12-c13','g02-r11-r12-c11-c12']:
 d=S/group;q=json.loads((d/'manifest.json').read_text(encoding='utf-8'))
 for axis in ['vertical','horizontal']:
  cuts=[e for e in q['crops'] if e['id'].startswith(axis+'-')]
  assert len(cuts)==8
  im=Image.new('RGB',(2048,2048))
  for k,e in enumerate(cuts):
   with Image.open(e['file']) as cr:
    pos=((k%4)*512,(k//4)*1024) if axis=='vertical' else ((k%2)*1024,(k//2)*512)
    im.paste(cr,pos)
  im.save(O/f'{group}-{axis}-board-100pct.png');im.close()
 print(group)
