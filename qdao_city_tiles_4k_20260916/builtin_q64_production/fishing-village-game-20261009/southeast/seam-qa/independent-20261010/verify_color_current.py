import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
TILE=HERE.parent.parent/sys.argv[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
selection=TILE/(sys.argv[2] if len(sys.argv)>2 else 'selected-patches.json')
for pid,rel in json.loads(selection.read_text(encoding='utf-8-sig'))['patches'].items():
 target=TILE/rel;rec=json.loads(Path(str(target)+'.derivation.json').read_text())
 source=Path(rec['derivedFrom'][0]['file']);base=Path(rec['derivedFrom'][1]['file'])
 ev=rec['correctionEvidence'];z=np.load(ev['file']);grid=z['additiveGridRgb'];n=grid.shape[0]
 q=np.clip((np.arange(1254,dtype=np.float32)-115+.5)/16,0,n-1)
 lo=np.floor(q).astype(int);hi=np.minimum(lo+1,n-1);w=q-lo
 a=grid[lo[:,None],lo[None,:]]*(1-w[None,:,None])+grid[lo[:,None],hi[None,:]]*w[None,:,None]
 b=grid[hi[:,None],lo[None,:]]*(1-w[None,:,None])+grid[hi[:,None],hi[None,:]]*w[None,:,None]
 field=(a*(1-w[:,None,None])+b*w[:,None,None]).astype(np.float32)
 field*=1-z['safetyProtectionY'][:,None,None]*(1-z['safetyWeightX'][None,:,None])
 s=np.asarray(Image.open(source).convert('RGB'),dtype=np.float32);bp=np.asarray(Image.open(base).convert('RGB'),dtype=np.float32)
 got=np.uint8(np.clip(np.rint(bp+np.clip(s+np.clip(field,-40,40)-bp,-40,40)),0,255))
 actual=np.asarray(Image.open(target).convert('RGB'))
 assert sha(source)==rec['derivedFrom'][0]['sha256'] and sha(target)==rec['sha256'] and sha(ev['file'])==ev['sha256']
 assert np.array_equal(got,actual)
 checks.append({'patch':pid,'source':str(source),'sourceSha256':sha(source),'output':str(target),'outputSha256':sha(target),'exactAdditiveReplay':True,'maxChange':int(np.abs(actual.astype(np.float32)-s).max())})
out={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'selection':str(selection),'selectionSha256':sha(selection),'checks':checks,'allExact':True,'noGeometryResamplingOrBlur':True,'maxChange':max(c['maxChange'] for c in checks)}
folder=HERE/sys.argv[1];folder.mkdir(exist_ok=True)
(folder/'independent-color-replay.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'tile':sys.argv[1],'allExact':True,'maxChange':out['maxChange'],'sourceCount':len(checks)}))
