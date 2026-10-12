from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;B='r06_c03-candidate-hard-b0c8f7b8ec2f'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,a):p=Path(p);assert not p.exists(),p;p.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
b=read(T/'candidate'/(B+'.assembly.json'));v=T/'candidate/native-repairs-20261013-v01';v.mkdir(exist_ok=False)
out=np.array(Image.open(b['output']['file']).convert('RGB'));owner=np.zeros((4096,4096),np.uint16);sources=[]
for i,s in enumerate(b['nativeSources'],1):
 x,y=s['tileCorePasteXY'];owner[y:y+1024,x:x+1024]=i;sources.append(dict(id=i,file=s['file'],sha256=s['sha256'],tileOriginXY=[x-115,y-115],generationRecord=s['generationRecord']['file'],role='selected_core'))
repairs=['circular-anchor-02/trials/v03-binary-seam','roof-truncation-02/trials/v02-binary-seam','fascia-truncation-02/trials/v02-binary-seam']
for rel in repairs:
 q=T/'repair-batches'/rel;m=read(q/'manifest.json');mask=np.array(Image.open(m['mask']))>0;native=np.array(Image.open(m['nativeSource']).convert('RGB'));x,y=m['tileOriginXY'];a=out[y:y+1254,x:x+1254];o=owner[y:y+1254,x:x+1254];i=len(sources)+1;a[mask]=native[mask];o[mask]=i
 sources.append(dict(id=i,file=m['nativeSource'],sha256=m['nativeSha256'],tileOriginXY=[x,y],generationRecord=str(q.parent.parent/'generation.json'),selectionManifest=str(q/'manifest.json'),selectionMask=m['mask'],selectionMaskSha256=m['maskSha256'],review=str(q/'independent-review.json') if (q/'independent-review.json').exists() else str(q/'producer-review.json'),role='native_local_repair'))
Image.fromarray(out).save(v/'candidate.png');Image.fromarray(owner).save(v/'source-index.png')
proof=[]
for s in sources:
 assert sha(s['file'])==s['sha256'];raw=np.array(Image.open(s['file']).convert('RGB'));yy,xx=np.where(owner==s['id']);ox,oy=s['tileOriginXY'];assert np.all((xx-ox>=0)&(xx-ox<1254)&(yy-oy>=0)&(yy-oy<1254));assert np.array_equal(out[yy,xx],raw[yy-oy,xx-ox]);proof.append(dict(id=s['id'],pixels=int(len(xx)),nativePixelsEqual=True))
assert sum(x['pixels'] for x in proof)==4096*4096
q=T/'qa/native-repairs-20261013-v01';q.mkdir(exist_ok=False)
old=read(T/'qa'/(B+'.reused-source-review.json'));prior={Path(x['file']).name:x for x in old['crops']}
for x in read(T/'qa'/(B+'.pending-independent-review-20261013.json'))['crops']:prior[Path(x['file']).name]['status']=x['verdict']
im=Image.fromarray(out);crops=[]
ext=read(T/'qa'/(B+'.actual-final-neighbors')/'manifest.json');N=Image.new('RGB',(4096,320));N.paste(Image.open(ext['north']['file']).crop((0,3936,4096,4096)),(0,0));N.paste(im.crop((0,0,4096,160)),(0,160));E=Image.new('RGB',(320,4096));E.paste(im.crop((3936,0,4096,4096)),(0,0));E.paste(Image.open(ext['east']['file']).crop((0,0,160,4096)),(160,0))
for item in b['qa']+ext['crops']:
 name=Path(item['file']).name
 if name.startswith('north-'):pic=N.crop(item['cropLTRB'])
 elif name.startswith('east-'):pic=E.crop(item['cropLTRB'])
 else:
  pic=im.crop(item['cropLTRB'])
  if item.get('rotationCCW90'):pic=pic.transpose(Image.Transpose.ROTATE_90)
 unchanged=np.array_equal(np.array(pic),np.array(Image.open(item['file']).convert('RGB')))
 if unchanged:path=Path(item['file'])
 else:path=q/name;pic.save(path)
 crops.append(dict(file=str(path),sha256=sha(path),nativePixelScale=1,sourceResampled=False,priorFile=item['file'],priorSha256=item['sha256'],pixelIdenticalToPrior=unchanged,status=prior[name]['status'] if unchanged else 'pending_changed',cropLTRB=item['cropLTRB'],rotationCCW90=item.get('rotationCCW90',False)))
record=dict(candidate=dict(file=str(v/'candidate.png'),sha256=sha(v/'candidate.png'),pixels=[4096,4096]),sourceIndex=dict(file=str(v/'source-index.png'),sha256=sha(v/'source-index.png')),sources=sources,proof=dict(status='passed_exact_same_world_native_pixels',provedPixels=16777216,bySource=proof),crops=crops,sourceResampled=False,sourceRecolored=False,feathered=False,interpolated=False,formalAccepted=False)
write(v/'assembly.json',record);write(q/'manifest.json',record)
print(json.dumps(dict(candidate=record['candidate'],sources=len(sources),provedPixels=16777216,unchanged=sum(x['pixelIdenticalToPrior'] for x in crops),changed=[Path(x['file']).name for x in crops if not x['pixelIdenticalToPrior']])))
