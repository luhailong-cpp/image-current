from workflow import *
import time
original_write=write
def write(path,value):
 for attempt in range(8):
  try:
   return original_write(path,value)
  except OSError:
   if attempt==7:raise
   time.sleep(0.25)
from PIL import Image
import numpy as np
q=ROOT/'qa/r12_c11-sol-20261012-final-v02'
f=ROOT/'tiles/r12_c11.candidate-sol-20261012-v02.png'
expected='9f8b0af6505b75bced4513a1bae6010a101891359cbf795b475b5a4e4294df72'
assert sha(f)==expected
review=read(q/'left-visual-review.json');proof=read(q/'source-pixel-proof.json')
assert review['internalSeamsPassed']==24 and review['junctionsPassed']==9 and proof['replayMismatchedPixels']==0
actual=np.array(Image.open(f).convert('RGB'))
for e in review['entries']:
 assert sha(Path(e['file']))==e['sha256']
 if e.get('sourceCrop'):
  x,y,x1,y1=e['sourceCrop'];assert np.array_equal(actual[y:y1,x:x1],np.array(Image.open(e['file']).convert('RGB')))
 assert e['status']=='visual_pass_no_substantive_issue'
write(q/'root-key-review.json',{'reviewedAtUtc':now(),'reviewer':'root','candidate':str(f),'candidateSha256':expected,'independentlyViewed':['fullPreview','h32','h33','v23','v33','j11','j12','j13','j21','j22','j23','j31','j32','j33','east1','east2','east3','east4'],'independentKeyReview':'pass','allOwnerReviewedCropHashesAndActualInternalPixelsVerified':True,'ownerInternalSeams24':'pass','ownerJunctions9':'pass','sourceReplayMismatchedPixels':0,'externalLayoutIssue':'Shared gold-capped foreground column ends too early in r12 and is duplicated in r13; complete cross-column upper/lower repair underway. Internal seam continuity of this candidate remains passed.','formalAccepted':False})
r=read(ROOT/'production-resume-20261012.json')
new=[]
for tid,rev,digest,qp,reviewPath in [
 ('r12_c11','sol-20261012-v02',expected,q/'source-pixel-proof.json',q/'root-key-review.json'),
 ('r12_c12','sol-20261012-v01','afc8b32555ff1d7b19de32c2e54e446245d62867f6b7ed5490d0ed2dbe0189fc',ROOT/'qa/r12_c12-sol-20261012-v01/source-proof.json',ROOT/'root-candidate-independent-review.json')]:
 cf=ROOT/'tiles'/f'{tid}.candidate-{rev}.png';assert sha(cf)==digest
 new.append({'tile':tid,'candidate':str(cf),'sha256':digest,'fullyCovered':True,'internalPassed':True,'externalPassed':False,'localArtworkAcceptanceReady':False,'formalAccepted':False,'sourceProof':str(qp),'review':str(reviewPath),'pending':'Shared column r12-to-r13 layout repair and incomplete remaining external neighbor edges.'})
r['currentAdoptedCandidates']=[x for x in r['currentAdoptedCandidates'] if x['tile'] not in ['r12_c11','r12_c12']]+new
r['pendingCandidates']=[x for x in r.get('pendingCandidates',[]) if x['tile'] not in ['r12_c11','r12_c12']]
r['pendingRepairs']=[{'id':'r12-r13-c11-c12-shared-long-column','tiles':['r12_c11','r12_c12','r13_c11','r13_c12'],'reason':'The shared gold-capped foreground column must extend out r12 south and have a single shaft/base in r13; current r12 premature foot and r13 duplicate cap found while checking actual layout continuation.','upperNativeRequest':'r12_c11_c12_shared_column_upper_v01','status':'whole_object_native_generation_in_flight'}]
r['counts'].update(generatedNativeCount=len(list((ROOT/'native').glob('*.png'))),fullyCovered4kCount=12,complete4kCount=12,internalPassed4kCount=12)
r.update(updatedAtUtc=now(),inFlightRequests=['r12_c11_c12_shared_column_upper_v01'],nextStep='Repair shared long column across r12/r13 c11/c12 using original builtin native output; continue r13 deck and remaining neighboring tiles.')
write(ROOT/'production-resume-20261012.json',r)
for fname in ['progress.json','production-state.json']:
 p=read(ROOT/fname);p.update(updatedAt=now(),pendingCandidates=r['pendingCandidates'],pendingRepairs=r['pendingRepairs'],rootInFlightCount=1,inFlight=True,nextStep=r['nextStep'])
 if fname=='progress.json':p.update(**r['counts'],currentAdoptedCandidates=r['currentAdoptedCandidates'],currentTile='r13_c12',currentPatch='shared_column_upper')
 else:p.update(counts=r['counts'],currentAdoptedCandidates=r['currentAdoptedCandidates'])
 write(ROOT/fname,p)
p=read(ROOT/'progress-r12_c12.json');p.update(updatedAt=now(),status='internal_passed_external_long_column_repair_pending',internalPassed4kCount=1,pendingRepairs=r['pendingRepairs'],nextStep=r['nextStep'],inFlight=False)
write(ROOT/'progress-r12_c12.json',p)
p=read(ROOT/'selected-native-r12_c12-sol-20261012-v01.json');p.update(internalAccepted=True,externalAccepted=False,formalAccepted=False,internalReview=str(ROOT/'root-candidate-independent-review.json'),pendingExternalLayoutRepair=r['pendingRepairs'])
write(ROOT/'selected-native-r12_c12-sol-20261012-v01.json',p)
m=read(ROOT/'proposed-overlay-r12_c12-board-end-20261012-v01.json');m['adoptedAtUtc']=now();m['internalCandidateReview']='root actual outer joins, 9 junctions and independent 24 seams passed'
for e in m['overlays']:e['status']='adopted_internal_joins_passed_external_east_pending'
write(ROOT/'adopted-overlay-r12_c12-board-end-20261012-v01.json',m)
p=read(ROOT/'qa/r12_c12-sol-20261012-v01/root-visual-review.json');p.update(internalSeams24='pass independent actual-pixel review',independentReview=str(ROOT/'root-candidate-independent-review.json'),externalLayoutIssue=r['pendingRepairs'])
write(ROOT/'qa/r12_c12-sol-20261012-v01/root-visual-review.json',p)
assert sha(ROOT/'migration-freeze-20261011.json')=='fde0f73f4342364e2d75c54401e9d4b66e378d3583d86ed6b2e3c13368954eeb'
print(json.dumps({'counts':r['counts'],'formalAccepted':False}))

