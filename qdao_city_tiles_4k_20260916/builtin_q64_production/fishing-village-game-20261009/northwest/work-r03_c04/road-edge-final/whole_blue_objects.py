from pathlib import Path
from collections import defaultdict
import json,hashlib
import numpy as np
from PIL import Image,ImageFilter
W=Path(__file__).resolve().parent;B=W.parents[1]
rd=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:np.asarray(Image.open(p).convert('RGB')).copy()
base=B/'work-r03_c04/joint-south-resume/proposal-v1';m=rd(base/'joint-assembly.json');ar=next(x for x in m['artifacts'] if x['globalBox']==[12288,8192,16384,12288]);a=rgb(ar['file']);i=np.asarray(Image.open(ar['sourceIdMap']['file'])).copy()
oldm=rd(B/'work-r03_c04/tiles/r03_c04.assembly.json');old=rgb(B/'work-r03_c04/tiles/r03_c04.candidate.png');oid=np.asarray(Image.open(oldm['sourceIdMap']['file'] if Path(oldm['sourceIdMap']['file']).is_absolute() else B/oldm['sourceIdMap']['file']))
box=[14300,10700,16384,12288];x,y,x1,y1=[box[0]-12288,box[1]-8192,box[2]-12288,box[3]-8192];v=old[y:y1,x:x1].astype(np.int16)
q=(v[:,:,0]>140)&(v[:,:,2]-v[:,:,0]>8)&(v[:,:,2]-v[:,:,1]>3)
q=np.asarray(Image.fromarray((q*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3)))>0
parent=[];runs=[];last=[]
def find(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for yy,row in enumerate(q):
 edges=np.flatnonzero(np.diff(np.r_[False,row,False].astype(np.int8)));current=[];k=0
 for l,r in zip(edges[::2],edges[1::2]):
  idx=len(parent);parent.append(idx);runs.append((yy,int(l),int(r),idx));current.append((int(l),int(r),idx))
  while k<len(last) and last[k][1]<=l:k+=1
  z=k
  while z<len(last) and last[z][0]<r:
   p=find(last[z][2]);t=find(idx)
   if p!=t:parent[t]=p
   z+=1
 last=current
groups=defaultdict(list)
for yy,l,r,idx in runs:groups[find(idx)].append((yy,l,r))
mask=np.zeros(q.shape,bool);objects=[]
for rs in groups.values():
 count=sum(r-l for yy,l,r in rs)
 if count<7000:continue
 ymin=min(yy for yy,l,r in rs);ymax=max(yy for yy,l,r in rs);xmin=min(l for yy,l,r in rs);xmax=max(r for yy,l,r in rs)
 # Keep complete existing blue faces only; anything clipped by the formal southern edge is not a complete object.
 selected=ymax<q.shape[0]-5
 objects.append({'id':len(objects)+1,'pixels':count,'globalBox':[box[0]+xmin,box[1]+ymin,box[0]+xmax,box[1]+ymax+1],'selected':selected,'reason':'complete legacy blue face' if selected else 'touches formal south boundary; preserving would violate approved road contour'})
 if selected:
  # A face's row spans fill internal tiny mineral-highlight holes without inventing final pixels.
  rows=defaultdict(list)
  for yy,l,r in rs:rows[yy].append((l,r))
  for yy,segments in rows.items():mask[yy,min(l for l,r in segments):max(r for l,r in segments)]=True
maskimg=Image.fromarray((mask*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(23))
mask=np.asarray(maskimg.filter(ImageFilter.MaxFilter(19)).filter(ImageFilter.MinFilter(19)))>0
dest=a[y:y1,x:x1];dest[mask]=old[y:y1,x:x1][mask]
registry={str(Path(s['file']).resolve()).lower():s['sourceId'] for s in m['sources']}
for s in oldm['sources']:
 f=Path(s['file']);f=f if f.is_absolute() else B/f;sid=registry[str(f.resolve()).lower()];sel=mask&(oid[y:y1,x:x1]==s['sourceId']);i[y:y1,x:x1][sel]=sid
D=W/'complete-blue-objects-v3';D.mkdir(exist_ok=True)
Image.fromarray(a).save(D/'r03_c04.candidate.png');Image.fromarray(i).save(D/'r03_c04.source-id.png');Image.fromarray((mask*255).astype(np.uint8)).save(D/'selected-face-mask.png');Image.fromarray(a[3298:4096,2842:4096]).save(D/'road.100pct.png');Image.fromarray(a[2783:4096,2242:4096]).save(D/'full-area.100pct.png')
proof=[]
for s in m['sources']:
 yy,xx=np.nonzero(i==s['sourceId'])
 if not len(xx):continue
 vv=rgb(s['file']);sx=xx+12288-s['globalNativeBox'][0];sy=yy+8192-s['globalNativeBox'][1];assert np.array_equal(a[yy,xx],vv[sy,sx]);proof.append({'sourceId':s['sourceId'],'pixels':len(xx),'mismatches':0})
manifest={'candidate':{'file':str(D/'r03_c04.candidate.png'),'sha256':sha(D/'r03_c04.candidate.png')},'sourceIdMap':{'file':str(D/'r03_c04.source-id.png'),'sha256':sha(D/'r03_c04.source-id.png')},'sources':m['sources'],'baseAssembly':str(base/'joint-assembly.json'),'objects':objects,'sourceSelectionMask':{'file':str(D/'selected-face-mask.png'),'globalBox':box},'proof':{'pixels':16777216,'mismatches':0,'contributions':proof},'formalAccepted':False,'status':'whole-blue-object-selection-diagnostic'}
(D/'assembly.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(json.dumps({'objects':objects,'candidate':manifest['candidate']}))
