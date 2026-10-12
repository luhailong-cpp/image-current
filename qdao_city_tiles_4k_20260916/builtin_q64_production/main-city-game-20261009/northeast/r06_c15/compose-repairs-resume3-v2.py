from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
T=Path(__file__).resolve().parent
R=T/'qa/local-repair-resume3-20261013';R.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((T/'qa/local-repair-resume2-20261013/composition-v1.json').read_text())
base=Path(old['base']);assert sha(base)==old['baseSha256']
im=Image.open(base).convert('RGB')
# Bands constrain an integer binary source-selection seam; no output pixel is painted,
# interpolated, feathered, rescaled, or shifted. Every selected pixel has one native source.
bands={
 'panel':(20,260,980,1220,20,460,850,1230),
 'ledge':(20,250,1050,1230,100,620,1110,1230),
 'roof':(20,340,1180,1230,20,440,850,1230),
 'trunk':(150,390,660,1000,20,180,850,1230),
 'wallrail':(20,185,1040,1230,20,150,1040,1230),
 'fascia':(20,150,800,1230,20,350,850,1230),
 'upperroof':(20,170,1180,1230,20,460,1000,1230),
}
def path(cost,lo,hi):
 a=cost[lo:hi+1,:].T
 parent=np.empty(a.shape,dtype=np.int8);d=a[0].copy()
 for x in range(1,len(a)):
  p=np.stack((np.r_[np.inf,d[:-1]],d,np.r_[d[1:],np.inf]))
  k=np.argmin(p,axis=0);parent[x]=k-1
  d=a[x]+p[k,np.arange(len(d))]
 ys=np.empty(len(a),dtype=np.int32);ys[-1]=int(np.argmin(d))
 for x in range(len(a)-1,0,-1):ys[x-1]=ys[x]+parent[x,ys[x]]
 return ys+lo
layers=[]
for layer in old['layers']:
 name=layer['id'];src=Path(layer['file']);assert sha(src)==layer['sha256']
 x,y=layer['targetOrigin'];native=Image.open(src).convert('RGB');assert native.size==(1254,1254)
 before=im.crop((x,y,x+1254,y+1254));a=np.asarray(before,dtype=np.float32);b=np.asarray(native,dtype=np.float32)
 cost=np.abs(a-b).mean(axis=2)+1
 # Matching geometry costs more than small material variation.
 cost+=np.abs(np.diff(a,axis=0,prepend=a[:1])-np.diff(b,axis=0,prepend=b[:1])).mean(axis=2)*2
 cost+=np.abs(np.diff(a,axis=1,prepend=a[:,:1])-np.diff(b,axis=1,prepend=b[:,:1])).mean(axis=2)*2
 xl,xh,rl,rh,tl,th,bl,bh=bands[name]
 left=path(cost.T,xl,xh);right=path(cost.T,rl,rh)
 top=path(cost,tl,th);bottom=path(cost,bl,bh)
 yy,xx=np.indices(cost.shape)
 mask=(xx>=left[:,None])&(xx<=right[:,None])&(yy>=top[None,:])&(yy<=bottom[None,:])
 mf=R/(name+'-binary-source-mask-v2.png');assert not mf.exists()
 mi=Image.fromarray(mask.astype(np.uint8)*255);mi.save(mf)
 im.paste(native,(x,y),mi)
 layers.append(dict(layer,mask=str(mf),maskSha256=sha(mf),selectedPixelCount=int(mask.sum()),sourceSelectionOnly=True))
dest=T/'candidates/r06_c15.local-repairs-resume3-v2.png';assert not dest.exists();im.save(dest)
for layer in layers:
 x,y=layer['targetOrigin'];out=R/(layer['id']+'-composited-v2.png');assert not out.exists();im.crop((x,y,x+1254,y+1254)).save(out)
report=dict(old,candidate=str(dest),candidateSha256=sha(dest),layers=layers,status='boundaries-awaiting-visual-review',operation='integer native source selection through binary masks; no painting, resampling, feathering, interpolation, or geometric transformation')
(R/'composition-v2.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'candidate':str(dest),'sha256':sha(dest)}))
