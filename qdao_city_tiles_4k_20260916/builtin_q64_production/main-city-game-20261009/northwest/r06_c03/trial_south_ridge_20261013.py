from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;d=T/'repair-batches/south-ridge-step-01';q=d/'trials/v01-binary-seam';q.mkdir(parents=True,exist_ok=False)
a=json.loads((d/'derivation.json').read_text());old=np.array(Image.open(d/'edit-target.png').convert('RGB'));new=np.array(Image.open(d/'native.png').convert('RGB'));diff=np.mean(np.abs(old.astype(float)-new.astype(float)),axis=2)
def path(cost):
 h,w=cost.shape;dp=cost[0].copy();parents=np.zeros((h,w),np.int8)
 for y in range(1,h):
  options=np.stack([np.r_[np.inf,dp[:-1]]+.03,dp,np.r_[dp[1:],np.inf]+.03]);ix=options.argmin(axis=0);parents[y]=ix-1;dp=cost[y]+options[ix,np.arange(w)]
 out=np.empty(h,np.int32);out[-1]=int(dp.argmin())
 for y in range(h-1,0,-1):out[y-1]=out[y]+parents[y,out[y]]
 return out
left=path(diff[570:1254,240:431])+240;right=path(diff[570:1254,1130:1241])+1130;top=path(diff[570:731,240:1241].T)+570
mask=np.zeros((1254,1254),bool)
for y in range(570,1254):
 for x in range(240,1241):mask[y,x]=left[y-570]<=x<right[y-570] and y>=top[x-240]
out=old.copy();out[mask]=new[mask];Image.fromarray(mask.astype(np.uint8)*255).save(q/'native-mask.png');Image.fromarray(out).save(q/'trial-frame.png')
base=np.array(Image.open(a['source']).convert('RGB'));x,y=a['tileCropLTRB'][:2];base[y:y+1254,x:x+1254][mask]=new[mask];Image.fromarray(base).save(q/'candidate.png')
boxes={'top':[x+160,y+490,x+1254,y+810],'left':[x+160,y+490,x+510,y+1254],'right':[x+1050,y+490,min(4096,x+1320),y+1254],'junction':[x+467,y+670,x+787,y+1254]}
for name,box in boxes.items():Image.fromarray(base).crop(box).save(q/(name+'.png'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(q/'manifest.json').write_text(json.dumps(dict(nativeSource=str(d/'native.png'),nativeSha256=sha(d/'native.png'),worldBox=a['worldBox'],tileOriginXY=[x,y],mask=str(q/'native-mask.png'),maskSha256=sha(q/'native-mask.png'),nativeSelectedPixelCount=int(mask.sum()),output=str(q/'candidate.png'),outputSha256=sha(q/'candidate.png'),perimeters={k:dict(file=str(q/(k+'.png')),tileCropLTRB=b,sha256=sha(q/(k+'.png'))) for k,b in boxes.items()},bottomEdge='Tile bottom y4096; no accepted south neighbor exists. Source is continued to physical tile edge without fabricated halo.',method='Exact same-world binary native selection. No resized/recolored/interpolated/feathered pixels.',formalAccepted=False),indent=2)+'\n')
print(json.dumps(dict(file=str(q/'candidate.png'),sha256=sha(q/'candidate.png'),pixelsSelected=int(mask.sum()))))
