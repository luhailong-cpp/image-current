from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from assemble_r03_c03 import append_hard
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resolve(p):return Path(p) if Path(p).is_absolute() else ROOT/p
sel=read(ROOT/'work-r04_c04/selected.json')['sources']
assert len(sel)==16
strips=[];stripids=[];seams=[]
for row in range(4):
 arrs=[np.array(Image.open(resolve(s['file'])).convert('RGB')) for s in sel[row*4:row*4+4]]
 a=arrs[0];ids=np.full(a.shape[:2],row*4+1,np.uint8)
 for col in range(1,4):
  a,ids,z=append_hard(a,ids,arrs[col],np.full(arrs[col].shape[:2],row*4+col+1,np.uint8),f'row{row+1}-col{col}')
  seams.append(z)
 strips.append(a);stripids.append(ids)
a,ids=strips[0],stripids[0]
for row in range(1,4):
 a,ids,z=append_hard(a.transpose(1,0,2),ids.T,strips[row].transpose(1,0,2),stripids[row].T,f'row{row}-to-{row+1}')
 a=a.transpose(1,0,2);ids=ids.T;seams.append(z)
a=a[115:4211,115:4211];ids=ids[115:4211,115:4211]
counts=[]
for s in sel:
 ys,xs=np.nonzero(ids==s['sourceId']);src=np.array(Image.open(resolve(s['file'])).convert('RGB'))
 sx=xs+115-(s['column']-1)*1024;sy=ys+115-(s['row']-1)*1024
 assert np.array_equal(a[ys,xs],src[sy,sx])
 counts.append({'sourceId':s['sourceId'],'pixels':len(xs)})
out=ROOT/'work-r04_c04/tiles';out.mkdir(exist_ok=True)
p=out/'r04_c04.candidate.png';Image.fromarray(a).save(p)
ip=out/'r04_c04.source-id.png';Image.fromarray(ids).save(ip)
rec={'tile':'r04_c04','status':'construction-candidate-known-defects','candidate':str(p),'sha256':sha(p),'size':[4096,4096],'globalBox':[12288,12288,16384,16384],'sources':sel,'pixelSourceVerified':True,'pixelCount':sum(v['pixels'] for v in counts),'sourceIdMap':str(ip),'sourceIdSha256':sha(ip),'seams':seams,'counts':counts,'resample':False,'blend':False,'formalAccepted':False}
(out/'r04_c04.assembly.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
qa=ROOT/'work-r04_c04/qa/full-v1';qa.mkdir(exist_ok=True)
crops=[]
for axis in ['h','v']:
 for k in range(1,4):
  for segment in range(4):
   box=[segment*1024,k*1024-230,(segment+1)*1024,k*1024+230] if axis=='h' else [k*1024-230,segment*1024,k*1024+230,(segment+1)*1024]
   cp=qa/f'{axis}{k}-s{segment+1}.png';Image.fromarray(a).crop(box).save(cp)
   crops.append({'file':str(cp),'sha256':sha(cp),'box':box})
for y in range(1,4):
 for x in range(1,4):
  box=[x*1024-230,y*1024-230,x*1024+230,y*1024+230]
  cp=qa/f'junction-r{y}-c{x}.png';Image.fromarray(a).crop(box).save(cp)
  crops.append({'file':str(cp),'sha256':sha(cp),'box':box})
(qa/'crops.json').write_text(json.dumps(crops,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate':str(p),'sha256':sha(p),'pixelSourceVerified':True,'pixels':4096*4096,'crops':len(crops)}))

