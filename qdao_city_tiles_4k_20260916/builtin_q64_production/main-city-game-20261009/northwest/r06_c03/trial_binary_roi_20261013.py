from pathlib import Path
import numpy as np,json,hashlib,sys
from PIL import Image
T=Path(__file__).resolve().parent;name,version=sys.argv[1:3];x0,xl,xr,x1,y0,yt,yb,y1=map(int,sys.argv[3:]);d=T/'repair-batches'/name;q=d/'trials'/version;q.mkdir(parents=True,exist_ok=False)
a=json.loads((d/'derivation.json').read_text());old=np.array(Image.open(d/'edit-target.png').convert('RGB'));new=np.array(Image.open(d/'native.png').convert('RGB'));diff=np.mean(np.abs(old.astype(float)-new.astype(float)),axis=2)
def path(cost):
 h,w=cost.shape;dp=cost[0].copy();parents=np.zeros((h,w),np.int8)
 for y in range(1,h):
  options=np.stack([np.r_[np.inf,dp[:-1]]+.03,dp,np.r_[dp[1:],np.inf]+.03]);ix=options.argmin(axis=0);parents[y]=ix-1;dp=cost[y]+options[ix,np.arange(w)]
 out=np.empty(h,np.int32);out[-1]=int(dp.argmin())
 for y in range(h-1,0,-1):out[y-1]=out[y]+parents[y,out[y]]
 return out
left=path(diff[y0:y1+1,x0:xl+1])+x0;right=path(diff[y0:y1+1,xr:x1+1])+xr;top=path(diff[y0:yt+1,x0:x1+1].T)+y0;bottom=path(diff[yb:y1+1,x0:x1+1].T)+yb
mask=np.zeros((1254,1254),bool)
for y in range(y0,y1+1):
 for x in range(x0,x1+1):mask[y,x]=left[y-y0]<=x<right[y-y0] and top[x-x0]<=y<bottom[x-x0]
out=old.copy();out[mask]=new[mask];Image.fromarray(mask.astype(np.uint8)*255).save(q/'native-mask.png');Image.fromarray(out).save(q/'trial-frame.png')
base=np.array(Image.open(a['source']).convert('RGB'));x,y=a['tileCropLTRB'][:2];region=base[y:y+1254,x:x+1254];region[mask]=new[mask];Image.fromarray(base).save(q/'candidate.png')
box=[x+max(0,x0-80),y+max(0,y0-80),x+min(1254,x1+80),y+min(1254,y1+80)];Image.fromarray(base).crop(box).save(q/'perimeter.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(q/'manifest.json').write_text(json.dumps(dict(nativeSource=str(d/'native.png'),nativeSha256=sha(d/'native.png'),worldBox=a['worldBox'],tileOriginXY=[x,y],mask=str(q/'native-mask.png'),maskSha256=sha(q/'native-mask.png'),nativeSelectedPixelCount=int(mask.sum()),output=str(q/'candidate.png'),outputSha256=sha(q/'candidate.png'),perimeterCrop=dict(file=str(q/'perimeter.png'),tileCropLTRB=box,sha256=sha(q/'perimeter.png')),selectionRanges=[x0,xl,xr,x1,y0,yt,yb,y1],method='Exact same-world binary native selection using four minimum-pixel-difference paths. No resized/recolored/interpolated/feathered pixels.',formalAccepted=False),indent=2)+'\n')
print(json.dumps(dict(file=str(q/'candidate.png'),sha256=sha(q/'candidate.png'),pixelsSelected=int(mask.sum()))))
