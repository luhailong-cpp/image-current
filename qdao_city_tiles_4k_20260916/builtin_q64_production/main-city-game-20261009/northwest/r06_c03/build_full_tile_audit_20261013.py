from pathlib import Path
import json,importlib.util,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('p',T.parent/'production_v2.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
name='r06_c03-candidate-hard-b0c8f7b8ec2f'
m=p.read(T/'candidate'/(name+'.assembly.json'));q=T/'qa'/(name+'.actual-final-neighbors');q.mkdir(exist_ok=False)
im=Image.open(m['output']['file']).convert('RGB');north=T.parent/'r05_c03/candidate/r05_c03-candidate-hard-80982c249bee.png';east=T.parent/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/tiles/r06_c04-joint-4096.png'
assert p.sha(north)=='8705aba979d280b2e3e90767b54882b8d867027f1242de4a452a214db0a61053'
assert p.sha(east)=='493e896f75ebe6188bc83d8359af92267ec9084132ad5631392b5a074e097282'
N=Image.new('RGB',(4096,320));N.paste(Image.open(north).crop((0,3936,4096,4096)),(0,0));N.paste(im.crop((0,0,4096,160)),(0,160))
E=Image.new('RGB',(320,4096));E.paste(im.crop((3936,0,4096,4096)),(0,0));E.paste(Image.open(east).crop((0,0,160,4096)),(160,0))
ext=[]
for side,img in [('north',N),('east',E)]:
 for i in range(4):
  box=[i*1024,0,(i+1)*1024,320] if side=='north' else [0,i*1024,320,(i+1)*1024]
  path=q/f'{side}-segment{i+1:02d}.png';p.save_png(path,img.crop(box));ext.append(dict(file=str(path),sha256=p.sha(path),cropLTRB=box,nativePixelScale=1,sourceResampled=False))
 for n in (1024,2048,3072):
  box=[n-160,0,n+160,320] if side=='north' else [0,n-160,320,n+160]
  path=q/f'{side}-junction{n}.png';p.save_png(path,img.crop(box));ext.append(dict(file=str(path),sha256=p.sha(path),cropLTRB=box,nativePixelScale=1,sourceResampled=False))
p.write_json(q/'manifest.json',dict(candidate=m['output'],north=dict(file=str(north),sha256=p.sha(north)),east=dict(file=str(east),sha256=p.sha(east)),crops=ext,actuallyViewed=False,formalAccepted=False))
def pixelkey(im):return str(im.size)+hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
catalog={}
for review in (T/'qa/source-review').glob('*/*review*.json'):
 r=p.read(review)
 if not r.get('actuallyViewed'):continue
 for c in r.get('crops',[]):
  if not c.get('actuallyViewed') or not Path(c['file']).exists() or p.sha(c['file'])!=c['sha256']:continue
  pic=Image.open(c['file']).convert('RGB');verdict=c.get('verdict','pass' if r['status'].startswith('passed') else 'pending')
  item=dict(reviewFile=str(review),reviewSha256=p.sha(review),reviewedCrop=c,verdict=verdict,notes=r.get('notes'))
  catalog[pixelkey(pic)]=item
  catalog[pixelkey(pic.transpose(Image.Transpose.ROTATE_90))]=item
results=[]
for c in m['qa']+ext:
 old=catalog.get(pixelkey(Image.open(c['file'])))
 results.append(dict(file=c['file'],sha256=c['sha256'],reviewReusedByExactPixelIdentity=bool(old),status=old['verdict'] if old else 'pending',priorReview=old))
p.write_json(T/'qa'/(name+'.reused-source-review.json'),dict(candidate=m['output'],crops=results,formalAccepted=False))
arr=np.asarray(im);cnt=0;refs=[]
for s in m['nativeSources']:
 raw=Image.open(s['file']).convert('RGB');host=Path(p.read(s['generationRecord']['file'])['evidence']['hostOutputPath']);assert p.sha(host)==s['sha256']
 x,y=s['tileCorePasteXY'];assert np.array_equal(arr[y:y+1024,x:x+1024],np.asarray(raw)[115:1139,115:1139]);cnt+=1024*1024;refs.append(dict(file=s['file'],sha256=s['sha256'],hostOutputPath=str(host),hostBytesIdentical=True))
p.write_json(T/'qa'/(name+'.native-pixel-proof.json'),dict(candidate=m['output'],provedPixels=cnt,sources=refs,sourceResampled=False,sourceRecolored=False,status='passed_exact_same_world_native_pixels',formalAccepted=False))
print(json.dumps(dict(candidate=m['output'],total=len(results),reused=sum(x['reviewReusedByExactPixelIdentity'] for x in results),passed=sum(x['status']=='pass' for x in results),needsRepair=sum(x['status']=='needs_repair' for x in results),pending=[str(Path(x['file']).relative_to(T)) for x in results if x['status']=='pending'],pixelProof=cnt)))
