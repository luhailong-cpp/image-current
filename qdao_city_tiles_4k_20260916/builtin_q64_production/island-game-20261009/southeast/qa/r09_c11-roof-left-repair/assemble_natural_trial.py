from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
R=Path(__file__).resolve().parents[2];Q=Path(__file__).resolve().parent
assert __import__('os').environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
p=json.loads((Q/'rect-trial-v01.json').read_text());b=Image.new('RGB',(8192,4096))
for i,o in enumerate(p['outputs']):b.paste(Image.open(o['base']).convert('RGB'),(4096*i,0))
U=np.asarray(Image.open(p['sources'][0]['file']).convert('RGB'));L=np.asarray(Image.open(p['sources'][1]['file']).convert('RGB'));B=np.asarray(b.crop((3300,0,4554,1854))).copy();C=B.copy();C[:737]=U[:737];C[737:]=L[137:]
def path(cost,start,end):
 # A coordinate path changes ONLY which original source owns a pixel.
 h,w=cost.shape;dp=cost[0].copy();back=np.zeros((h,w),np.int16)
 for y in range(1,h):
  candidates=[]
  for step in range(-4,5):
   z=np.full(w,np.inf);lo=max(0,-step);hi=min(w,w-step);z[lo:hi]=dp[lo+step:hi+step]+abs(step)*0.8;candidates.append(z)
  a=np.stack(candidates);pick=a.argmin(0);dp=cost[y]+a[pick,np.arange(w)];back[y]=pick-4
 out=np.empty(h,np.int16);out[-1]=dp.argmin()
 for y in range(h-1,0,-1):out[y-1]=out[y]+back[y,out[y]]
 return out+start
diff=np.abs(C.astype(float)-B.astype(float)).mean(2);brightness=(C.mean(2)+B.mean(2))/2
# Seek continuous shared dark gutter boundaries, not independent per-row best pixels.
leftcost=diff[:1600,:500]*2+brightness[:1600,:500]*.03
lp=path(leftcost,0,500)
rightcost=diff[:1600,950:1254]*2+brightness[:1600,950:1254]*.015
rp=path(rightcost,950,1254)
lp=np.r_[lp,np.repeat(lp[-1],254)];rp=np.r_[rp,np.repeat(rp[-1],254)]
def blue(a):
 a=a.astype(np.int16);return (a[:,:,2]>a[:,:,0]+25)&(a[:,:,2]>a[:,:,1]+15)&(a[:,:,2]>45)
bb=blue(C)|blue(B);bottom=1853-bb[::-1].argmax(0)+3;mask=np.arange(1854)[:,None]<=bottom[None,:]
mask&=(np.arange(1254)[None,:]>=lp[:,None])&(np.arange(1254)[None,:]<rp[:,None])
out=np.asarray(b).copy();out[:1854,3300:4554][mask]=C[mask];sid=np.zeros((4096,8192),np.uint8);reg=sid[:1854,3300:4554];reg[mask&(np.arange(1854)[:,None]<737)]=1;reg[mask&(np.arange(1854)[:,None]>=737)]=2
for i,o in enumerate(p['outputs']):
 f=Q/f"{o['tile']}-trial-natural-v01.png";Image.fromarray(out[:,i*4096:(i+1)*4096]).save(f);sf=Q/f"{o['tile']}-source-id-natural-v01.png";Image.fromarray(sid[:,i*4096:(i+1)*4096]).save(sf);o.update(file=str(f),sha256=sh(f),sourceID=str(sf),sourceIDSha256=sh(sf))
trial=Image.fromarray(out);ev=[]
for n,box in [('left-upper',[3200,0,3900,750]),('left-lower',[3200,750,3900,1650]),('right-upper',[4200,0,4650,750]),('right-lower',[4200,750,4650,1650]),('fixed-v14',[3072,768,4096,1280]),('upper-lower',[3300,609,4554,865]),('bottom-left',[3300,1150,3927,1650]),('bottom-right',[3927,1300,4554,1854]),('shared-upper',[3840,0,4352,1024]),('shared-lower',[3840,1024,4352,1854])]:
 f=Q/f'{n}-natural-v01.png';trial.crop(box).save(f);ev.append({'file':str(f),'sha256':sh(f),'canvasCrop':box})
north=Image.new('RGB',(458,512));north.paste(Image.open(R/'tiles/r08_c12.candidate-v15.png').crop((0,3840,458,4096)),(0,0));north.paste(trial.crop((4096,0,4554,256)),(0,256));north.save(Q/'north-r08-natural-v01.png')
Image.fromarray(mask.astype(np.uint8)*255).save(Q/'combined-native-mask-natural-v01.png');p.update(evidence=ev,leftPath=lp.tolist(),rightPath=rp.tolist(),maskFile=str(Q/'combined-native-mask-natural-v01.png'),status='pending_visual_natural_path');wr(Q/'natural-trial-v01.json',p);print('natural trial saved')

