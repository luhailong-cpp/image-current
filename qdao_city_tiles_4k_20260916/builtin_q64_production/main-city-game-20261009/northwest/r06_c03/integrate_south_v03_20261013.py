from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,a):p=Path(p);assert not p.exists(),p;p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=read(T/'candidate/native-repairs-20261013-v02/assembly.json');oldreview=read(T/'qa/native-repairs-20261013-v02/review-reopened-upstream-20261013.json');rdir=T/'repair-batches/south-ridge-step-01/trials/v01-binary-seam';r=read(rdir/'manifest.json')
out=np.array(Image.open(base['candidate']['file']).convert('RGB'));owner=np.array(Image.open(base['sourceIndex']['file']),dtype=np.uint16);mask=np.array(Image.open(r['mask']))>0;raw=np.array(Image.open(r['nativeSource']).convert('RGB'));x,y=r['tileOriginXY'];i=len(base['sources'])+1;out[y:y+1254,x:x+1254][mask]=raw[mask];owner[y:y+1254,x:x+1254][mask]=i
v=T/'candidate/native-repairs-20261013-v03';v.mkdir(exist_ok=False);q=T/'qa/native-repairs-20261013-v03';q.mkdir(exist_ok=False);Image.fromarray(out).save(v/'candidate.png');Image.fromarray(owner).save(v/'source-index.png')
sources=base['sources']+[dict(id=i,file=r['nativeSource'],sha256=r['nativeSha256'],tileOriginXY=[x,y],generationRecord=str(rdir.parent.parent/'generation.json'),selectionManifest=str(rdir/'manifest.json'),selectionMask=r['mask'],selectionMaskSha256=r['maskSha256'],review=str(rdir/'producer-review.json'),role='native_local_repair')]
proof=[]
for s in sources:
 assert sha(s['file'])==s['sha256'];native=np.array(Image.open(s['file']).convert('RGB'));yy,xx=np.where(owner==s['id']);ox,oy=s['tileOriginXY'];assert np.all((xx-ox>=0)&(xx-ox<1254)&(yy-oy>=0)&(yy-oy<1254));assert np.array_equal(out[yy,xx],native[yy-oy,xx-ox]);proof.append(dict(id=s['id'],pixels=int(len(xx)),nativePixelsEqual=True))
assert sum(z['pixels'] for z in proof)==16777216
changed=[];crops=[];fullmask=np.zeros((4096,4096),bool);fullmask[y:y+1254,x:x+1254]=mask
for c in oldreview['crops']:
 n=Path(c['file']).name
 if n.startswith('north-'):affected=fullmask[:160,:].any()
 elif n.startswith('east-'):affected=fullmask[:,3936:].any()
 else:
  a,b,cc,d=c['cropLTRB'];affected=fullmask[b:d,a:cc].any()
 if affected:
  assert not n.startswith(('north-','east-'));pic=Image.fromarray(out).crop(c['cropLTRB'])
  if c.get('rotationCCW90'):pic=pic.transpose(Image.Transpose.ROTATE_90)
  path=q/n;pic.save(path);crops.append(dict(c,file=str(path),sha256=sha(path),pixelIdenticalToPrior=False,reviewReusedByExactPixelIdentity=False,status='pending_changed',actuallyViewed=False));changed.append(n)
 else:crops.append(dict(c,pixelIdenticalToV02ByMaskNonIntersection=True,reviewReusedByExactPixelIdentity=True))
record=dict(candidate=dict(file=str(v/'candidate.png'),sha256=sha(v/'candidate.png'),pixels=[4096,4096]),sourceIndex=dict(file=str(v/'source-index.png'),sha256=sha(v/'source-index.png')),sources=sources,proof=dict(status='passed_exact_same_world_native_pixels',provedPixels=16777216,bySource=proof),crops=crops,sourceResampled=False,sourceRecolored=False,feathered=False,interpolated=False,formalAccepted=False)
write(v/'assembly.json',record);write(q/'manifest.json',record)
print(json.dumps(dict(candidate=record['candidate'],changed=changed,sources=len(sources),proofPixels=16777216)))
