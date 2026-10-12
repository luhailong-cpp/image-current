from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent;T=B.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sel=json.loads((T/'selected-native.json').read_text())
box=[1536,2695,2790,3949];out=Image.new('RGB',(1254,1254));sources=[]
for r in range(1,5):
 for c in range(1,5):
  ox,oy=(c-1)*1024,(r-1)*1024;x0,y0,x1,y1=max(ox,box[0]),max(oy,box[1]),min(ox+1024,box[2]),min(oy+1024,box[3])
  if x0>=x1 or y0>=y1:continue
  patch=f'p{r}{c}';p=T/'native'/sel.get(patch,patch+'.png');im=Image.open(p).convert('RGB');assert im.size==(1254,1254)
  crop=[x0-ox+115,y0-oy+115,x1-ox+115,y1-oy+115];dest=[x0-box[0],y0-box[1]]
  out.paste(im.crop(crop),tuple(dest));sources.append({'file':str(p),'sha256':sha(p),'crop':crop,'paste':dest})
(B/'context').mkdir(exist_ok=True);f=B/'context/p43-eave-centred.png';out.save(f)
Path(str(f)+'.generation.json').write_text(json.dumps({'file':str(f),'sha256':sha(f),'tile':'r06_c13','tileBox':box,'worldBox':[49152+box[0],20480+box[1],49152+box[2],20480+box[3]],'derivedFrom':sources,'operation':'integer native-core crops; no resampling; QA/edit context'},indent=2)+'\n')
print(str(f))
