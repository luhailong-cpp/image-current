from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parents[1]
T=Z/'r07_c15'
Q=T/'qa/core-baseline/4310c2993aead148fef7'
R=T/'qa/local-repair-20261013'
R.mkdir(exist_ok=True)
base=Q/'r07_c15-core-baseline.candidate.png'
im=Image.open(base).convert('RGB')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
items=[('post',[2450,300,3704,1554]),('stair',[380,2450,1634,3704])]
records=[]
for name,box in items:
    f=R/(name+'-target-v1.png')
    assert not f.exists(),f
    im.crop(box).save(f)
    records.append({'id':name,'file':str(f),'sha256':sha(f),'crop':box,'operation':'integer crop; no resize or painting','source':str(base),'sourceSha256':sha(base)})
(R/'targets-v1.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
tp=json.loads((T/'tile-progress.json').read_text(encoding='utf-8-sig'))
tp.update({'selectedCoreCount':16,'remainingCoreCount':0,'candidate':str(base),'candidateSha256':sha(base),'completeCandidateCount':1,'internalPassed4kCount':0,'formalAcceptedCount':0,'nextPatch':None,'preparedNeverSubmitted':[],'status':'complete_native_candidate_two_local_P2_repairs','fullAssembly':str(Q/'assembly.json'),'updatedAt':datetime.now(timezone.utc).isoformat()})
(T/'tile-progress.json').write_text(json.dumps(tp,indent=2)+'\n',encoding='utf-8')
old=json.loads((T/'qa/model-pause-20261012/visual-review.json').read_text(encoding='utf-8'))
review={'tile':'r07_c15','candidate':str(base),'candidateSha256':sha(base),'nativeCoreCount':16,'internalPassed4kCount':0,'formalAcceptedCount':0,'reusedPriorReview':str(T/'qa/model-pause-20261012/visual-review.json'),'reusedUnchangedSourceCount':15,'reusedInternalJoins':22,'reusedIntersections':8,'newJoinWindowsReviewed':['horizontal-p34-p44-join-100pct.png','vertical-p43-p44-join-100pct.png'],'newIntersectionReviewed':'intersection-r3-c3-100pct.png','newFindings':'p44 joins continuous countertop, rails, green inset and stone floor; no new P2. Minor texture variation remains P3.','p2Issues':old['p2Issues'],'updatedAt':datetime.now(timezone.utc).isoformat()}
for a in review['p2Issues']:a['repairStatus']='active_under_latest_builtin_model_policy'
(R/'baseline-review.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records))
