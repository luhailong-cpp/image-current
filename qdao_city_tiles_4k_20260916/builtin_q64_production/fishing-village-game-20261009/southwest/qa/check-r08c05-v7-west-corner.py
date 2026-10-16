import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
left=Q/'block2x2-r09r10c03c04-v1-r09_c04-context-native.png';right=Q/'block2x2-r08r09c05c06-v7-r09_c05-context-native.png';old=Q/'pair-r09c05-c06-northupdate-v1-r09_c05-context-native.png'
a=np.asarray(Image.open(left).convert('RGB'));b=np.asarray(Image.open(right).convert('RGB'));c=np.asarray(Image.open(old).convert('RGB'))
out=np.concatenate([a[115:1015,3866:4211],b[115:1015,115:460]],axis=1);p=Q/'block2x2-r08r09c05c06-v7-west-external-top-direct-100pct.png';assert not p.exists();Image.fromarray(out).save(p)
diff=np.any(b[:,:230]!=c[:,:230],axis=2);ys,xs=np.where(diff)
d={'qa':ref(p),'left':ref(left),'right':ref(right),'operation':'integer core crops, direct concatenation with actual export boundary at x345; no resizing','changedWestOverlapBoundingBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'belowChangedBoxIdentical':bool(np.array_equal(b[ys.max()+1:,:230],c[ys.max()+1:,:230]))}
with (Q/'block2x2-r08r09c05c06-v7-west-external-top-check.json').open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
print(json.dumps(d))
