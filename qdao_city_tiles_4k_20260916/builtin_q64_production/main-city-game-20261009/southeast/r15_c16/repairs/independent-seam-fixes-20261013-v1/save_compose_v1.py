from pathlib import Path
import json,hashlib,shutil,datetime
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];S=T.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def write(p,o):
 p=Path(p);assert not p.exists(),p;p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(p,a):
 assert not p.exists();Image.fromarray(a).save(p);return ev(p)
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def path_dp(err):
 h,w=err.shape;score=err.copy().astype(np.float64);back=np.zeros((h,w),np.int16)
 for x in range(1,w):
  for y in range(h):
   ya=max(0,y-1);yb=min(h,y+2);q=ya+int(np.argmin(score[ya:yb,x-1]));score[y,x]+=score[q,x-1];back[y,x]=q
 path=np.empty(w,np.int16);path[-1]=np.argmin(score[:,-1])
 for x in range(w-1,0,-1):path[x-1]=back[path[x],x]
 return path
originals={'W01-west-capstone':'C:/Users/luyua/.codex/generated_images/01a1256f-f474-7161-a84b-6c353e51fc2f/exec-e4f2ee89-1d8e-466b-a9f7-5dcdd5957b36.png','I01-blind-stone-grout':'C:/Users/luyua/.codex/generated_images/01a1256f-f474-7161-a84b-6c353e51fc2f/exec-c8d0c63c-d902-496c-b584-875751db7988.png'}
receipts={}
for name,original in originals.items():
 out=D/name;prep=read(out/'preparation.json');im=Image.open(original)
 assert im.size==(1254,1254) and im.format=='PNG' and im.mode in ('RGB','RGBA')
 assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
 h=sha(original);dest=out/('actual-native-'+h[:16]+'.png');assert not dest.exists();shutil.copyfile(original,dest);assert sha(dest)==h
 receipt=dict(schemaVersion=1,status='success',tool='image_gen.imagegen',route='builtin',actualModel=None,actualQuality=None,modelEvidence='Builtin result returned image and original output path; no backend model/quality metadata',savedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),timeMeaning='Local preservation time only; generation completion timestamp not exposed',originalOutputPath=original,originalSha256=h,savedNative=ev(dest),width=1254,height=1254,format='PNG',mode=im.mode,preparation=ev(out/'preparation.json'),request=ev(out/'request.json'),prompt=ev(out/'prompt.txt'),references=prep['referenceImages'],resizedAfterGeneration=False,finalArtUpscaled=False,sourceObserved='Actual successful builtin call and displayed returned image in /root/assembly_support')
 write(out/'receipt.json',receipt);receipts[name]=receipt
 print(json.dumps(dict(saved=name,native=ev(dest))),flush=True)

latest=read(T/'candidate/latest-assembly.json');assert latest['candidate']['sha256']=='0cd62b74724ba75db14f8e4f0c6a80490bb71e410f4a8bb6529873176844ef81'
base=rgb(latest['candidate']['path']);ctxbase=rgb(latest['context']['path']);current=base.copy();union=np.zeros((4096,4096),bool)
assert np.array_equal(ctxbase[115:4211,115:4211],base)
trial=D/'trial-v1';trial.mkdir(exist_ok=False);steps=[]
for name in originals:
 out=D/name;prep=read(out/'preparation.json');native=rgb(receipts[name]['savedNative']['path']);nc=prep['sourceCrop'];box=prep['destinationCoreBox'];x0,y0,x1,y1=box
 cut=native[nc[1]:nc[3],nc[0]:nc[2]];old=current[y0:y1,x0:x1];hh,ww=old.shape[:2]
 err=np.mean((old.astype(np.float64)-cut.astype(np.float64))**2,axis=2)
 alpha=np.ones((hh,ww),np.float64);paths={}
 sides={'top':32,'bottom':16,'right':40} if name.startswith('W') else {'top':8,'bottom':8,'left':10,'right':5}
 fade=6 if name.startswith('W') else 3
 for side,width in sides.items():
  if side=='top':e=err[:width,:]
  elif side=='bottom':e=err[-width:,:][::-1]
  elif side=='left':e=err[:,:width].T
  else:e=err[:,-width:][:,::-1].T
  path=path_dp(e);paths[side]=path
  depth=np.arange(hh if side in ('top','bottom') else ww)[:,None]
  a=np.clip((depth-path[None,:])/fade,0,1)
  if side=='bottom':a=a[::-1]
  elif side=='left':a=a.T
  elif side=='right':a=a[::-1].T
  alpha=np.minimum(alpha,a)
 a=np.rint(alpha*255).astype(np.uint8)
 sd=trial/name;sd.mkdir();save(sd/'alpha-crop.png',a);np.savez_compressed(sd/'minimum-error-paths.npz',**paths)
 aa=a.astype(np.uint32)[...,None];before=current.copy();current[y0:y1,x0:x1]=((old.astype(np.uint32)*(255-aa)+cut.astype(np.uint32)*aa+127)//255).astype(np.uint8)
 replay=before.copy()
 for y in range(hh):
  for x in range(ww):
   av=int(a[y,x]);replay[y0+y,x0+x]=tuple((int(before[y0+y,x0+x,c])*(255-av)+int(cut[y,x,c])*av+127)//255 for c in range(3))
 assert np.array_equal(current,replay)
 support=np.zeros_like(union);support[y0:y1,x0:x1]=a>0;assert not np.any(support&union);union|=support
 assert np.array_equal(current[~support],before[~support]);assert np.array_equal(current[3712:],base[3712:])
 core=save(sd/'candidate-4096.png',current);ctx=ctxbase.copy();ctx[115:4211,115:4211]=current;context=save(sd/'context-4326.png',ctx)
 ox,oy=prep['contextOriginInCore']
 if ox<0:
  west=rgb(prep['pixelSources'][0]['source']['path']);local=np.concatenate((west[oy:oy+1254,4096+ox:4096],current[oy:oy+1254,:1254+ox]),axis=1)
 else:local=current[oy:oy+1254,ox:ox+1254]
 evidence=[]
 def qa(n,b):
  b=[max(0,b[0]),max(0,b[1]),min(1254,b[2]),min(1254,b[3])];e=save(sd/(n+'.png'),local[b[1]:b[3],b[0]:b[2]]);e.update(boxInTarget=b,scale='1:1');evidence.append(e)
 qa('composed-local-1254',[0,0,1254,1254]);qa('left-boundary-100pct',[nc[0]-96,nc[1]-48,nc[0]+96,nc[3]+48]);qa('right-boundary-100pct',[nc[2]-96,nc[1]-48,nc[2]+96,nc[3]+48]);qa('top-boundary-100pct',[nc[0]-64,nc[1]-64,nc[2]+64,nc[1]+64]);qa('bottom-boundary-100pct',[nc[0]-64,nc[3]-64,nc[2]+64,nc[3]+64])
 doc=dict(schemaVersion=1,id=name,status='trial_pending_visual_qa',published=False,formalAccepted=False,base=latest['candidate'],baseContext=latest['context'],actualNative=receipts[name]['savedNative'],receipt=ev(out/'receipt.json'),preparation=ev(out/'preparation.json'),nativeCrop=nc,destinationCoreBox=box,alpha=ev(sd/'alpha-crop.png'),minimumErrorPaths=ev(sd/'minimum-error-paths.npz'),seamWidths=sides,fadePixels=fade,blendArithmetic='(old*(255-alpha)+native*alpha+127)//255; RGB integers',RGBColorCorrection=False,resampling=False,independentScalarReplayExact=True,outsideMaskExact=True,south384PixelsExact=True,core=core,context=context,evidence=evidence)
 write(sd/'composition.json',doc);steps.append(ev(sd/'composition.json'))
assert np.array_equal(current[~union],base[~union])
write(trial/'trial-index.json',dict(base=latest['candidate'],steps=steps,finalCore=core,finalContext=context,outsideUnionExact=True,south384PixelsExact=True,formalAccepted=False,published=False))
print(json.dumps(dict(trial=ev(trial/'trial-index.json'),finalCore=core,finalContext=context)))
