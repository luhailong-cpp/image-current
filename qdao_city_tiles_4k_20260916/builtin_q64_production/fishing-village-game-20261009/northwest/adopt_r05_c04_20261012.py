from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent;W=B/'work-r05_c04/final-v2-20261012';O=B/'delivery-2x2/resume-20261012';O.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
delivery=read(W/'delivery.json')
for k in ['candidate','assembly','qa','sourceProof','sourceEvidence','northDelta']:
 e=delivery[k];assert sha(e['file'])==e['sha256'],k
idx=read(B/'current-artifacts.json');delta=read(W/'north-delta.json')
assert sha(B/idx['r04_c04']['candidate'])==delta['baseline']['candidate']['sha256']
old=np.asarray(Image.open(B/idx['r04_c04']['candidate']).convert('RGB'));new=np.asarray(Image.open(delta['candidate']).convert('RGB'));mask=np.asarray(Image.open(delta['mask']['file']))>0
assert np.array_equal(old[~mask],new[~mask]);assert int(mask.sum())==375176
qa={'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r05_c04','candidate':delivery['candidate'],'internalAccepted':True,'northBoundaryAccepted':True,'westBoundaryAccepted':True,'eastBoundaryAccepted':False,'southBoundaryAccepted':False,'formalAccepted':False,'agentReview':delivery['qa'],'sourceProof':delivery['sourceProof'],'sourceEvidence':delivery['sourceEvidence'],'rootInspected':['north-head-bridge.100pct','sand-1.after.100pct','sand-2.after.100pct','north-4.100pct','head-top.100pct','head-right.100pct','west-2.100pct'],'finding':'Changed sand transitions and post/rope bridge continuous; agent reviewed all 16 cores and internal seams. East/south joins deferred.'}
qp=O/'r05_c04.root-qa.json';write(qp,qa)
nqa={'createdAt':qa['createdAt'],'tile':'r04_c04','candidate':delta['candidateEvidence'],'internalAccepted':True,'southBoundaryAccepted':True,'formalAccepted':False,'priorQa':idx['r04_c04']['qa'],'northDelta':delivery['northDelta'],'deltaMaskPixels':int(mask.sum()),'outsideDeltaPixelMismatches':0,'rootInspected':['whole north-head bridge','head-top/right contours','new south join crop'],'sourceProof':delta['proof'],'finding':'Only native slim-post/head bridge delta adopted; prior road and center repairs preserved outside delta.'}
nqp=O/'r04_c04.root-qa.json';write(nqp,nqa)
idx['r05_c04']={'candidate':Path(delivery['candidate']['file']).relative_to(B).as_posix(),'assembly':Path(delivery['assembly']['file']).relative_to(B).as_posix(),'qa':qp.relative_to(B).as_posix(),'status':'internally-accepted-north-west-boundaries-passed-candidate','formalAccepted':False}
idx['r04_c04']={'candidate':Path(delta['candidate']).relative_to(B).as_posix(),'assembly':Path(delta['assembly']).relative_to(B).as_posix(),'qa':nqp.relative_to(B).as_posix(),'status':'internally-accepted-south-head-bridge-candidate','formalAccepted':False}
write(B/'current-artifacts.json',idx)
p=B/'production-resume-20261012.json';v=read(p);v.update(adopted4kCandidates=8,internallyPassed4kCandidates=8,updatedAtUtc=qa['createdAt'],networkState='builtin succeeded after renewed continue instruction',currentPatch='r05_c02_s01_s01_v01');v['completedThisResume']=['r04_c02 internal QA and adoption','r05_c04 complete candidate adoption','r04_c04 south native post-head delta adoption'];write(p,v)
print(json.dumps({'adopted':['r05_c04','r04_c04 delta'],'maskPixels':int(mask.sum()),'outsideMaskMismatch':0}))
