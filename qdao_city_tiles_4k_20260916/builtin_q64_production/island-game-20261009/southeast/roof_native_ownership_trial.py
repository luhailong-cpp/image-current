from workflow import *
from PIL import Image
import numpy as np
folder=ROOT/'qa/roof-surface-ownership';folder.mkdir(exist_ok=True)
left0=Image.open(ROOT/'tiles/r09_c11.candidate.png').convert('RGB');right0=Image.open(ROOT/'tiles/r09_c12.candidate-v03.png').convert('RGB')
old=Image.new('RGB',(3072,1254));old.paste(left0.crop([3814,0,4096,1254]),(0,0));old.paste(right0.crop([0,0,2790,1254]),(282,0))
new=Image.new('RGB',(3072,1254))
for j,letter in enumerate('abc'):new.paste(Image.open(ROOT/'native'/f'r09_c12_roof_surface_{letter}_v01.png').convert('RGB').crop([115,0,1139,1254]),(1024*j,0))
oldA=np.asarray(old,dtype=np.float32);newA=np.asarray(new,dtype=np.float32);lo,hi=800,1254
cost=np.mean((oldA[lo:hi]-newA[lo:hi])**2,axis=2)+0.12*np.mean(newA[lo:hi]**2,axis=2)
h,w=cost.shape;dp=cost[:,0].copy();back=np.zeros((h,w),dtype=np.int8)
for x in range(1,w):
 options=[]
 for step in [-2,-1,0,1,2]:
  v=np.full(h,np.inf,dtype=np.float32)
  if step<0:v[:step]=dp[-step:]
  elif step>0:v[step:]=dp[:-step]
  else:v=dp.copy()
  options.append(v+abs(step)*2)
 stack=np.stack(options);idx=np.argmin(stack,axis=0);dp=cost[:,x]+stack[idx,np.arange(h)];back[:,x]=idx-2
path=np.zeros(w,dtype=np.int32);y=int(np.argmin(dp));path[-1]=y+lo
for x in range(w-1,0,-1):y-=int(back[y,x]);path[x-1]=y+lo
# each column remains an exact unscaled source rectangle; no output value is synthesized
q=old.copy()
for x,y in enumerate(path):q.paste(new.crop([x,0,x+1,int(y)+1]),(x,0))
testL=left0.copy();testR=right0.copy();testL.paste(q.crop([0,0,282,1254]),(3814,0));testR.paste(q.crop([282,0,3072,1254]),(0,0));testR.paste(Image.open(ROOT/'native/r09_c12_roof_surface_d_v01.png').convert('RGB'),(1651,742))
testR.resize((1024,1024),Image.Resampling.LANCZOS).save(folder/'preview.png');testL.save(folder/'r09_c11-trial.png');testR.save(folder/'r09_c12-trial.png')
for i,x in enumerate([0,742,1200]):testR.crop([x,750,x+1024,1400]).save(folder/f'boundary-{i}.png')
write(folder/'path.json',{'type':'minimum-error hard native pixel ownership, no new pixel colors, no resampling/alpha/warp/painting','globalXRelativeR09c12Start':-282,'ySearchRange':[lo,hi],'path':path.tolist(),'range':[int(path.min()),int(path.max())],'meanBoundaryRGBError':float(np.mean(np.abs(oldA[path,np.arange(w)]-newA[path,np.arange(w)]))),'status':'trial_pending_visual_review','nativeInputs':[{'file':str(ROOT/'native'/f'r09_c12_roof_surface_{letter}_v01.png'),'sha256':sha(ROOT/'native'/f'r09_c12_roof_surface_{letter}_v01.png')} for letter in 'abc']})
print('path range',int(path.min()),int(path.max()))

