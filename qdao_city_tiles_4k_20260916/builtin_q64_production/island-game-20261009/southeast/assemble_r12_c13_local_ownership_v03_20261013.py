from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent;Q=R/'qa/r12_c13-floor-ownership-20261013'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bp=R/'tiles/r12_c13.candidate-sol-20261012-v02.png';fp=R/'native/r12_c13_floor_end_joint_whole_v01.png';old=Image.open(bp).convert('RGB');fa=np.asarray(Image.open(fp).convert('RGB'));a=np.asarray(old).copy();mask=np.asarray(Image.open(Q/'trial-physical-joint-source-cut-v02.mask.png')).copy();mask[:115]=0;mask[1139:]=0;mask[:,:115]=0;mask[:,1139:]=0
mp=Q/'candidate-v03-floor-source-mask-native.png';Image.fromarray(mask).save(mp);ix=mask!=0;region=a[1421:2675,397:1651];region[ix]=fa[ix]
out=R/'tiles/r12_c13.candidate-sol-20261013-v03-local-ownership.png';assert not out.exists();im=Image.fromarray(a);im.save(out)
baseMeta=read(Path(str(bp)+'.generation.json'));ids=np.zeros((4096,4096),dtype=np.uint8);sources=[]
for i,s in enumerate(baseMeta['sources'],start=1):
 x,y=s['destination'];ids[y:y+1024,x:x+1024]=i;sources.append({'sourceId':i,'file':s['file'],'sha256':s['sha256'],'sourceCrop':[115,115,1139,1139],'destination':[x,y],'tileRelativeOrigin':[x-115,y-115]})
regionId=ids[1421:2675,397:1651];regionId[ix]=17;sources.append({'sourceId':17,'file':str(fp),'sha256':sha(fp),'sourceCoreCrop':[115,115,1139,1139],'tileRelativeOrigin':[397,1421],'nativeGlobalBox':[49549,46477,50803,47731],'binaryOwnershipMask':str(mp),'maskSha256':sha(mp)})
ip=Q/'candidate-v03-source-id.png';Image.fromarray(ids).save(ip);checks=[];total=0
for s in sources:
 ox,oy=s['tileRelativeOrigin'];sy,sx=np.where(ids==s['sourceId']);native=np.asarray(Image.open(s['file']).convert('RGB'));npix=int(len(sx));bad=int(np.count_nonzero(np.any(a[sy,sx]!=native[sy-oy,sx-ox],axis=1)));total+=bad;checks.append({'sourceId':s['sourceId'],'file':s['file'],'sha256':sha(Path(s['file'])),'ownedPixels':npix,'mismatchedPixels':bad,'allOwnedPixelsWithin1024Core':bool(np.all((sx-ox>=115)&(sx-ox<1139)&(sy-oy>=115)&(sy-oy<1139)))})
proof={'candidate':str(out),'candidateSha256':sha(out),'sourceIdMap':str(ip),'sourceIdSha256':sha(ip),'sourceIdCount':17,'coveredPixels':int(np.count_nonzero(ids)),'unownedPixels':int(np.count_nonzero(ids==0)),'mismatchedPixels':total,'resampled':False,'blended':False,'RGBModified':False,'checks':checks};write(Q/'candidate-v03-source-id-proof.json',proof)
meta={'file':str(out),'sha256':sha(out),'width':4096,'height':4096,'operation':'exact world-registered source-ID binary pixel ownership; no scaling, warping, blending or RGB edit','baseCandidate':str(bp),'baseCandidateSha256':sha(bp),'sources':sources,'selectedBasePatchVersions':baseMeta['selectedPatchVersions'],'newRepairOwnedPixelCount':int(np.count_nonzero(ix)),'sourcePixelProof':str(Q/'candidate-v03-source-id-proof.json'),'status':'provisional_local_source_ownership_pending_root_review','formalAccepted':False,'internalAccepted':False,'createdAtUtc':datetime.now(timezone.utc).isoformat()};write(Path(str(out)+'.generation.json'),meta)
items=[]
for rr in range(4):
 for cc in range(1,4):
  b=[cc*1024-256,rr*1024,cc*1024+256,(rr+1)*1024];p=Q/f'candidate-v03-seam-v-r{rr+1}-c{cc}.png';im.crop(tuple(b)).save(p);items.append({'id':f'v-r{rr+1}-c{cc}','box':b,'file':str(p),'sha256':sha(p),'status':'pending_review'})
for rr in range(1,4):
 for cc in range(4):
  b=[cc*1024,rr*1024-256,(cc+1)*1024,rr*1024+256];p=Q/f'candidate-v03-seam-h-r{rr}-c{cc+1}.png';im.crop(tuple(b)).save(p);items.append({'id':f'h-r{rr}-c{cc+1}','box':b,'file':str(p),'sha256':sha(p),'status':'pending_review'})
junctions=[]
for rr in range(1,4):
 for cc in range(1,4):
  b=[cc*1024-256,rr*1024-256,cc*1024+256,rr*1024+256];p=Q/f'candidate-v03-junction-r{rr}-c{cc}.png';im.crop(tuple(b)).save(p);junctions.append({'id':f'junction-r{rr}-c{cc}','box':b,'file':str(p),'sha256':sha(p),'status':'pending_review'})
ownedEdges=[]
for name,b in [('whole-object',[397,1421,1651,2675]),('complete-T-joint',[850,2048,1210,2470]),('upper-source-edge',[950,1980,1600,2180]),('lower-source-edge',[950,2200,1600,2440]),('right-source-edge',[1400,1920,1660,2430]),('old-source-left-preserved',[720,2100,990,2420])]:
 p=Q/f'candidate-v03-ownership-{name}.png';im.crop(tuple(b)).save(p);ownedEdges.append({'id':name,'box':b,'file':str(p),'sha256':sha(p),'status':'pending_review'})
write(Q/'candidate-v03-actual-qa.json',{'candidate':str(out),'sha256':sha(out),'internalSeams':items,'junctions':junctions,'ownershipBoundaryQA':ownedEdges,'formalAccepted':False,'status':'pending_local_and_root_review'})
print(json.dumps({'candidate':str(out),'sha256':sha(out),'repairOwnedPixels':int(np.count_nonzero(ix)),'sourceProofMismatch':total,'allSourcesCoreOnly':all(c['allOwnedPixelsWithin1024Core'] for c in checks),'QA':str(Q/'candidate-v03-actual-qa.json')}))
