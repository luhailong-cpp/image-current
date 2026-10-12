from pathlib import Path
from PIL import Image
import numpy as np
import json, hashlib, sys
sys.dont_write_bytecode=True
Z=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(Z))
from join_vertical import minimum_error_path
Q=Z/'qa/s04_02_a01_base_a02_body_trial';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pa=Z/'native/r03_c03_s04_02_a01.png';pb=Z/'native/r03_c03_s04_02_a02.png'
a=np.asarray(Image.open(pa).convert('RGB'));b=np.asarray(Image.open(pb).convert('RGB'))
assert a.shape==b.shape==(1254,1254,3)
x0,x1,y0,y1=300,870,150,341
delta=a[y0:y1,x0:x1].astype(float)-b[y0:y1,x0:x1].astype(float)
cost=np.mean(delta*delta,axis=2).T
def gold(arr):
 f=arr.astype(float)
 return (f[...,0]>135)&(f[...,1]>f[...,0]*.50)&(f[...,2]<f[...,1]*.88)
both=(gold(a[y0:y1,x0:x1])&gold(b[y0:y1,x0:x1])).T
for ix,x in enumerate(range(x0,x1)):
 if 365<=x<=795:cost[ix]+=np.where(both[ix],0,10000)
seam=minimum_error_path(cost)+y0
mask=np.zeros((1254,1254),dtype=bool)
for ix,x in enumerate(range(x0,x1)):mask[:int(seam[ix]),x]=True
out=np.where(mask[...,None],b,a)
assert np.array_equal(out[~mask],a[~mask]) and np.array_equal(out[mask],b[mask])
im=Image.fromarray(out);op=Q/'composite.png';im.save(op)
mp=Q/'source_selection_mask.png';Image.fromarray(mask.astype('uint8')*255).save(mp)
detail=Q/'base_join100pct.png';im.crop((280,100,890,430)).save(detail)
rec=dict(operation='same-coordinate selection of two AI-native sources; not new AI generation',sources=[dict(path=pa.as_posix(),sha256=sha(pa),role='base; all ground/side/bottom and original cylinder lower rim'),dict(path=pb.as_posix(),sha256=sha(pb),role='repaired upper cylinder body only')],mask=dict(path=mp.as_posix(),sha256=sha(mp),whiteSource=pb.as_posix(),blackSource=pa.as_posix()),output=dict(path=op.as_posix(),sha256=sha(op),dimensions=[1254,1254]),method=dict(sourceCoordinateTransform='identity',alphaBlending=False,colorCorrection=False,resizing=False,painting=False,hardSeam=True,bottomPathPerX=seam.tolist(),xRangeHalfOpen=[x0,x1],cost='RGB MSE plus 10000 penalty outside common gold for cylinder interior x365..795',searchYRangeHalfOpen=[y0,y1]),status='pending_visual_review')
(Q/'record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(op),'seamMinMax':[int(seam.min()),int(seam.max())]}))
