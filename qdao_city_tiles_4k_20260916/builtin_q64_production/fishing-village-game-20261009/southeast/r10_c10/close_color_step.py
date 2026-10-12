"""Remove a local material color step using only a bounded additive field."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
source_rel,out_rel,axis=sys.argv[1:4];seam,lo,hi,support=map(int,sys.argv[4:8])
source=T/source_rel;out=T/out_rel;assert not out.exists()
a=np.asarray(Image.open(source).convert('RGB'),dtype=np.float32);assert a.shape==(1254,1254,3)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
v=a if axis=='vertical' else a.transpose(1,0,2)
# v has seam along x; profile position y.
n=hi-lo;centers=list(range(lo,hi,32))+[hi-1];vals=[];samples=[]
for p in centers:
 y0=max(lo,p-32);y1=min(hi,p+33)
 left=v[y0:y1,seam-13:seam-1];right=v[y0:y1,seam+1:seam+13]
 def g(b):return np.maximum(np.max(np.abs(np.gradient(b,axis=0)),axis=2),np.max(np.abs(np.gradient(b,axis=1)),axis=2))
 ok=(g(left)<8)&(g(right)<8)&(np.max(np.abs(right-left),axis=2)<70)
 diff=(right-left)[ok];value=np.median(diff,axis=0) if len(diff)>12 else np.zeros(3)
 vals.append(np.clip(value*.5,-20,20));samples.append({'center':p,'accepted':len(diff),'halfDifferenceRGB':vals[-1].tolist()})
profile=np.stack([np.interp(np.arange(lo,hi),centers,np.array(vals)[:,ch]) for ch in range(3)],axis=1)
yy=np.arange(lo,hi);endfade=np.minimum(np.clip((yy-lo)/48,0,1),np.clip((hi-1-yy)/48,0,1))
profile*=endfade[:,None]
xx=np.arange(1254);d=np.abs(xx+.5-seam);q=np.clip(d/support,0,1);weight=1-q*q*(3-2*q);weight*=np.where(xx<seam,1,-1)
field=np.zeros_like(v);field[lo:hi]=profile[:,None,:]*weight[None,:,None]
if axis!='vertical':field=field.transpose(1,0,2)
result=np.uint8(np.clip(np.rint(a+field),0,255));out.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(result).save(out)
fp=out.with_suffix('.field.npz');np.savez_compressed(fp,additiveField=field)
rec={'file':str(out),'sha256':sha(out),'nativeDimensions':[1254,1254],'derivedFrom':{'path':str(source),'sha256':sha(source)},'operation':'bounded low-frequency additive RGB half-difference field at certified material color step','parameters':{'axis':axis,'seam':seam,'profileRange':[lo,hi],'support':support,'sampleWidth':12,'profileStep':32,'gradientMax':8,'incompatibleRGBMax':70,'limit':20,'endpointFade':48},'samples':samples,'maximumActualRGBDelta':int(np.abs(result.astype(np.int16)-a.astype(np.int16)).max()),'field':{'path':str(fp),'sha256':sha(fp)},'imageBlur':False,'imagePixelBlend':False,'resamplingApplied':False,'coordinateShift':[0,0],'script':str(Path(__file__)),'scriptSha256':sha(__file__)}
out.with_suffix('.png.derivation.json').write_text(json.dumps(rec,indent=2),encoding='utf-8');print(json.dumps({'file':str(out),'maximumRGBDelta':rec['maximumActualRGBDelta']}))

