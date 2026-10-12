from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
from apply_r03_c03_repairs import overlay_mask
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resolve(p):return Path(p) if Path(p).is_absolute() else ROOT/p
basep=ROOT/'work-r04_c04/tiles/r04_c04.assembly.json';base=read(basep)
a=np.array(Image.open(base['candidate']).convert('RGB'));ids=np.array(Image.open(base['sourceIdMap'])).astype(np.uint16)
sources=base['sources'];src=ROOT/'native/r04_c04_post_net_support_bridge_v01.png';rp=Path(str(src)+'.generation.json');r=read(rp)
assert sha(src)==r['sha256']
box=[v-(12288 if i%2==0 else 12288) for i,v in enumerate(r['globalNativeBox'])]
x0,y0,x1,y1=box;repair=np.array(Image.open(src).convert('RGB'));mask,paths=overlay_mask(a[y0:y1,x0:x1],repair)
a[y0:y1,x0:x1][mask]=repair[mask];ids[y0:y1,x0:x1][mask]=17
sources.append({'sourceId':17,'file':str(src),'sha256':sha(src),'generationRecord':str(rp),'generationRecordSha256':sha(rp),'nativeBox':box})
counts=[]
for s in sources:
 gr=read(resolve(s['generationRecord']));g=gr['globalNativeBox'];s['nativeBox']=[g[0]-12288,g[1]-12288,g[2]-12288,g[3]-12288]
 y,x=np.nonzero(ids==s['sourceId']);im=np.array(Image.open(resolve(s['file'])).convert('RGB'));sx=x-s['nativeBox'][0];sy=y-s['nativeBox'][1]
 assert (sx>=0).all() and (sx<1254).all() and (sy>=0).all() and (sy<1254).all()
 assert np.array_equal(a[y,x],im[sy,sx]);counts.append({'sourceId':s['sourceId'],'pixels':len(x)})
out=ROOT/'work-r04_c04/tiles';p=out/'r04_c04.candidate-repair-v2.png';ip=out/'r04_c04.source-id-repair-v2.png'
Image.fromarray(a).save(p);Image.fromarray(ids.astype(np.uint8)).save(ip)
rec={'tile':'r04_c04','status':'candidate-repair-pending-QA','candidate':str(p),'sha256':sha(p),'size':[4096,4096],'globalBox':[12288,12288,16384,16384],'sources':sources,'pixelSourceVerified':True,'pixelCount':4096*4096,'sourceIdMap':str(ip),'sourceIdSha256':sha(ip),'base':{'record':str(basep),'sha256':sha(basep)},'overlay':{'source':str(src),'nativeBox':box,'paths':paths,'selectedPixels':int(mask.sum())},'counts':counts,'resample':False,'blend':False,'formalAccepted':False}
(out/'r04_c04.repair-v2.assembly.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
qa=ROOT/'work-r04_c04/qa/support-bridge-v01';qa.mkdir(exist_ok=True)
crops=[]
# Exact 4 side bands with full extent, plus corners; all native dimensions.
for name,b in [('north',[x0,y0,x1,y0+230]),('south',[x0,y1-230,x1,y1]),('west',[x0,y0,x0+230,y1]),('east',[x1-230,y0,x1,y1])]:
 for k in range(2):
  bb=[b[0]+627*k,b[1],min(b[2],b[0]+627*(k+1)),b[3]] if name in ['north','south'] else [b[0],b[1]+627*k,b[2],min(b[3],b[1]+627*(k+1))]
  q=qa/f'{name}-{k+1}.png';Image.fromarray(a).crop(bb).save(q);crops.append({'file':str(q),'sha256':sha(q),'box':bb})
for name,b in [('nw',[x0,y0,x0+300,y0+300]),('ne',[x1-300,y0,x1,y0+300]),('sw',[x0,y1-300,x0+300,y1]),('se',[x1-300,y1-300,x1,y1])]:
 q=qa/f'{name}.png';Image.fromarray(a).crop(b).save(q);crops.append({'file':str(q),'sha256':sha(q),'box':b})
(qa/'crops.json').write_text(json.dumps(crops,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate':str(p),'sha256':sha(p),'assembly':str(out/'r04_c04.repair-v2.assembly.json'),'pixelsVerified':4096*4096,'changed':int(mask.sum())}))

