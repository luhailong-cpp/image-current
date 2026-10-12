import json,hashlib
from pathlib import Path
z=Path(__file__).resolve().parent
rows=[['a01','a01','a01','a01'],['a01','a01','a02','a01'],['a01','a01','a01','a03'],['a01','a01','a01','a01']]
m={'schemaVersion':1,'tileId':'r05_c04','nativePixels':1254,'corePixels':1024,'haloPixels':115,'patchMatrix':[]}
for r,row in enumerate(rows,1):
 entries=[]
 for c,a in enumerate(row,1):
  p=f'native/r05_c04_s{r:02}_{c:02}_{a}.png'
  entries.append({'path':p,'generationRecord':p+'.generation.json','sha256':hashlib.sha256((z/p).read_bytes()).hexdigest()})
 m['patchMatrix'].append(entries)
out=z/'r05_c04.candidate-v1.manifest.json'
assert not out.exists()
out.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
print(out)
