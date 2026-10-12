from pathlib import Path
import json,hashlib
from PIL import Image
OUT=Path(__file__).resolve().parent
for q in sorted(OUT.glob('g0*')):
 m=json.loads((q/'manifest.json').read_text(encoding='utf-8'))
 for e in m['crops']:
  if e['id'].startswith('contact-'):e['excludedReason']='Contact panel v01 cell indexing error; original individual crops and native assembly unaffected. Use explicitly listed v02 panels.'
 for axis in ['vertical','horizontal']:
  cuts=[e for e in m['crops'] if e['id'].startswith(axis+'-')]
  for j in range(2):
   block=cuts[j*4:(j+1)*4]
   panel=Image.new('RGB',(1024,2048) if axis=='vertical' else (2048,1024))
   for k,e in enumerate(block):
    with Image.open(e['file']) as im:panel.paste(im,((k%2)*im.width,(k//2)*im.height))
   p=q/f'contact-{axis}-{j+1}-100pct-NO-resample-v02.png';panel.save(p)
   m['crops'].append({'id':f'contact-{axis}-{j+1}-v02','file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'resampled':False,'displayOrder':[e['id'] for e in block],'visualStatus':'pending_current_review'})
 (q/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
