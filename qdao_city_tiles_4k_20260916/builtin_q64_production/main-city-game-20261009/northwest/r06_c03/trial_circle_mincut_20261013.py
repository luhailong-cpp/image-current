from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;d=T/'repair-batches/circular-anchor-02';q=d/'trials/v03-binary-seam';q.mkdir(parents=True,exist_ok=False)
a=json.loads((d/'derivation.json').read_text());old=np.array(Image.open(d/'edit-target.png').convert('RGB'));new=np.array(Image.open(d/'native.png').convert('RGB'))
y0,y1=285,925;lo,hi=1090,1253
diff=np.mean(np.abs(old.astype(float)-new.astype(float)),axis=2)
# Only select a path between immutable same-world pixels. This cost never enters rendered artwork.
cost=diff[y0:y1,lo:hi+1].copy();gradold=np.diff(old.astype(float),axis=1,prepend=old[:,:1]);gradnew=np.diff(new.astype(float),axis=1,prepend=new[:,:1])
cost+=np.mean(np.abs(gradold-gradnew),axis=2)[y0:y1,lo:hi+1]*.4
h,w=cost.shape;dp=cost[0].copy();parents=np.zeros((h,w),np.int8)
for y in range(1,h):
 options=np.stack([np.r_[np.inf,dp[:-1]]+.03,dp,np.r_[dp[1:],np.inf]+.03])
 ix=options.argmin(axis=0);parents[y]=ix-1;dp=cost[y]+options[ix,np.arange(w)]
path=np.empty(h,np.int32);path[-1]=int(dp.argmin())
for y in range(h-1,0,-1):path[y-1]=path[y]+parents[y,path[y]]
path+=lo;mask=np.zeros((1254,1254),bool)
for y,x in enumerate(path,y0):mask[y,390:int(x)]=True
out=old.copy();out[mask]=new[mask]
Image.fromarray(mask.astype(np.uint8)*255).save(q/'native-mask.png');Image.fromarray(out).save(q/'trial-frame.png')
base=np.array(Image.open(a['source']).convert('RGB'));x,y=a['tileCropLTRB'][:2];region=base[y:y+1254,x:x+1254];region[mask]=new[mask];Image.fromarray(base).save(q/'candidate.png')
Image.fromarray(base).crop((x+lo-80,y+y0-80,x+1254+80,y+y1+80)).save(q/'right-perimeter.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(q/'manifest.json').write_text(json.dumps(dict(nativeSource=str(d/'native.png'),nativeSha256=sha(d/'native.png'),worldBox=a['worldBox'],tileOriginXY=[x,y],mask=str(q/'native-mask.png'),maskSha256=sha(q/'native-mask.png'),nativeSelectedPixelCount=int(mask.sum()),rightPathSourceX=path.tolist(),rightPathSourceYStart=y0,output=str(q/'candidate.png'),outputSha256=sha(q/'candidate.png'),method='Exact same-world binary native selection only; minimum difference path. No resized/recolored/interpolated/feathered pixels.',formalAccepted=False),indent=2)+'\n')
print(json.dumps(dict(file=str(q/'candidate.png'),sha256=sha(q/'candidate.png'),pixelsSelected=int(mask.sum()),pathMin=int(path.min()),pathMax=int(path.max()))))
