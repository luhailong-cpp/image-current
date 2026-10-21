from pathlib import Path
from PIL import Image
import json,hashlib,sys
R=Path(__file__).resolve().parent
tile=sys.argv[1]; out=R/'tiles'/f'{tile}_candidate-v1_4096.png'
selected=json.loads((R/'selected-revisions.json').read_text()) if (R/'selected-revisions.json').exists() else {}
im=Image.new('RGB',(4096,4096));records=[]
for r in range(1,5):
 for c in range(1,5):
  stem=f'{tile}_s{r:02d}_{c:02d}';p=R/'native'/f'{stem}_{selected.get(stem,"a01")}.png'; a=Image.open(p);assert a.size==(1254,1254)
  im.paste(a.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
  records.append({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'crop':[115,115,1139,1139],'destination':[(c-1)*1024,(r-1)*1024]})
if out.exists(): raise RuntimeError('No overwrite')
im.save(out);q=R/'qa'/tile;q.mkdir(exist_ok=True)
im.resize((1024,1024)).save(q/'preview-only.png')
for axis in ['vertical','horizontal']:
 for n in range(1,4):
  for k in range(4):
   box=(n*1024-128,k*1024,n*1024+128,(k+1)*1024) if axis=='vertical' else (k*1024,n*1024-128,(k+1)*1024,n*1024+128)
   im.crop(box).save(q/f'{axis}-{n}-{k+1}.png')
(out.with_suffix('.json')).write_text(json.dumps({'tile':tile,'dimensions':[4096,4096],'method':'16 unscaled native1024 cores, direct joins, no blur','sources':records,'formalAccepted':False,'internalSeams':'pending','sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
print(out)
