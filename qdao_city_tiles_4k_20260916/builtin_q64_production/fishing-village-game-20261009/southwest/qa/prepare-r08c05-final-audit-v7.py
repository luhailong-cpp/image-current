import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
def ref(p):p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def arr(p):return np.asarray(Image.open(p).convert('RGB'))
def save(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
t=rd(Q/'block2x2-r08r09c05c06-v7-trace.json');full=arr(t['context']['path']);checks=[]
for a in rd(Q/'r08c05-internal-audit-v1.json')['repairsPlanned']:
 rid=a['id'];box=a['contextBox'];checks.append((rid,box,Q/('repair-r08_c05-internal-v2-'+rid+'-after-100pct.png')))
for version in (2,3,7):
 v=rd(Q/('block2x2-r08r09c05c06-v'+str(version)+'-trace.json'))
 for a in v['repairs']:
  rid=a['id'];box=a['contextBox'];checks.append((rid,box,Path(a['after']['path'])))
out=[];fresh=[]
for rid,box,prior in checks:
 l,top,r,b=box;crop=full[top:b,l:r];same=np.array_equal(crop,arr(prior));p=prior
 if not same:
  p=Q/('block2x2-r08r09c05c06-v7-audit-'+rid+'-100pct.png')
  if not p.exists():Image.fromarray(crop).save(p)
  fresh.append(p.as_posix())
 out.append({'id':rid,'contextBox':box,'finalCrop':ref(p),'sourceContext':t['context'],'identicalToAlreadyViewedNativeCrop':bool(same),'previousNativeView':ref(prior)})
save(Q/'block2x2-r08r09c05c06-v7-final-repair-checks.json',out)
print(json.dumps({'fresh':fresh,'total':len(out),'reuse':sum(a['identicalToAlreadyViewedNativeCrop'] for a in out)}))
