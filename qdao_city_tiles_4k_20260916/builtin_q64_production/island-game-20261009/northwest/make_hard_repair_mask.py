"""Select unmodified same-coordinate native pixels with binary hard seams; no painting."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,argparse
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(e):
 h,w=e.shape;cost=e[0].copy();prev=np.zeros((h,w),np.int8)
 for y in range(1,h):
  c=np.stack([np.r_[np.inf,cost[:-1]],cost,np.r_[cost[1:],np.inf]])
  choice=np.argmin(c,axis=0);prev[y]=choice-1;cost=c[choice,np.arange(w)]+e[y]
 p=np.empty(h,np.int32);p[-1]=np.argmin(cost)
 for y in range(h-1,0,-1):p[y-1]=p[y]+prev[y,p[y]]
 return p
ap=argparse.ArgumentParser();ap.add_argument('--target',required=True);ap.add_argument('--repair',required=True);ap.add_argument('--inner',type=int,nargs=4,required=True);ap.add_argument('--outer',type=int,nargs=4,required=True);ap.add_argument('--output-dir',required=True);a=ap.parse_args()
target=Path(a.target).resolve();repair=Path(a.repair).resolve();out=Path(a.output_dir).resolve();assert out.is_relative_to(Z)
old=np.array(Image.open(target).convert('RGB'));new=np.array(Image.open(repair).convert('RGB'));assert old.shape==new.shape==(1254,1254,3)
ox0,oy0,ox1,oy1=a.outer;ix0,iy0,ix1,iy1=a.inner
assert 0<=ox0<=ix0<ix1<=ox1<=1254 and 0<=oy0<=iy0<iy1<=oy1<=1254
assert (ox0<ix0 or ox0==ix0==0) and (ix1<ox1 or ix1==ox1==1254)
assert (oy0<iy0 or oy0==iy0==0) and (iy1<oy1 or iy1==oy1==1254)
assert not out.exists();out.mkdir(parents=True)
error=((old.astype(float)-new.astype(float))**2).mean(2)
left=np.zeros(oy1-oy0,np.int32) if ox0==ix0==0 else ox0+path(error[oy0:oy1,ox0:ix0+1])
right=np.full(oy1-oy0,1254,np.int32) if ix1==ox1==1254 else ix1+path(error[oy0:oy1,ix1:ox1])
top=np.zeros(ox1-ox0,np.int32) if oy0==iy0==0 else oy0+path(error[oy0:iy0+1,ox0:ox1].T)
bottom=np.full(ox1-ox0,1254,np.int32) if iy1==oy1==1254 else iy1+path(error[iy1:oy1,ox0:ox1].T)
yy,xx=np.mgrid[oy0:oy1,ox0:ox1]
inside=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:])
mask=np.zeros((1254,1254),bool);mask[oy0:oy1,ox0:ox1]=inside
assert mask[iy0:iy1,ix0:ix1].all()
joined=old.copy();joined[mask]=new[mask];assert np.array_equal(joined[~mask],old[~mask]) and np.array_equal(joined[mask],new[mask])
mp=out/'source_selection_mask.png';jp=out/'combined_native_crop.png'
Image.fromarray(mask.astype(np.uint8)*255).save(mp);Image.fromarray(joined).save(jp)
rec=dict(operation='same-coordinate native hard source selection; four minimum RGB-error boundaries',isAiGeneration=False,registration=False,resizing=False,feathering=False,colorCorrection=False,pixelSynthesis=False,target=dict(path=target.as_posix(),sha256=sha(target)),repair=dict(path=repair.as_posix(),sha256=sha(repair)),mask=dict(path=mp.as_posix(),sha256=sha(mp),zeroSource='target',value255Source='repair'),combinedCrop=dict(path=jp.as_posix(),sha256=sha(jp)),outerBox=a.outer,mandatoryRepairCore=a.inner,repairPixelCount=int(mask.sum()),targetPixelCount=int((~mask).sum()),paths=dict(leftXByY=left.tolist(),rightXByY=right.tolist(),topYByX=top.tolist(),bottomYByX=bottom.tolist(),coordinateNote='y domain outer y0:y1 for left/right, x domain outer x0:x1 for top/bottom'),visualStatus='pending_native_boundary_review')
(out/'mask_selection.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(mask=mp.as_posix(),combinedCrop=jp.as_posix(),repairPixelCount=int(mask.sum()))))

