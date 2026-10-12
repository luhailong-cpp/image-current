"""Assemble native source rectangles and prove every final RGB pixel against its owner."""
from workflow import *
from PIL import Image
import numpy as np
import sys
spec=read(Path(sys.argv[1]));tid=spec['tile'];rev=sys.argv[2]
assert len(spec['patchVersions'])==16
out=ROOT/'tiles'/f'{tid}.candidate-{rev}.png'
q=ROOT/'qa'/f'{tid}-{rev}'
assert not out.exists() and not q.exists()
q.mkdir()
im=Image.new('RGB',(4096,4096))
ids=np.full((4096,4096),255,dtype=np.uint8)
coverage=np.zeros_like(ids)
sources=[];operations=[]
for rc,v in sorted(spec['patchVersions'].items()):
 r,c=map(int,rc);x=(c-1)*1024;y=(r-1)*1024
 f=ROOT/'native'/f'{tid}_p{rc}_{v}.png'
 assert f.exists() and Path(str(f)+'.generation.json').exists()
 ni=Image.open(f).convert('RGB');assert ni.size==(1254,1254)
 sid=len(sources);src=[115,115,1139,1139];box=[x,y,x+1024,y+1024]
 im.paste(ni.crop(src),(x,y));ids[y:y+1024,x:x+1024]=sid;coverage[y:y+1024,x:x+1024]+=1
 sources.append({'id':sid,'file':str(f),'sha256':sha(f),'tileToNativeOffset':[115-x,115-y],'record':str(f)+'.generation.json'})
 operations.append({'sourceId':sid,'sourceCrop':src,'destinationBox':box})
assert np.all(coverage==1)
for manifest in spec.get('overlayManifests',[]):
 m=read(Path(manifest));assert m['tile']==tid
 for entry in m['overlays']:
  f=Path(entry['file']);assert sha(f)==entry['sha256']
  ni=Image.open(f).convert('RGB');assert ni.size==(1254,1254)
  sx,sy,sx1,sy1=entry['sourceCrop'];x,y,x1,y1=entry['destinationBox']
  assert (sx1-sx,sy1-sy)==(x1-x,y1-y) and 0<=x<x1<=4096 and 0<=y<y1<=4096
  sid=len(sources);im.paste(ni.crop((sx,sy,sx1,sy1)),(x,y));ids[y:y1,x:x1]=sid
  sources.append({'id':sid,'file':str(f),'sha256':sha(f),'tileToNativeOffset':[sx-x,sy-y],'record':str(f)+'.generation.json','adoptionManifest':str(manifest)})
  operations.append({'sourceId':sid,'sourceCrop':entry['sourceCrop'],'destinationBox':entry['destinationBox'],'overlay':True})
assert np.all(ids!=255)
im.save(out);Image.fromarray(ids).save(q/'source-id.png')
rgb=np.array(Image.open(out).convert('RGB'));replay=[]
for s in sources:
 assert sha(Path(s['file']))==s['sha256']
 yy,xx=np.where(ids==s['id']);a=np.array(Image.open(s['file']).convert('RGB'));dx,dy=s['tileToNativeOffset']
 assert not len(xx) or (xx.min()+dx>=0 and xx.max()+dx<1254 and yy.min()+dy>=0 and yy.max()+dy<1254)
 n=int(np.any(rgb[yy,xx]!=a[yy+dy,xx+dx],axis=1).sum())
 assert n==0
 replay.append({'sourceId':s['id'],'ownedPixels':len(xx),'mismatch':n})
proof={'candidate':str(out),'candidateSha256':sha(out),'dimensions':[4096,4096],'coveredPixels':int(ids.size),'sourceIdMap':str(q/'source-id.png'),'sourceIdMapSha256':sha(q/'source-id.png'),'sourceReplayMismatch':0,'sourceReplay':replay,'sources':sources,'operation':'unchanged native source pixels only; exact rectangular crop and hard paste; no rescale, interpolation, blending, RGB change, warping or painting'}
write(q/'source-proof.json',proof)
record={**proof,'generatedAt':now(),'width':4096,'height':4096,'fullCoverage':True,'allContributionsPixelExact':True,'operations':operations,'spec':str(Path(sys.argv[1]).resolve()),'actualModel':None,'actualQuality':None,'status':'full_candidate_pending_internal_and_external_review'}
write(Path(str(out)+'.generation.json'),record)
write(ROOT/f'selected-native-{tid}-{rev}.json',{'tile':tid,'candidate':str(out),'candidateSha256':sha(out),'sources':sources,'sourceIdMap':str(q/'source-id.png'),'formalAccepted':False,'internalAccepted':False,'externalAccepted':False})
for r in range(1,4):
 for c in range(1,4):
  box=[c*1024-256,r*1024-256,c*1024+256,r*1024+256]
  im.crop(box).save(q/f'junction_{r}{c}.png')
im.resize((1024,1024),Image.Resampling.LANCZOS).save(q/'preview.png')
# Every outer join introduced by an adopted repair must be viewed separately.
cuts=[]
for op in operations:
 if not op.get('overlay'):continue
 x,y,x1,y1=op['destinationBox'];sid=op['sourceId']
 for label,box in [('left',[max(0,x-256),y,min(4096,x+256),y1]),('right',[max(0,x1-256),y,min(4096,x1+256),y1]),('top',[x,max(0,y-256),x1,min(4096,y+256)]),('bottom',[x,max(0,y1-256),x1,min(4096,y1+256)])]:
  f=q/f'overlay-{sid}-{label}.png';im.crop(box).save(f);cuts.append({'file':str(f),'sourceCrop':box,'kind':label,'sourceId':sid})
write(q/'overlay-qa-cuts.json',{'candidate':str(out),'candidateSha256':sha(out),'cuts':cuts,'status':'pending_visual_review'})
print(json.dumps({'candidate':str(out),'sha256':sha(out),'sourceReplayMismatch':0,'sourceCount':len(sources),'coveredPixels':int(ids.size)}))
