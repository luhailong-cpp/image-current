from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
Q=Z/'seam-qa/r13_c08-selected-color-v2';m=read(Q/'manifest.json');seen=[]
for p in Q.glob('*.qa.json'):
 d=read(p)
 if not d['sourceComplete']:continue
 for source in d['sources']:assert sha(source['file'])==source['sha256']
 assert sha(d['image']['file'])==d['image']['sha256']
 d['visualReview']=dict(status='geometry_and_material_passed_available_sources',geometryPassed=True,colorPassed=True,materialPassed=True,candidateUsable=True,formalAccepted=False,note='Native exact core strip/crossing visually inspected; missing west and south sources still pending, and future neighbor changes invalidate this evidence.')
 write(p,d);seen.append(dict(id=d['id'],file=d['image']['file'],sha256=d['image']['sha256'],sources=d['sourcePixelSignature']))
assert len(seen)==15
rp=Q/'root-available-external-review.json';assert not rp.exists();write(rp,dict(createdAt=datetime.now(timezone.utc).isoformat(),tile='r13_c08',reviewedSegments=8,reviewedCrossings=7,evidence=seen,geometryPassed=True,materialPassed=True,completeExternalAcceptance=False,missingSides=['west','south'],formalAccepted=False))
sp=Z/'r13_c08/selected-patches.json';s=read(sp);s['availableExternalReview']=str(rp);write(sp,s)
g=Z/'seam-qa/G3-shared-stairs-resume-20261012/root-G3-joint-adoption-20261012.json'
w=Z/'seam-qa/repair-resume-20261012/root-wall-joint-adoption-20261012.json'
for tile in ['r12_c09','r12_c10']:
 sp=Z/tile/'selected-patches.json';s=read(sp);snap=Z/tile/'qa/selection-before-G3-metadata-correction-20261012.json';assert not snap.exists();snap.write_bytes(sp.read_bytes())
 assert Path(s['wallJointAdoption']).resolve()==g.resolve()
 s['G3JointAdoption']=str(g)
 if tile=='r12_c09':s['wallJointAdoption']=str(w)
 else:del s['wallJointAdoption']
 s['geometryBlockingIssues']=[v for v in s.get('geometryBlockingIssues',[]) if v!='G3']
 s.update(G3GeometryReview=str(g.parent/'root-v3-independent-geometry-review.json'),G3MaterialStatus='material_finish_pending',materialPending=True,internalReady=False,formalAccepted=False)
 write(sp,s)
print(json.dumps(dict(availableExternalEvidence=15,correctedJointMetadata=['r12_c09','r12_c10'])))
