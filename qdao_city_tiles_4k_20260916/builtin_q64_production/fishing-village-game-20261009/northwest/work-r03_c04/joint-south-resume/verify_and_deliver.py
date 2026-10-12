from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;B=W.parents[1];O=W/'proposal-v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=read(O/'joint-assembly.json');results=[]
for a in d['artifacts']:
 p=Path(a['file']);ip=Path(a['sourceIdMap']['file']);im=np.asarray(Image.open(p));ids=np.asarray(Image.open(ip));assert im.shape==(4096,4096,3) and ids.shape==(4096,4096)
 assert sha(p)==a['sha256'] and sha(ip)==a['sourceIdMap']['sha256']
 ox,oy=a['globalBox'][:2];cnt=0
 for s in d['sources']:
  yy,xx=np.nonzero(ids==s['sourceId'])
  if not len(xx):continue
  src=np.asarray(Image.open(s['file']).convert('RGB'));assert sha(s['file'])==s['sha256'];sx=xx+ox-s['globalNativeBox'][0];sy=yy+oy-s['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(im[yy,xx],src[sy,sx]);cnt+=len(xx)
 assert cnt==4096*4096
 name=p.name.split('.')[0];old=d['baseNorth']['candidate'] if name=='r03_c04' else d['baseSouth']['candidate'];base=np.asarray(Image.open(old).convert('RGB'))
 mask=np.any(im!=base,axis=2);mp=O/(name+'.changed-pixels.png');Image.fromarray((mask*255).astype(np.uint8)).save(mp)
 y,x=np.nonzero(mask);box=[int(x.min()+ox),int(y.min()+oy),int(x.max()+ox+1),int(y.max()+oy+1)]
 results.append({'tile':name,'file':str(p),'sha256':sha(p),'pixelCount':cnt,'mismatches':0,'sourceIdMap':a['sourceIdMap'],'base':str(old),'changedPixelCount':int(mask.sum()),'changedGlobalBoundingBox':box,'changedPixelMask':{'file':str(mp),'sha256':sha(mp)}})
write(O/'independent-replay.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'verification':'reopened saved PNGs; each pixel checked by source ID against the recorded native RGB at global coordinate','totalPixels':33554432,'mismatches':0,'artifacts':results})
reviews=[]
for i in range(1,9):reviews.append({'file':str(O/f'shared-segment-{i:02d}.png'),'sha256':sha(O/f'shared-segment-{i:02d}.png'),'globalBox':[12288+(i-1)*512,12058,12288+i*512,12518],'viewedAtNativeResolution':True,'sharedBoundaryPassed':True,'finding':{1:'Post axis and full foot continuous; thin far-west halo ground-tone edge is retained and needs joint west-neighbor context in root 2x2 review.',2:'Wall foot and sand continuous.',3:'Sand continuous; no horizontal cut line.',4:'Lamp left ellipse and cast shadow continuous.',5:'Lamp right ellipse continuous with no notch or shard.',6:'Sand continuous.',7:'Sand continuous; no prior wide paving remaining at seam.',8:'Approved narrow diagonal stone triangle crosses shared edge, no horizontal cutoff.'}[i]})
for i in range(1,4):reviews.append({'file':str(O/f'shared-cross-{i}.png'),'sha256':sha(O/f'shared-cross-{i}.png'),'globalBox':[12288+i*1024-340,11948,12288+i*1024+340,12628],'viewedAtNativeResolution':True,'sharedBoundaryPassed':True,'finding':'Intersecting internal column and external row join is geometrically continuous.'})
for kind in ['post','lamp','road']:
 for edge in ['north','south','west','east']:
  p=O/(kind+'-'+edge+'.png');passed=not(kind=='road' and edge in ['north','west','east'])
  finding='Native bridge perimeter has continuous geometry and matched current local material.'
  if kind=='post' and edge=='west':finding='Post silhouette and wood shaft continuous. Narrow retained old sand-tone island near far-left foot will be checked against west tile by root.'
  if not passed:finding='Existing bright-blue northern road remains at upper bridge halo; incompatible with new matte gray paving. Must rebase/close with parallel northern paving repair before tile-wide internal acceptance.'
  reviews.append({'file':str(p),'sha256':sha(p),'viewedAtNativeResolution':True,'passedAgainstCurrentBase':passed,'finding':finding})
write(O/'visual-review.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'sharedNorthSouthBoundaryPassed':True,'allEightSharedSegmentsAndThreeJunctionsViewed':True,'postGeometryPassed':True,'lampGeometryPassed':True,'roadAtY12288GeometryPassed':True,'entireNorthTileInternalPassed':False,'formalAccepted':False,'records':reviews,'pending':['Rebase northern paving repair to bridge new matte gray road at global [15130,11490,16384,11720], including upper-left contour where old road was too wide.','Root 2x2 west-neighbor context check at post far-left halo, global x12288..12348,y12288..12550.','Future east tile r03c05/r04c05 outside present 2x2 not reviewed.']})
write(W/'delivery.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'task':'r03c04 to r04c04 shared north-south boundary whole-object repair','status':'shared-boundary-passed-await-north-paving-rebase-and-root-2x2-review','generatedNativeImages':3,'actualModel':None,'actualQuality':None,'route':'builtin','paidApiUsed':False,'fullDoubleCandidateAssembly':str(O/'joint-assembly.json'),'independentReplay':str(O/'independent-replay.json'),'visualReview':str(O/'visual-review.json'),'candidates':results,'integration':{'instruction':'Use new-source masks/global boxes and shared DP path from joint-assembly.json. Base north was initial r03c04.candidate.png, so do not replace a later northern paving candidate wholesale. Rebase repairs onto new north, preserving matte road bridge core. South base is joint-west/final-v3 with source-ID tracking of west-net repairs. Recheck west 2x2 corner after merge.','newBridges':[s for s in d['sources'] if 'joint-south-resume' in s['file']],'doNotClaimNorthInternalPassed':True},'originalCandidatesModified':False,'rootCurrentArtifactsModified':False})
print(json.dumps({'pixels':33554432,'mismatches':0,'candidates':[{k:v for k,v in a.items() if k in ['tile','sha256','changedPixelCount','changedGlobalBoundingBox']} for a in results]},ensure_ascii=False))
