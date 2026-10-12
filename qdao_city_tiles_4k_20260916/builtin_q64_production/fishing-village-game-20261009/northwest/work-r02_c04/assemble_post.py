from pathlib import Path
from PIL import Image,ImageFilter
from collections import deque
import numpy as np,json,hashlib
from production import B,W,read,write,sha,box
def path(cost,lo,hi,step=4):
 h,w=cost.shape; yy=np.arange(h);prev=np.where((yy>=lo[0])&(yy<=hi[0]),cost[:,0],1e15);backs=np.zeros((h,w),np.int16)
 for x in range(1,w):
  v=np.stack([np.roll(prev,k) for k in range(-step,step+1)])
  for k in range(-step,step+1):
   if k<0:v[k+step,k:]=1e15
   elif k>0:v[k+step,:k]=1e15
  z=np.argmin(v,axis=0);p=np.min(v,axis=0)+cost[:,x];p[(yy<lo[x])|(yy>hi[x])]=1e15;backs[:,x]=z-step;prev=p
 y=int(np.argmin(prev));assert prev[y]<1e14;line=np.empty(w,int)
 for x in range(w-1,-1,-1):line[x]=y;y-=int(backs[y,x])
 return line
old=np.asarray(Image.open(W/'guides/south-same-column-native-context.png').convert('RGB'))
top=np.asarray(Image.open(W/'native/r02_c04_s04_s04_v01.png').convert('RGB'))
new=np.asarray(Image.open(W/'native/r02_c04_r03_c04_fence_post_whole_bridge_v01.png').convert('RGB'))
a=new.astype(float); b=np.zeros_like(a);b[624:]=old[:630]
wood=lambda p:((p[:,:,0]>p[:,:,1]+24)&(p[:,:,1]>p[:,:,2]+15)&(p[:,:,0]>85))
gray=lambda p:((p[:,:,2]>p[:,:,0]*.85)&(p[:,:,1]>p[:,:,0]*.90)&(p.min(axis=2)>110))
def wood_object(p,seeds):
 raw=wood(p); dil=np.asarray(Image.fromarray(raw.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(7)))>0
 seen=np.zeros(raw.shape,bool);q=deque(seeds)
 while q:
  y,x=q.popleft()
  if y<0 or y>=1254 or x<0 or x>=1254 or seen[y,x] or not dil[y,x]:continue
  seen[y,x]=True;q.extend([(y-1,x),(y+1,x),(y,x-1),(y,x+1)])
 return seen&raw
woods=wood_object(a,[(500,670),(900,670)])|wood_object(b,[(800,680),(1100,680)]);woods[:739]=False
paves=(gray(a)|gray(b));paves[:739]=False
ys=np.arange(1254)[:,None]
lo=np.maximum(755,np.max(np.where(woods,ys,-1),axis=0)+8)
hi=np.minimum(1253,np.min(np.where(paves,ys,9999),axis=0)-8)
# A few foliage highlights are not pavement. Keep a generous final native margin.
bad=lo>hi
hi[bad]=1253
lo=np.minimum(lo,1253)
cost=np.mean(np.abs(a-b),axis=2)+4
cost[:739]=1e7
lower=path(cost,lo,hi,5)
costtop=np.mean(np.abs(a[:120]-top[400:520].astype(float)),axis=2)
upper=path(costtop,np.zeros(1254,int),np.full(1254,75),3)
m=(ys>=upper[None,:])&(ys<=lower[None,:])
out=np.zeros((2278,1254,3),np.uint8);out[:1254]=top;out[1024:]=old
src=np.zeros((2278,1254),np.uint16)
ap=B/'delivery-2x2/stage-v3/r03_c04.assembly.json';ass=read(ap);sid=np.asarray(Image.open(ass['sourceIdMap']['file']))
sources=ass['sources'];n=max(s['sourceId'] for s in sources)+1
src[:1254]=n
gy,gx=np.indices((1254,1254));gx+=15245;gy+=8077
src[1024:]=sid[np.clip(gy-8192,0,4095),np.clip(gx-12288,0,4095)]
out[400:1654][m]=new[m];src[400:1654][m]=n+1
for id,p in [(n,W/'native/r02_c04_s04_s04_v01.png'),(n+1,W/'native/r02_c04_r03_c04_fence_post_whole_bridge_v01.png')]:
 g=read(str(p)+'.generation.json');sources.append({'sourceId':id,'file':str(p),'sha256':sha(p),'globalNativeBox':g['globalNativeBox'],'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'actualModel':None,'actualQuality':None})
d=W/'selected';d.mkdir(exist_ok=True)
Image.fromarray(out).save(d/'s04s04-post-south.context.png');Image.fromarray(src).save(d/'s04s04-post-south.source-id.png')
Image.fromarray(out[:1254]).save(d/'r02_c04_s04_s04_v01.png');Image.fromarray(src[:1254]).save(d/'r02_c04_s04_s04_v01.source-id.png')
Image.fromarray(m.astype(np.uint8)*255).save(d/'whole-post.mask.png')
write(d/'s04s04-post-south.assembly.json',{'globalBox':[15245,7053,16499,9331],'file':str(d/'s04s04-post-south.context.png'),'sourceIdMap':str(d/'s04s04-post-south.source-id.png'),'sources':sources,'baseAssembly':str(ap),'hardMask':str(d/'whole-post.mask.png'),'nativeResampled':False,'status':'candidate-pending-100pct-visual-qa'})
Image.fromarray(out[850:1850]).save(W/'qa/s04s04-post-seam.100pct.png')
Image.fromarray(out[320:600]).save(W/'qa/s04s04-post-upper.100pct.png')
Image.fromarray(out[1200:1800]).save(W/'qa/s04s04-post-foot.100pct.png')
print(json.dumps({'minLower':int(lower.min()),'maxLower':int(lower.max()),'newSourceId':n+1,'woodConstraintsBad':int(bad.sum())}))

