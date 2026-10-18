from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image
T=Path(__file__).resolve().parent;d=T/'repair-batches/east-gold-material-01';q=d/'trials/v01-binary-seam';q.mkdir(parents=True,exist_ok=False)
a=json.loads((d/'derivation.json').read_text());old=np.array(Image.open(d/'edit-target.png').convert('RGB'));new=np.array(Image.open(d/'native.png').convert('RGB'));diff=np.mean(np.abs(old.astype(float)-new.astype(float)),axis=2)
def path(cost):
 h,w=cost.shape;dp=cost[0].copy();parents=np.zeros((h,w),np.int8)
 for y in range(1,h):
  options=np.stack([np.r_[np.inf,dp[:-1]]+.03,dp,np.r_[dp[1:],np.inf]+.03]);ix=options.argmin(axis=0);parents[y]=ix-1;dp=cost[y]+options[ix,np.arange(w)]
 out=np.empty(h,np.int32);out[-1]=int(dp.argmin())
 for y in range(h-1,0,-1):out[y-1]=out[y]+parents[y,out[y]]
 return out
left=path(diff[570:801,420:531])+420;top=path(diff[570:626,420:627].T)+570;bottom=path(diff[735:801,420:627].T)+735
mask=np.zeros((1254,1254),bool)
for y in range(570,801):
 for x in range(420,627):mask[y,x]=x>=left[y-570] and top[x-420]<=y<bottom[x-420]
out=old.copy();out[mask]=new[mask];assert np.array_equal(out[:,627:],old[:,627:]);Image.fromarray(mask.astype(np.uint8)*255).save(q/'native-mask.png');Image.fromarray(out).save(q/'trial-frame.png')
base=np.array(Image.open(a['source']).convert('RGB'));x,y=a['tileCropLTRB'][:2];region=base[y:y+1254,x:4096];region[mask[:,:627]]=new[:,:627][mask[:,:627]];Image.fromarray(base).save(q/'candidate.png')
box=[340,490,820,890];Image.fromarray(out).crop(box).save(q/'perimeter.png');Image.fromarray(old).crop(box).save(q/'before.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(q/'manifest.json').write_text(json.dumps(dict(nativeSource=str(d/'native.png'),nativeSha256=sha(d/'native.png'),worldBox=a['worldBox'],tileOriginXY=[x,y],mask=str(q/'native-mask.png'),maskSha256=sha(q/'native-mask.png'),nativeSelectedPixelCount=int(mask.sum()),output=str(q/'candidate.png'),outputSha256=sha(q/'candidate.png'),perimeterCrop=dict(file=str(q/'perimeter.png'),frameCropLTRB=box,sha256=sha(q/'perimeter.png')),actualEastNeighborUnchanged=True,method='Exact same-world binary native selection; left/top/bottom minimum pixel-difference paths and fixed right ownership border x627. No resize or pixel synthesis.',formalAccepted=False),indent=2)+'\n')
print(json.dumps(dict(file=str(q/'candidate.png'),sha256=sha(q/'candidate.png'),pixelsSelected=int(mask.sum()))))
