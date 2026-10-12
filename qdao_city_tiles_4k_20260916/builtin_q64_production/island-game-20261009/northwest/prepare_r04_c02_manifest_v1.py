import json,hashlib
from pathlib import Path
z=Path(__file__).resolve().parent
a=[['a02','a01','a01','a02'],['a01','a01','a01','a02'],['a01','a01','a01','a02'],['a01','a01','a01','a02']]
m=dict(schemaVersion=1,tileId='r04_c02',nativePixels=1254,corePixels=1024,haloPixels=115,patchMatrix=[])
for r,row in enumerate(a,1):
 out=[]
 for c,v in enumerate(row,1):
  p=f'native/r04_c02_s{r:02d}_{c:02d}_{v}.png'
  out.append(dict(path=p,generationRecord=p+'.generation.json',sha256=hashlib.sha256((z/p).read_bytes()).hexdigest()))
 m['patchMatrix'].append(out)
with (z/'r04_c02.candidate-v1.manifest.json').open('x',encoding='utf-8') as f:json.dump(m,f,indent=2)

