from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;d=T/'repair-batches/internal-wall-strip-01';q=d/'trials/v01-binary-seam';q.mkdir(parents=True,exist_ok=False);a=json.loads((d/'derivation.json').read_text());old=np.array(Image.open(d/'edit-target.png').convert('RGB'));new=np.array(Image.open(d/'native.png').convert('RGB'));diff=np.mean(np.abs(old.astype(float)-new.astype(float)),axis=2)
def path(cost):
 h,w=cost.shape;dp=cost[0].copy();parents=np.zeros((h,w),np.int8)
 for y in range(1,h):
  options=np.stack([np.r_[np.inf,dp[:-1]]+.03,dp,np.r_[dp[1:],np.inf]+.03]);ix=options.argmin(axis=0);parents[y]=ix-1;dp=cost[y]+options[ix,np.arange(w)]
 out=np.empty(h,np.int32);out[-1]=int(dp.argmin())
 for y in range(h-1,0,-1):out[y-1]=out[y]+parents[y,out[y]]
 return out
ranges=[[500,570,690,780,280,300,390,430],[490,570,690,760,490,545,660,710],[500,565,690,770,740,800,915,970]];mask=np.zeros((1254,1254),bool)
for x0,xl,xr,x1,y0,yt,yb,y1 in ranges:
 left=path(diff[y0:y1+1,x0:xl+1])+x0;right=path(diff[y0:y1+1,xr:x1+1])+xr;top=path(diff[y0:yt+1,x0:x1+1].T)+y0;bottom=path(diff[yb:y1+1,x0:x1+1].T)+yb
 for yy in range(y0,y1+1):
  for xx in range(x0,x1+1):mask[yy,xx]|=left[yy-y0]<=xx<right[yy-y0] and top[xx-x0]<=yy<bottom[xx-x0]
out=old.copy();out[mask]=new[mask];Image.fromarray(out).save(q/'trial-frame.png');Image.fromarray(mask.astype(np.uint8)*255).save(q/'native-mask.png');base=np.array(Image.open(a['source']).convert('RGB'));x,y=a['tileCropLTRB'][:2];base[y:y+1254,x:x+1254][mask]=new[mask];Image.fromarray(base).save(q/'candidate.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
crops=[]
for i,r in enumerate(ranges):
 box=[r[0]-80,r[4]-80,r[3]+80,r[7]+80];p=q/('beam'+str(i+1)+'-perimeter.png');Image.fromarray(out).crop(box).save(p);crops.append(dict(file=str(p),frameCropLTRB=box,sha256=sha(p)))
(q/'manifest.json').write_text(json.dumps(dict(nativeSource=str(d/'native.png'),nativeSha256=sha(d/'native.png'),worldBox=a['worldBox'],tileOriginXY=[x,y],mask=str(q/'native-mask.png'),maskSha256=sha(q/'native-mask.png'),nativeSelectedPixelCount=int(mask.sum()),output=str(q/'candidate.png'),outputSha256=sha(q/'candidate.png'),perimeterCrops=crops,selectionRanges=ranges,method='Exact same-world binary native selection using disjoint minimum-pixel-difference boundary paths; no resize/blend/feather/recolor.',formalAccepted=False),indent=2)+'\n');print(json.dumps(dict(file=str(q/'candidate.png'),sha256=sha(q/'candidate.png'),pixelsSelected=int(mask.sum()))))
