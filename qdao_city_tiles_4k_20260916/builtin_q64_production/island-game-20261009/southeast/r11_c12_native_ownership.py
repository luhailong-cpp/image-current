"""Mechanical same-coordinate native ownership; no new colors, resampling or blending."""
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
R=Path(__file__).parent;name=sys.argv[1];native=R/'native'/f'{name}.png';rec=json.loads(Path(str(native)+'.generation.json').read_text(encoding='utf-8'));box=rec['targetTileBox'];req=json.loads((R/'prompts'/f'{name}.request.json').read_text(encoding='utf-8'));base=Path(req['sourceComposition'][0]['file']);oldim=Image.open(base).convert('RGB');newim=Image.open(native).convert('RGB')
assert box[3]<=4211
old=Image.open(req['references'][0]['file']).convert('RGB');oa=np.asarray(old,dtype=np.int16);na=np.asarray(newim,dtype=np.int16);cost=np.abs(oa-na).mean(axis=2).astype(np.float64)
def path(costs):
 h,w=costs.shape;dp=costs[0].copy();back=np.zeros((h,w),dtype=np.int8)
 for y in range(1,h):
  choices=np.stack([np.r_[np.inf,dp[:-1]]+0.35,dp,np.r_[dp[1:],np.inf]+0.35])
  move=np.argmin(choices,axis=0);back[y]=move-1;dp=costs[y]+np.min(choices,axis=0)
 p=np.empty(h,dtype=np.int32);p[-1]=np.argmin(dp)
 for y in range(h-1,0,-1):p[y-1]=p[y]+int(back[y,p[y]])
 return p
left=path(cost[:,20:300])+20;right=path(cost[:,954:1234])+954
top=path(cost[0:70,:].T);bottom=path(cost[1080:1254,:].T)+1080
if box[3]>4096:bottom[:]=1254
ys,xs=np.indices((1254,1254));mask=(xs>=left[:,None])&(xs<right[:,None])&(ys>=top[None,:])&(ys<bottom[None,:])
result=old.copy();runs=[]
for y in range(1254):
 changes=np.flatnonzero(np.diff(np.r_[False,mask[y],False].astype(np.int8)))
 for x0,x1 in zip(changes[::2],changes[1::2]):
  b=[int(x0),y,int(x1),y+1];result.paste(newim.crop(b),b[:2]);runs.append(b)
want=np.where(mask[:,:,None],na,oa).astype(np.uint8);assert np.array_equal(np.asarray(result),want)
out=oldim.copy();out.paste(result,box[:2])
q=R/'qa'/f'{name}-ownership';q.mkdir(exist_ok=True)
outpath=R/'tiles'/f'r11_c12.candidate-{name.split("r11_c12_")[1]}-ownership.png';assert not outpath.exists();out.save(outpath)
result.save(q/'actual-insert.png');Image.fromarray(mask.astype(np.uint8)).save(q/'source-id-local.png')
# Actual source-boundary strips include the full bounded seam search area.
out.crop((box[0]-70,box[1],box[0]+370,box[3])).save(q/'left-boundary.png')
out.crop((box[0]+884,box[1],box[2]+70,box[3])).save(q/'right-boundary.png')
out.crop((box[0],box[1]-70,box[2],box[1]+140)).save(q/'top-boundary.png')
if box[3]<=4096:out.crop((box[0],box[1]+1010,box[2],box[3]+70)).save(q/'bottom-boundary.png')
else:
 out.crop((box[0],3856,box[2],4096)).save(q/'bottom-boundary.png')
 result.crop((0,1024,1254,1254)).save(q/'native-bottom-halo.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
data={'candidate':str(outpath),'sha256':sha(outpath),'base':str(base),'baseSha256':sha(base),'native':str(native),'nativeSha256':sha(native),'targetTileBox':box,'sourceIdMap':str(q/'source-id-local.png'),'sourceIdMapSha256':sha(q/'source-id-local.png'),'sourceIdSemantics':{'0':'base at same world coordinate','1':'native at same world coordinate'},'nativeRowCropRuns':runs,'nativePixelCount':int(mask.sum()),'exactPixelReplayVerified':True,'operations':'Original-pixel mechanical crop/paste only; shortest-path merely selects ownership in same-coordinate source overlap. No colors changed, no blend/filter/resize.','formalAcceptedCount':0,'status':'pending_visual_boundary_review'}
(q/'source-replay.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in data.items() if k not in ['nativeRowCropRuns']}))

