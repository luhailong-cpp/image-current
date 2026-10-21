from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,a):p=Path(p);assert not p.exists(),p;p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=read(T/'candidate/native-repairs-20261013-v01/assembly.json');oldreview=read(T/'qa/native-repairs-20261013-v01/review.json')
rdir=T/'repair-batches/extra-curl-removal-01/trials/v01-binary-seam';r=read(rdir/'manifest.json')
out=np.array(Image.open(base['candidate']['file']).convert('RGB'));owner=np.array(Image.open(base['sourceIndex']['file']),dtype=np.uint16);mask=np.array(Image.open(r['mask']))>0;raw=np.array(Image.open(r['nativeSource']).convert('RGB'));x,y=r['tileOriginXY'];i=len(base['sources'])+1;out[y:y+1254,x:x+1254][mask]=raw[mask];owner[y:y+1254,x:x+1254][mask]=i
v=T/'candidate/native-repairs-20261013-v02';v.mkdir(exist_ok=False);q=T/'qa/native-repairs-20261013-v02';q.mkdir(exist_ok=False)
Image.fromarray(out).save(v/'candidate.png');Image.fromarray(owner).save(v/'source-index.png')
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
 assert not affected,n
 crops.append(dict(c,pixelIdenticalToV01ByMaskNonIntersection=True,reviewReusedByExactPixelIdentity=True))
record=dict(candidate=dict(file=str(v/'candidate.png'),sha256=sha(v/'candidate.png'),pixels=[4096,4096]),sourceIndex=dict(file=str(v/'source-index.png'),sha256=sha(v/'source-index.png')),sources=sources,proof=dict(status='passed_exact_same_world_native_pixels',provedPixels=16777216,bySource=proof),crops=crops,sourceResampled=False,sourceRecolored=False,feathered=False,interpolated=False,formalAccepted=False)
write(v/'assembly.json',record);review=dict(candidate=record['candidate'],crops=crops,passed=35,needsRepair=12,total=47,newLocalRepairReview=str(rdir/'producer-review.json'),reusedUnchangedCount=47,actuallyViewedChangedCount=0,reuseEvidence='New binary mask does not intersect any of the 47 existing native QA crops. Existing crop images and reviews unchanged.',formalAccepted=False);write(q/'review.json',review)
cp=read(T/'current-fullqa-checkpoint-20261013.json');write(T/'checkpoint-v01-before-curl-20261013.json',cp)
cp.update(updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate=record['candidate'],assembly=str(v/'assembly.json'),nativeSourceCount=20,nativeRepairVersionCount=len(list((T/'repair-batches').glob('*/generation.json'))),selectedRepairSourceCount=4,fullQA=str(q/'review.json'),qaPassed=35,qaNeedsRepair=12)
cp['localCompleted'].append('extra small gold curl removed with plain attachment')
cp['unpassed']=[z.replace('s04_03 eastern ridge step and curl','s04_03 eastern ridge step; curl removal completed') for z in cp['unpassed']];cp['deferredAfterTwoAttempts']=['roof x895 residual adjoining tile cut','beam face step x909/y2048','east row4 upper tile contour'];cp['continuation']='Material transitions and remaining east/middle/bottom contours are still unpassed. Do not export as accepted.'
(T/'current-fullqa-checkpoint-20261013.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(cp))
