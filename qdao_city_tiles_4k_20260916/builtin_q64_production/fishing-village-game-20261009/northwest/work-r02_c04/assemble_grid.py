from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from production import B,W,read,write,sha,native,box
O=W/'assembly';O.mkdir(exist_ok=True)
N=4326
rgb=np.zeros((N,N,3),np.uint8);sid=np.zeros((N,N),np.uint16)
pa=read(W/'selected/s04s04-post-south.assembly.json');sources=list(pa['sources'])
files={Path(s['file']).resolve():s['sourceId'] for s in sources}
def register(p):
 p=Path(p).resolve()
 if p in files:return files[p]
 g=read(str(p)+'.generation.json');k=max(s['sourceId'] for s in sources)+1
 sources.append({'sourceId':k,'file':str(p),'sha256':sha(p),'globalNativeBox':g['globalNativeBox'],'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality')});files[p]=k;return k
def minpath(cost,step=2):
 h,w=cost.shape;prev=cost[:,0].copy();back=np.zeros((h,w),np.int8)
 for x in range(1,w):
  ar=np.stack([np.roll(prev,k) for k in range(-step,step+1)])
  for k in range(-step,step+1):
   if k<0:ar[k+step,k:]=1e12
   elif k>0:ar[k+step,:k]=1e12
  arg=ar.argmin(axis=0);back[:,x]=arg-step;prev=ar.min(axis=0)+cost[:,x]
 y=int(prev.argmin());p=np.zeros(w,int)
 for x in range(w-1,-1,-1):p[x]=y;y-=int(back[y,x])
 return p
def error(a,b):
 return np.abs(a.astype(float)-b.astype(float)).mean(axis=2)+.005
# Frozen south strip including our whole-post candidate.
ctx=np.asarray(Image.open(W/'guides/current-r03-north-context-post-candidate.png'))
ass=read(B/'delivery-2x2/stage-v3/r03_c04.assembly.json');base=np.asarray(Image.open(ass['sourceIdMap']['file']))
gy,gx=np.indices((230,4326));gx+=12173;gy+=8077
southids=base[np.clip(gy-8192,0,4095),np.clip(gx-12288,0,4095)]
southids[:,3072:]=np.asarray(Image.open(W/'selected/s04s04-post-south.source-id.png'))[1024:1254]
rgb[4096:]=ctx[:230];sid[4096:]=southids
# Recorded explicit western peer natives.
for r in range(1,5):
 p=B/'work-r02_c03/native'/f'r02_c03_s{r:02d}_s04_v01.png'
 if p.exists():
  y=(r-1)*1024;im=np.asarray(Image.open(p).convert('RGB'));rgb[y:y+1254,:230]=im[:,1024:];sid[y:y+1254,:230]=register(p)
log=[]
for r in [4,3,2,1]:
 for c in [4,3,2,1]:
  p=native(r,c)
  if p is None:continue
  a=np.asarray(Image.open(p).convert('RGB'));y=(r-1)*1024;x=(c-1)*1024;old=rgb[y:y+1254,x:x+1254];oi=sid[y:y+1254,x:x+1254]
  if r==4 and c==4:
   ni=np.asarray(Image.open(W/'selected/r02_c04_s04_s04_v01.source-id.png'))
  else:
   der=Path(str(p)+'.derivation.json')
   original=read(der).get('nativeSource',str(p)) if der.exists() else str(p)
   ni=np.full((1254,1254),register(original),np.uint16)
  mask=np.ones((1254,1254),bool)
  # horizontal seam inside the full 230-px native overlap.
  if np.all(oi[1024:]>0):
   cost=error(a[1024:],old[1024:]);cost[:10]+=1e5;cost[-10:]+=1e5
   curve=minpath(cost);mask[1024:]=np.arange(230)[:,None]<=curve
  if np.all(oi[:,1024:]>0):
   cost=error(a[:,1024:],old[:,1024:]).T;cost[:10]+=1e5;cost[-10:]+=1e5
   curve=minpath(cost);mask[:,1024:]&=np.arange(230)[None,:]<=curve[:,None]
  if c==1 and np.all(oi[:,:230]>0):
   cost=error(a[:,:230],old[:,:230]).T;cost[:10]+=1e5;cost[-10:]+=1e5
   curve=minpath(cost);mask[:,:230]&=np.arange(230)[None,:]>=curve[:,None]
  old[mask]=a[mask];oi[mask]=ni[mask]
  log.append({'row':r,'column':c,'candidate':str(p),'sha256':sha(p),'pastedPixelCount':int(mask.sum())})
core=rgb[115:4211,115:4211];ids=sid[115:4211,115:4211];valid=ids>0
Image.fromarray(core).save(O/'r02_c04.candidate.png');Image.fromarray(ids).save(O/'r02_c04.source-id.png')
Image.fromarray(rgb).save(O/'r02_c04.with-halo.png');Image.fromarray(sid).save(O/'r02_c04.with-halo.source-id.png')
Image.fromarray(core).resize((1024,1024),Image.Resampling.LANCZOS).save(W/'qa/r02_c04.preview-only.png')
used=set(np.unique(ids).tolist());used.discard(0)
sources=[s for s in sources if s['sourceId'] in used or s['sourceId'] in np.unique(sid)]
m={'file':str(O/'r02_c04.candidate.png'),'sha256':sha(O/'r02_c04.candidate.png'),'globalCoreBox':[12288,4096,16384,8192],'sourceIdMap':{'file':str(O/'r02_c04.source-id.png'),'sha256':sha(O/'r02_c04.source-id.png')},'sources':sources,'coveragePixels':int(valid.sum()),'totalPixels':4096**2,'completeNativeCells':len(log),'sourceOrder':log,'pixelMethod':'exact native unscaled hard seam selection, no color blending or resampling','formalAccepted':False,'status':'candidate-pending-100-percent-internal-and-boundary-qa'}
write(O/'r02_c04.assembly.json',m)
for axis in ['v','h']:
 for k in [1,2,3]:
  for z in [0,1,2,3]:
   b=(k*1024-220,z*1024,k*1024+220,(z+1)*1024) if axis=='v' else (z*1024,k*1024-220,(z+1)*1024,k*1024+220)
   Image.fromarray(core).crop(b).save(W/'qa'/f'internal-{axis}{k}-part{z+1}.100pct.png')
print(json.dumps({'cells':len(log),'covered':int(valid.sum()),'sourceCount':len(sources),'assembly':str(O/'r02_c04.assembly.json')}))

