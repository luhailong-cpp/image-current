from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
j=json.loads((T/'candidate/latest-assembly.json').read_text())
p=Path(j['candidate']['path']);s=hashlib.sha256(p.read_bytes()).hexdigest()
assert s==j['candidate']['sha256']
D=T/'review'/('south-local-'+s[:16]);D.mkdir(exist_ok=True)
im=Image.open(p).convert('RGB')
items=[]
for n in range(4):
 box=[n*1024,3712,(n+1)*1024,4096];f=D/f'south-q{n}-100pct.png'
 with f.open('xb') as out:im.crop(box).save(out,format='PNG')
 items.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'coreBox':box,'resized':False})
with (D/'evidence.json').open('x') as f:json.dump({'candidate':j['candidate'],'crops':items},f,indent=2)
print(json.dumps({'candidate':j['candidate'],'context':j['context'],'directory':str(D),'items':items}))
