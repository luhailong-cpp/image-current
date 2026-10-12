"""Bind explicit root-reviewed candidate selections to their exact image hashes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parent.parent
EV=ROOT/'provenance/foot-axis-20261004'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
review=read(EV/'root-review.json');assert review['pendingDirections']==[]
assert review['passedCombatCandidates']=={'hit/W':[3,4,5]}
assert read(EV/'audit-run-arms.json')['mandatoryCorrections']==[]
expected={'NE':[10,11],'SE':[4,5,7],'SW':[9,10,11,12],'NW':[1,2,9,10,11]}
assert review['passedCandidates']==expected
repairs=[]
for d,frames in expected.items():
    selection=read(EV/f'repair-selection-{d}.json');assert sorted(r['frame'] for r in selection)==frames
    for r in selection:
        file=r.get('reviewFile') or r['sourceFile'];assert sha(ROOT/file)==r['sha256']
        repairs.append({'action':'run','direction':d,'frame':r['frame'],'version':r['version'],'reviewFile':file,'sha256':r['sha256'],'nativeSha256':r['nativeSha256'],'previousSha256':r.get('previousSha256') or r['previousFinalSha256'],'visualReview':{'reviewer':'root_and_direction_agent','actuallyViewed':True,'notes':r['visualNotes'],'candidateReview':'provenance/foot-axis-20261004/root-review.json','passed':True,'clientValidated':False}})
selection=read(EV/'repair-selection-hit-W.json')
assert sorted(r['frame'] for r in selection)==[3,4,5]
for r in selection:
    assert r['action']=='hit' and r['direction']=='W' and sha(ROOT/r['reviewFile'])==r['sha256']
    repairs.append({k:r[k] for k in ['action','direction','frame','version','reviewFile','sha256','nativeSha256','previousSha256']} | {'visualReview':{'reviewer':'root_and_action_agent','actuallyViewed':True,'notes':r['visualNotes'],'candidateReview':'provenance/foot-axis-20261004/root-review.json','passed':True,'clientValidated':False}})
audits=['audit-run-arms.json','audit-hit.json','audit-attack.json','audit-cast.json']
assert all((EV/p).is_file() for p in audits)
attack=read(EV/'audit-attack.json')['rows']
assert len(attack)==24 and all(r['actuallyViewed'] and not r['mandatoryCorrection'] for r in attack)
cast=read(EV/'audit-cast.json')['summary']
assert cast['frameCount']==32 and cast['mustCorrectCount']==0
hit=read(EV/'audit-hit.json')['summary']
assert hit['reviewedFrames']==12 and hit['mustRepair']==['W03','W04','W05']
acceptance={'schemaVersion':1,'acceptedAt':datetime.now(timezone.utc).isoformat(),'accepted':True,'acceptanceScope':'offline all-196-frame limbs/grip review and selected local repairs, not human approval or client runtime validation','clientValidated':False,'repairs':repairs,'retainedRunFrames':114,'unchangedCombatFrames':65,'mandatoryCorrectionsRemaining':[],'rootReviewSha256':sha(EV/'root-review.json'),'baselineSha256':sha(EV/'baseline.json'),'audits':[{'file':'provenance/foot-axis-20261004/'+p,'sha256':sha(EV/p)} for p in audits],'referenceReview':'provenance/foot-axis-20261004/reference-review.json','timing':{'frameMs':75,'cycleMs':1200,'uniform':True},'contactFramesByDirection':{d:{'RIGHT':list(range(1,9)),'LEFT':list(range(9,17))} for d in ['N','NE','E','SE','S','SW','W','NW']}}
assert not (EV/'acceptance.json').exists()
(EV/'acceptance.json').write_text(json.dumps(acceptance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'acceptedRepairs':len(repairs),'retainedRunFrames':114,'clientValidated':False}))
