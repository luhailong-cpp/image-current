from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;d=T/'repair-batches/roof-truncation-02';q=d/'trials/v02-binary-seam';q.mkdir(parents=True,exist_ok=False)
a=json.loads((d/'derivation.json').read_text());old=np.array(Image.open(d/'edit-target.png').convert('RGB'));new=np.array(Image.open(d/'native.png').convert('RGB'));diff=np.mean(np.abs(old.astype(float)-new.astype(float)),axis=2)
def path(cost):
 h,w=cost.shape;dp=cost[0].copy();parents=np.zeros((h,w),np.int8)
 for y in range(1,h):
  options=np.stack([np.r_[np.inf,dp[:-1]]+.03,dp,np.r_[dp[1:],np.inf]+.03]);ix=options.argmin(axis=0);parents[y]=ix-1;dp=cost[y]+options[ix,np.arange(w)]
 out=np.empty(h,np.int32);out[-1]=int(dp.argmin())
 for y in range(h-1,0,-1):out[y-1]=out[y]+parents[y,out[y]]
 return out
left=path(diff[410:901,570:621])+570;right=path(diff[410:901,690:726])+690;top=path(diff[410:451,570:726].T)+410;bottom=path(diff[820:901,570:726].T)+820
mask=np.zeros((1254,1254),bool)
for y in range(410,901):
 for x in range(570,726):mask[y,x]=left[y-410]<=x<right[y-410] and top[x-570]<=y<bottom[x-570]
out=old.copy();out[mask]=new[mask];Image.fromarray(mask.astype(np.uint8)*255).save(q/'native-mask.png');Image.fromarray(out).save(q/'trial-frame.png')
base=np.array(Image.open(a['source']).convert('RGB'));x,y=a['tileCropLTRB'][:2];region=base[y:y+1254,x:x+1254];region[mask]=new[mask];Image.fromarray(base).save(q/'candidate.png')
box=[x+490,y+330,x+806,y+981];Image.fromarray(base).crop(box).save(q/'perimeter.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(q/'manifest.json').write_text(json.dumps(dict(nativeSource=str(d/'native.png'),nativeSha256=sha(d/'native.png'),worldBox=a['worldBox'],tileOriginXY=[x,y],mask=str(q/'native-mask.png'),maskSha256=sha(q/'native-mask.png'),nativeSelectedPixelCount=int(mask.sum()),output=str(q/'candidate.png'),outputSha256=sha(q/'candidate.png'),perimeterCrop=dict(file=str(q/'perimeter.png'),tileCropLTRB=box,sha256=sha(q/'perimeter.png')),method='Exact same-world binary native selection using four minimum-pixel-difference paths. No resized/recolored/interpolated/feathered pixels.',formalAccepted=False),indent=2)+'\n')
print(json.dumps(dict(file=str(q/'candidate.png'),sha256=sha(q/'candidate.png'),pixelsSelected=int(mask.sum()))))
