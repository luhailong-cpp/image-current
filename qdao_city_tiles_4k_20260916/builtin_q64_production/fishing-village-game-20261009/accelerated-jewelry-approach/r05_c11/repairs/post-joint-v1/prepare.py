from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[3]
D=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=Image.new('RGB',(1254,1254))
box=[1400,-115,2654,1139]
sources=[]
for r in [1,2]:
 for c in [2,3]:
  rec=json.loads((B/'r05_c11/records'/f'p{r}{c}.selection.json').read_text())
  p=Path(rec['file'])
  sb=[(c-1)*1024,(r-1)*1024,c*1024,r*1024]
  it=[max(box[0],sb[0]),max(box[1],sb[1]),min(box[2],sb[2]),min(box[3],sb[3])]
  if it[2]<=it[0] or it[3]<=it[1]:continue
  crop=[it[0]-sb[0]+115,it[1]-sb[1]+115,it[2]-sb[0]+115,it[3]-sb[1]+115]
  at=[it[0]-box[0],it[1]-box[1]]
  out.paste(Image.open(p).crop(crop),at)
  sources.append({'file':str(p),'sha256':sha(p),'sourceCrop':crop,'pasteAt':at})
p=B/'r04_c11/candidate/r04_c11-4096-candidate-v3.png'
crop=[1400,3981,2654,4096]
out.paste(Image.open(p).crop(crop),(0,0))
sources.append({'file':str(p),'sha256':sha(p),'sourceCrop':crop,'pasteAt':[0,0],'role':'north existing approved candidate, exact115px'})
out.save(D/'target-native.png')
(D/'target.derivation.json').write_text(json.dumps({'tileBox':box,'dimensions':list(out.size),'resampling':False,'sources':sources,'targetSha256':sha(D/'target-native.png')},indent=2))
print(json.dumps({'file':str(D/'target-native.png'),'sha256':sha(D/'target-native.png')}))
