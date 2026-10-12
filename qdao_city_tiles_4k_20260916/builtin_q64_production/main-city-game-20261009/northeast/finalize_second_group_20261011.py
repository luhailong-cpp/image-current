from pathlib import Path
from PIL import Image,ImageChops
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
G=Z/'qa/connected-group-r07_c13-r08_c14';F=G/'b8d681f571f8430e473e';M=read(F/'manifest.json')
pairs={
'r07_c13':(Z/'r07_c13/qa/shared-foliage-20261011/before.candidate.png',Z/'r07_c13/qa/independent-final-review-20261011.json'),
'r08_c13':(Z/'qa/central-foliage-20261011/before/r08_c13.png',Z/'r08_c13/qa/internal-review-20261011.json'),
'r08_c14':(Z/'qa/central-foliage-20261011/before/r08_c14.png',Z/'r08_c14/qa/final-review-20261011.json')}
proof={}
boxes=[]
for r in range(4):
 for c in range(1,4):boxes.append([c*1024-192,r*1024,c*1024+192,(r+1)*1024])
for r in range(1,4):
 for c in range(4):boxes.append([c*1024,r*1024-192,(c+1)*1024,r*1024+192])
for r in range(1,4):
 for c in range(1,4):boxes.append([c*1024-450,r*1024-450,c*1024+450,r*1024+450])
for tid,(before,prior) in pairs.items():
 current=Path(M['sources'][tid]['file']);assert sha(current)==M['sources'][tid]['sha256']
 a=Image.open(before).convert('RGB');b=Image.open(current).convert('RGB')
 for box in boxes:assert ImageChops.difference(a.crop(box),b.crop(box)).getbbox() is None,(tid,box)
 proof[tid]={'before':str(before),'beforeSha256':sha(before),'candidate':str(current),'candidateSha256':sha(current),'priorInternalReview':str(prior),'priorInternalReviewSha256':sha(prior),'unchangedInternalSeamWindows':24,'unchangedIntersectionWindows':9,'boxes':boxes,'changedPixelBox':ImageChops.difference(a,b).getbbox()}
# Exact current exports must match already viewed pixels, with changed corner windows explicitly reviewed.
reviewed={}
first=G/'5f4a9800e41a661dbe22';second=G/'d257b1479221428912e7'
for label,nums,folder,who in [('south-west-east',[2,3,4],first,'native_quality'),('west-north-south',[1,2,3],first,'native_quality'),('east-north-south',[2,3,4],first,'root'),('north-west-east',[1,2,3,4],second,'root')]:
 for i in nums:
  name=f'{label}-{i}-100pct.png';assert sha(F/name)==sha(folder/name)
  reviewed[name]={'file':str(F/name),'sha256':sha(F/name),'reviewer':who,'reviewedFile':str(folder/name),'pixelIdenticalToReviewedFile':True,'status':'passed-no-P2'}
for name in ['south-west-east-1-100pct.png','west-north-south-4-100pct.png','east-north-south-1-100pct.png']:
 reviewed[name]={'file':str(F/name),'sha256':sha(F/name),'reviewer':'root','reviewedFile':str(F/name),'status':'passed-no-P2 after central repair'}
name='central-intersection-100pct.png';integrated=Z/'qa/central-foliage-20261011/integrated-central-100pct.png'
assert sha(F/name)==sha(integrated)
reviewed[name]={'file':str(F/name),'sha256':sha(F/name),'reviewer':'root and independent qa_r07','reviewedFile':str(integrated),'pixelIdenticalToReviewedFile':True,'status':'passed-local-central-shared-intersection'}
assert len(reviewed)==17
R=F/'visual-review.json'
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'passed_connected_group_shared_edges','sources':M['sources'],'manifest':str(F/'manifest.json'),'manifestSha256':sha(F/'manifest.json'),'windows':list(reviewed.values()),'windowCount':17,'internalPreservationProof':proof,'independentCentralReview':str(Z/'qa/central-foliage-20261011/independent-review.json'),'independentCentralReviewSha256':sha(Z/'qa/central-foliage-20261011/independent-review.json'),'resolvedP2':['r07c14 west stone truncation and foliage cutoff','central foliage cut after m03, resolved by southern native layer'],'openP2':[],'p3':['slight stone mineral/tone changes','short leaf-highlight change near central x790,y627; silhouette continuous'],'formalAcceptedCount':0,'outerWorldEdgesIncomplete':True}
save(R,report)
for tid in pairs:
 T=Z/tid;p=read(T/'tile-progress.json');p.update({'internalPassed4kCount':1,'candidateSha256':M['sources'][tid]['sha256'],'status':'complete_candidate_internal_and_connected_group_seams_reviewed','nextStep':'Continue adjacent unpainted assigned coordinates; world perimeter incomplete','visualReview':str(R),'formalAcceptedCount':0});save(T/'tile-progress.json',p)
 C=T/f'candidates/{tid}.candidate.png';side=read(str(C)+'.generation.json');side.update({'sha256':sha(C),'assetRole':'complete4kCandidate; internal and second connected group reviewed; outer-world edges incomplete','visualReview':str(R),'visualReviewSha256':sha(R),'pixelReplayVerified':True});save(str(C)+'.generation.json',side)
CG=read(Z/'connected-groups.json');CG['groups']=[g for g in CG['groups'] if g['group']!='r07-r08_c13-c14']
CG['groups'].append({'group':'r07-r08_c13-c14','review':str(R),'reviewSha256':sha(R),'sources':M['sources'],'connectedReviewedTileCount':4,'formalAcceptedCount':0,'sourceManifest':str(F/'manifest.json'),'sourceSignature':M['signature'],'sharedEdgeWindowsReviewed':17,'internalPassedTileCount':sum(read(Z/tid/'tile-progress.json').get('internalPassed4kCount',0)==1 for tid in M['sources'])})
save(Z/'connected-groups.json',CG)
print(json.dumps({'review':str(R),'windows':17,'internalPreservedTiles':list(pairs),'groupInternalPassed':CG['groups'][-1]['internalPassedTileCount']}))

