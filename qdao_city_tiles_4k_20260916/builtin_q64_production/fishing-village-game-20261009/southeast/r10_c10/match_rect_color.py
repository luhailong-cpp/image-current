"""Match only a bounded additive RGB field on an edited rectangle. Never blur/resample image pixels."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
base_rel,edit_rel,out_rel=sys.argv[1:4]
rect=list(map(int,sys.argv[4:8]));x0,y0,x1,y1=rect
base=T/base_rel;edit=T/edit_rel;out=T/out_rel;assert not out.exists()
a=np.asarray(Image.open(base).convert('RGB'),dtype=np.float32)
b=np.asarray(Image.open(edit).convert('RGB'),dtype=np.float32);assert a.shape==b.shape==(1254,1254,3)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def grad(a):return np.maximum(np.max(np.abs(np.gradient(a,axis=0)),axis=2),np.max(np.abs(np.gradient(a,axis=1)),axis=2))
g1=grad(a);g2=grad(b)
good=(g1<8)&(g2<8)&(np.max(np.abs(a-b),axis=2)<70)
diff=a-b
stats=[]
def curve(side):
 vertical=side in ('left','right')
 n=(y1-y0) if vertical else (x1-x0)
 centers=list(range(0,n,32))
 if centers[-1]!=n-1:centers.append(n-1)
 vals=[]
 for t in centers:
  lo=max(0,t-32);hi=min(n,t+33)
  if vertical:
   x=x0 if side=='left' else x1-1
   box=(max(0,x-6),y0+lo,min(1254,x+7),y0+hi)
  else:
   y=y0 if side=='top' else y1-1
   box=(x0+lo,max(0,y-6),x0+hi,min(1254,y+7))
  l,t0,r,d=box;m=good[t0:d,l:r];v=diff[t0:d,l:r][m]
  value=np.median(v,axis=0) if len(v)>=8 else np.zeros(3)
  vals.append(np.clip(value,-40,40));stats.append({'side':side,'box':box,'acceptedPixels':len(v),'additiveRGB':vals[-1].tolist()})
 return np.stack([np.interp(np.arange(n),centers,np.array(vals)[:,k]) for k in range(3)],axis=1)
L,R,U,D=[curve(s) for s in ('left','right','top','bottom')]
h,w=y1-y0,x1-x0
yy,xx=np.indices((h,w),dtype=np.float32)
ds=[xx,w-1-xx,yy,h-1-yy]
weights=[]
for d in ds:
 q=np.clip(d/160,0,1);weights.append((1-q*q*(3-2*q))/(d+1))
fields=[L[:,None,:],R[:,None,:],U[None,:,:],D[None,:,:]]
field=sum(v*wt[:,:,None] for v,wt in zip(fields,weights))/np.maximum(sum(weights)[:,:,None],1e-8)
fade=np.maximum.reduce([np.clip(1-d/160,0,1) for d in ds])
field*=fade[:,:,None]
field=np.clip(field,-40,40)
result=b.copy();result[y0:y1,x0:x1]=np.clip(np.rint(b[y0:y1,x0:x1]+field),0,255)
result=result.astype('uint8');out.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(result).save(out)
fp=out.with_suffix('.field.npz');np.savez_compressed(fp,additiveField=field,rectangle=np.array(rect))
delta=result.astype(np.int16)-b.astype(np.int16);assert np.abs(delta).max()<=40
mask=np.ones((1254,1254),bool);mask[y0:y1,x0:x1]=False
assert np.array_equal(result[mask],b.astype('uint8')[mask])
rec={'file':str(out),'sha256':sha(out),'nativeDimensions':[1254,1254],'operation':'bounded low-frequency additive RGB field on edited image; source pixel geometry unchanged','baseColorAnchor':{'path':str(base),'sha256':sha(base)},'editedSource':{'path':str(edit),'sha256':sha(edit)},'rectangle':rect,'field':{'path':str(fp),'sha256':sha(fp)},'parameters':{'limit':40,'sampleWidth':13,'profileStep':32,'sampleProfileHalfWidth':32,'gradientMax':8,'incompatibleDifferenceMax':70,'inwardSupport':160,'fieldInterpolationOnly':True},'sampling':stats,'maximumActualChannelChange':int(np.abs(delta).max()),'resamplingApplied':False,'imageBlur':False,'imagePixelBlend':False,'coordinateShift':[0,0],'outsideRectanglePixelsIdentical':True,'script':str(Path(__file__)),'scriptSha256':sha(__file__)}
out.with_suffix('.png.derivation.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'maxRGBChange':int(np.abs(delta).max())}))

