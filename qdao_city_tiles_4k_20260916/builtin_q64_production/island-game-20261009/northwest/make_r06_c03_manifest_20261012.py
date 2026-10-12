from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parent
sel=[['a01','a01','a02','a01'],['a01','a01','a01','a02'],['a01']*4,['a01','a01','a01','a03']]
matrix=[]
for r,row in enumerate(sel,1):
 cells=[]
 for c,a in enumerate(row,1):
  p=Z/'native'/f'r06_c03_s{r:02d}_{c:02d}_{a}.png'
  cells.append({'path':p.relative_to(Z).as_posix(),'generationRecord':p.relative_to(Z).as_posix()+'.generation.json','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 matrix.append(cells)
p=Z/'r06_c03.candidate-v1.manifest.json'
assert not p.exists()
p.write_text(json.dumps({'schemaVersion':1,'tileId':'r06_c03','nativePixels':1254,'corePixels':1024,'haloPixels':115,'patchMatrix':matrix},indent=2)+'\n',encoding='utf-8')
print(p)
