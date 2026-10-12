"""Match generated repair edge colors to unchanged same-coordinate surroundings.
Only a bounded, low-frequency RGB correction field is interpolated. Geometry and
all native pixel coordinates remain unchanged; no image blending or resampling.
"""
from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
selpath=T/'canopy-edge-v1-selected.json';sel=read(selpath)
OUT=T/'processed/joint-edge-color-v1';OUT.mkdir(parents=True,exist_ok=True)
jobs=[('bench-rim-joint-v1',[31117,39821,32371,41075]),('canopy-edge-joint-v1',[31683,38785,32183,39045])]
fields=[]
for stem,adopt in jobs:
 req=read(T/'repairs'/f'{stem}.request.json');box=req['coordinate']['globalBox']
 bp=Path(req['referenced_image_paths'][0]);jp=T/'repairs'/f'{stem}.png'
 crop=[adopt[0]-box[0],adopt[1]-box[1],adopt[2]-box[0],adopt[3]-box[1]]
 aa=np.asarray(Image.open(bp).crop(crop).convert('RGB'),dtype=np.float32)
 bb=np.asarray(Image.open(jp).crop(crop).convert('RGB'),dtype=np.float32)
 h,w=aa.shape[:2]
 def profile(a,b,vertical):
  diff=a-b
  grad=lambda x:np.maximum(np.max(np.abs(np.gradient(x,axis=0)),axis=2),np.max(np.abs(np.gradient(x,axis=1)),axis=2))
  mask=(grad(a)<6)&(grad(b)<6)&(np.max(np.abs(diff),axis=2)<50)
  if not vertical:diff=diff.swapaxes(0,1);mask=mask.T
  n=len(diff);raw=np.zeros((n,3),np.float32);valid=mask.sum(axis=1)>=4
  for i in np.flatnonzero(valid):raw[i]=np.median(diff[i][mask[i]],axis=0)
  kernel=np.exp(-.5*(np.arange(-72,73)/24)**2);kernel/=kernel.sum()
  den=np.convolve(np.pad(valid.astype(float),(72,72),mode='edge'),kernel,mode='valid')
  num=np.stack([np.convolve(np.pad(raw[:,c]*valid,(72,72),mode='edge'),kernel,mode='valid') for c in range(3)],axis=1)
  out=num/np.maximum(den[:,None],1e-8);out[den<.15]=0
  return np.clip(out,-24,24)
 curves={'left':profile(aa[:,:24],bb[:,:24],True),'right':profile(aa[:,-24:],bb[:,-24:],True),'top':profile(aa[:24],bb[:24],False),'bottom':profile(aa[-24:],bb[-24:],False)}
 gx=np.linspace(0,w-1,int(np.ceil((w-1)/16))+1);gy=np.linspace(0,h-1,int(np.ceil((h-1)/16))+1)
 field=np.zeros((len(gy),len(gx),3),np.float32);fixed=np.zeros(field.shape[:2],bool)
 for side,p in curves.items():
  axis=gy if side in ('left','right') else gx
  q=np.stack([np.interp(axis,np.arange(len(p)),p[:,c]) for c in range(3)],axis=1)
  if side=='left':field[:,0]=q;fixed[:,0]=True
  if side=='right':field[:,-1]=q;fixed[:,-1]=True
  if side=='top':field[0]=q;fixed[0]=True
  if side=='bottom':field[-1]=q;fixed[-1]=True
 # Reconcile corner values, then solve a bounded harmonic extension.
 for iy,ix,v,hp in [(0,0,'left','top'),(0,-1,'right','top'),(-1,0,'left','bottom'),(-1,-1,'right','bottom')]:
  field[iy,ix]=(curves[v][iy]+curves[hp][ix])/2
 yy,xx=np.meshgrid(gy,gx,indexing='ij');fixed|=np.minimum.reduce([xx,w-1-xx,yy,h-1-yy])>=256
 iy,ix=np.indices(fixed.shape);masks=[(~fixed)&((iy+ix)%2==p) for p in (0,1)]
 for iteration in range(4000):
  old=field.copy()
  for mask in masks:
   total=np.zeros_like(field);total[1:]+=field[:-1];total[:-1]+=field[1:];total[:,1:]+=field[:,:-1];total[:,:-1]+=field[:,1:]
   field[mask]+=1.8*(total[mask]/4-field[mask])
  if np.max(np.abs(field-old))<.00002:break
 else:raise RuntimeError('Field convergence failed')
 horiz=np.stack([np.stack([np.interp(np.arange(w),gx,row[:,c]) for c in range(3)],axis=1) for row in field])
 full=np.stack([np.stack([np.interp(np.arange(h),gy,horiz[:,x,c]) for c in range(3)],axis=1) for x in range(w)],axis=1).astype(np.float32)
 assert np.abs(full).max()<=24.0001
 fp=OUT/f'{stem}-edge-color-field.npz';np.savez_compressed(fp,additiveRgb=full,gridRgb=field,gridX=gx,gridY=gy)
 fields.append({'stem':stem,'globalBox':adopt,'path':str(fp),'sha256':sha(fp),'input':str(bp),'inputSha256':sha(bp),'generated':str(jp),'generatedSha256':sha(jp),'maximumCorrection':float(np.abs(full).max()),'field':full})
for pid,rel in list(sel['patches'].items()):
 r,c=int(pid[1])-1,int(pid[2])-1;nx,ny=28672+c*1024-115,36864+r*1024-115
 base=T/rel;arr=np.asarray(Image.open(base).convert('RGB'),dtype=np.float32);delta=np.zeros_like(arr);uses=[]
 for rec in fields:
  b=rec['globalBox'];inter=[max(nx,b[0]),max(ny,b[1]),min(nx+1254,b[2]),min(ny+1254,b[3])]
  if inter[0]>=inter[2] or inter[1]>=inter[3]:continue
  x,y,x1,y1=inter;delta[y-ny:y1-ny,x-nx:x1-nx]=rec['field'][y-b[1]:y1-b[1],x-b[0]:x1-b[0]]
  uses.append({k:v for k,v in rec.items() if k!='field'})
 if not uses:continue
 out=OUT/f'{pid}-joint-edge-color.png';result=np.uint8(np.clip(np.rint(arr+delta),0,255));Image.fromarray(result).save(out)
 write(out.with_suffix('.png.derivation.json'),{'file':str(out),'sha256':sha(out),'base':str(base),'baseSha256':sha(base),'operation':'bounded additive low-frequency color field; unchanged pixel coordinates','fields':uses,'maxActualChannelDelta':int(np.abs(result.astype(float)-arr).max()),'resamplingApplied':False,'blurApplied':False,'pixelBlendingApplied':False,'script':str(Path(__file__)),'scriptSha256':sha(__file__)})
 sel['patches'][pid]=str(out.relative_to(T))
canvas=Image.new('RGB',(4096,4096))
for pid,rel in sel['patches'].items():
 canvas.paste(Image.open(T/rel).crop((115,115,1139,1139)),((int(pid[2])-1)*1024,(int(pid[1])-1)*1024))
cp=OUT/'candidate-4096.png';canvas.save(cp);canvas.resize((1024,1024),Image.Resampling.LANCZOS).save(OUT/'preview-QA-1024.png')
sel['candidate']=str(cp);sel['status']='color_candidate_pending_QA';write(T/'joint-edge-color-v1-selected.json',sel)
write(OUT/'report.json',{'selectionSource':str(selpath),'selectionSourceSha256':sha(selpath),'fields':[{k:v for k,v in f.items() if k!='field'} for f in fields],'candidate':str(cp),'candidateSha256':sha(cp),'maxCorrection':max(f['maximumCorrection'] for f in fields),'resamplingApplied':False,'geometryAcceptanceClaimed':False})
print(json.dumps({'candidate':str(cp),'maxCorrection':max(f['maximumCorrection'] for f in fields)}))
