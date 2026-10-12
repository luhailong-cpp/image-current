from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sample_assembly(ap,box):
 a=read(ap);bb=a['globalCoreBox'];ids=np.asarray(Image.open(a['sourceIdMap']['file']));h,w=box[3]-box[1],box[2]-box[0]
 yy,xx=np.mgrid[box[1]:box[3],box[0]:box[2]];cy=np.clip(yy-bb[1],0,ids.shape[0]-1);cx=np.clip(xx-bb[0],0,ids.shape[1]-1);chosen=ids[cy,cx]
 valid=(xx>=bb[0]-115)&(xx<bb[2]+115)&(yy>=bb[1]-115)&(yy<bb[3]+115);arr=np.zeros((h,w,3),np.uint8);covered=np.zeros((h,w),bool)
 for s in a['sources']:
  sid=s.get('sourceId',s.get('jointSourceId'));g=s['globalNativeBox'];m=valid&(chosen==sid)&(xx>=g[0])&(xx<g[2])&(yy>=g[1])&(yy<g[3])
  if not m.any():continue
  p=Path(s['file']);assert sha(p)==s['sha256'];im=np.asarray(Image.open(p).convert('RGB'));arr[m]=im[yy[m]-g[1],xx[m]-g[0]];covered|=m
 return arr,covered
tile,sr,sc,ver=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]);r,c=map(lambda q:int(q[1:]),tile.split('_'));x=(c-1)*4096+(sc-1)*1024;y=(r-1)*4096+(sr-1)*1024;core=[x,y,x+1024,y+1024];box=[x-115,y-115,x+1139,y+1139]
w=B/('work-'+tile)
for dd in ['guides','receipts','prompts','qa','tiles','selections']:(w/dd).mkdir(parents=True,exist_ok=True)
name=f'{tile}_s{sr:02d}_s{sc:02d}_v{ver:02d}';con=read(B.parent/'production-contract.json');ref=Path(con['layoutReference']);guide=np.asarray(Image.open(ref).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,tuple(z*1254/57344 for z in box),resample=Image.Resampling.BICUBIC)).copy();der=[]
idx=read(B/'current-artifacts.json')
for t in [f'r{r-1:02d}_c{c:02d}',f'r{r+1:02d}_c{c:02d}',f'r{r:02d}_c{c-1:02d}',f'r{r:02d}_c{c+1:02d}']:
 if t not in idx:continue
 ap=B/idx[t]['assembly'];a,m=sample_assembly(ap,box)
 if m.any():guide[m]=a[m];der.append({'assembly':str(ap),'sha256':sha(ap),'nativePixelsPasted':int(m.sum()),'method':'source-id lookup at global coordinates; only for halo ownership outside core use nearest edge source id; actual pixels remain native and unscaled'})
for rr,cc in [(sr,sc-1),(sr,sc+1),(sr-1,sc),(sr+1,sc)]:
 sp=w/'selections'/f's{rr:02d}_s{cc:02d}.json'
 if not sp.exists():continue
 s=read(sp);p=Path(s['file']);g=read(str(p)+'.generation.json')['globalNativeBox'];inter=[max(box[0],g[0]),max(box[1],g[1]),min(box[2],g[2]),min(box[3],g[3])]
 if inter[2]<=inter[0] or inter[3]<=inter[1]:continue
 dst=[inter[0]-box[0],inter[1]-box[1],inter[2]-box[0],inter[3]-box[1]];src=[inter[0]-g[0],inter[1]-g[1],inter[2]-g[0],inter[3]-g[1]];guide[dst[1]:dst[3],dst[0]:dst[2]]=np.asarray(Image.open(p).convert('RGB').crop(src));der.append({'file':str(p),'sha256':sha(p),'sourceCrop':src,'destinationBox':dst})
out=w/'guides'/(name+'.authoritative.png');Image.fromarray(guide).save(out);write(str(out)+'.derivation.json',{'file':str(out),'sha256':sha(out),'globalCoreBox':core,'globalNativeBox':box,'layout':str(ref),'layoutSha256':sha(ref),'neighbors':der,'role':'position-only blurred layout guide plus exact native neighbor pixels; never final pixels'})
write(w/'active-preparation.json',{'tile':tile,'ident':name,'guide':str(out),'globalCoreBox':core,'globalNativeBox':box,'neighbors':der});print(json.dumps({'ident':name,'guide':str(out),'globalCoreBox':core,'globalNativeBox':box,'neighbors':len(der)}))
