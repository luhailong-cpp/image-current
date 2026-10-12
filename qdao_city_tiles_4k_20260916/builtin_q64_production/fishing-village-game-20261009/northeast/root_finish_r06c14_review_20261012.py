import json
from pathlib import Path
import root_workflow as w
import r06_c14_extension as b
Z=w.Z;Q=Z/'qa'/'r06_c14-v1';old=Q/'root-partial-review-at-freeze.json';d=json.loads(old.read_text(encoding='utf-8-sig'));C=Path(d['candidate']['path']);assert b.sha(C)==d['candidate']['sha256']
assert d['counts']=={'cores':16,'boundaryStrips':24,'junctions':5}
for item in d['reviewed']:assert b.sha(item['path'])==item['sha256']
extra=[b.ref(Q/(n+'.native-1to1.png'),'root direct native junction review') for n in ['junction_r2_c3','junction_r3_c1','junction_r3_c2','junction_r3_c3']]
f=Q/'root-internal-review-complete-20261012.json';assert not f.exists()
w.atomic(f,{'reviewer':'root','reviewedAtUtc':b.now(),'candidate':b.ref(C,'stable candidate'),'prior45Review':b.ref(old,'unchanged historical partial evidence'),'prior45HashesReverified':True,'newFourDirectlyViewed':extra,'counts':{'cores':16,'boundaryStrips':24,'junctions':9},'internalNativeQAPassed':True,'formalAccepted':False,'findings':['All four remaining native junctions have continuous post, plank, quay and water outlines. Small painterly facet differences are nonblocking.'],'remainingIndependentQA':['west four segments and three exterior junctions','north/south available outer junctions and final region boundary closure']})
p=Z/'records'/'active-candidates.json';index=json.loads(p.read_text(encoding='utf-8-sig'));index['tiles']['r06_c14']['reviewStatus']='root_internal49_native_QA_passed_external_pending';index['tiles']['r05_c12']['reviewStatus']='root_internal49_east_south15_passed_west_roof_tone_repair_north_pending';index['updatedAtUtc']=b.now();index['activeBlockers']=['r05_c12 west roof highlight repair pending; r05_c13/r05_c14 stable private candidates await independent review','Remaining owned native coordinates and available external seam closure in progress'];index['reviewPaths']+=['qa/r06_c14-v1/root-internal-review-complete-20261012.json','qa/r05_c12-root-v2/west-neighbor-QA/root-initial-review.json'];w.atomic(p,index)
print(json.dumps({'r06_c14IndependentInternalPassed':True,'ownedDistinctTarget':43,'fullyCovered4096Candidates':9,'rootIndependentInternalPassed':6,'tilesStillMissingNativeCoordinates':34,'fullCandidatesAwaitingInternalIndependentReview':3,'fullCandidatesWithKnownLocalSeamRepair':1,'formalAccepted':0}))
