from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
authority=B.parents[3]/'docs/MAP_PRODUCTION_RESUME_20261012.json'
assert read(authority)['newArtworkGenerationAllowed'] is True
W=B/'work-r04_c02';old=read(W/'repair-v3/r04_c02.candidate.assembly.json')
before=np.asarray(Image.open(W/'repair-v2/r04_c02.candidate.png'))
after=np.asarray(Image.open(old['candidate']['file']))
changed=np.any(before!=after,axis=2);yy,xx=np.where(changed)
assert len(xx)>0
changebox=[int(xx.min()+4096),int(yy.min()+12288),int(xx.max()+4097),int(yy.max()+12289)]
assert changebox[0]>=4890 and changebox[1]>=12700 and changebox[2]<=5630 and changebox[3]<=13210
md=W/'reviewed-20261012';md.mkdir(exist_ok=True)
for name in ['extended','r04_c02.candidate']:
 p=W/f'repair-v3/{name}.assembly.json';v=read(p)
 assert sha(v['candidate']['file'])==v['candidate']['sha256']
 assert sha(v['sourceIdMap']['file'])==v['sourceIdMap']['sha256']
 v['base']=str(W/'repair-v2/extended.assembly.json')
 v['metadataCorrection']={'originalAssembly':str(p),'originalAssemblySha256':sha(p),'reason':'Correct stale base label: composition script actually loaded repair-v2. Candidate and source map bytes unchanged.'}
 v['status']='internal-native-seams-pass-external-pending'
 write(md/f'{name}.assembly.json',v)
qa={'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r04_c02','candidate':old['candidate'],'internalAccepted':True,'northBoundaryAccepted':True,'eastBoundaryAccepted':True,'westBoundaryAccepted':False,'southBoundaryAccepted':False,'formalAccepted':False,'rootInspectedThisResume':['repair-v3 overview for layout only','paving repair whole after crop at native resolution','all 16 core-1-1 through core-4-4 native 1024 crops'],'priorReviewReused':'All 24 internal seam strips, 9 junctions, and 8 north/east boundary crops of repair-v2 were already reviewed in the prior production turn. Latest v3 change is confined to one interior paving joint. No full re-review of accepted tiles performed.','changedPixelCount':int(changed.sum()),'changedGlobalBox':changebox,'sourcePixelProof':old['proof'],'sourceMapUnmodified':True,'finding':'Paving junction now continuous, cloth hems/folds and both suspension ropes continuous; no visible object discontinuity across core views. West/south future neighbors remain pending.'}
write(md/'qa.json',qa)
idx=read(B/'current-artifacts.json');snapshot=B/'current-artifacts.before-resume-20261012.json'
if not snapshot.exists():shutil.copy2(B/'current-artifacts.json',snapshot)
idx['r04_c02']={'candidate':'work-r04_c02/repair-v3/r04_c02.candidate.png','assembly':'work-r04_c02/reviewed-20261012/r04_c02.candidate.assembly.json','qa':'work-r04_c02/reviewed-20261012/qa.json','status':'internally-accepted-north-east-boundaries-passed-candidate','formalAccepted':False}
if 'work-r05_c02' not in idx['adjacentWork']:idx['adjacentWork'].append('work-r05_c02')
write(B/'current-artifacts.json',idx)
resume={'schemaVersion':1,'zone':'northwest','resumedAtUtc':datetime.now(timezone.utc).isoformat(),'userAuthorization':'边继续做边传吧','authority':{'file':str(authority),'sha256':sha(authority)},'newArtworkGenerationAllowed':True,'historicalFreezeUnmodified':{'file':str(B/'migration-freeze-20261011.json'),'sha256':sha(B/'migration-freeze-20261011.json')},'gitWritesAllowed':False,'snapshotUpload':'Already captured independent snapshot; new work belongs to later incremental capture.','actualModel':None,'actualQuality':None,'route':'builtin','currentTile':'r05_c02','adoptedIndex':str(B/'current-artifacts.json'),'complete4kCandidatesOnDisk':10,'adopted4kCandidates':7,'internallyPassed4kCandidates':7,'formalAccepted4kCandidates':0,'target4kCandidates':49,'activeWorkers':{'root':'r05_c02 from current r04_c02 south and r05_c03 west native boundaries','paving_resume':'r02_c03 final candidate and independent neighbor delta','e3_integration_resume':'r02_c04 final candidate and independent neighbor delta','north_joint_resume':'r05_c04 recovery/final candidate and independent north delta'},'firstNewOutput':None,'latestAdoption':{'tile':'r04_c02','candidate':old['candidate'],'qa':str(md/'qa.json'),'newArtworkGenerated':False},'remaining':['Complete/reconcile 3 saved worker candidates and needed deltas.','Produce r05_c02 and 38 other coordinates lacking complete candidates.','Remaining exterior joins and formal acceptance.'],'errors':[]}
write(B/'production-resume-20261012.json',resume)
p=read(B/'progress.json');p.update(currentTile='r05_c02',currentPatch='s01_s04',nextStep='Generate r05_c02 native patches from accepted north/east boundaries',completeCandidateCoordinatesOnDisk=10,newArtworkGenerationAllowed=True,productionResume='production-resume-20261012.json');write(B/'progress.json',p)
print(json.dumps({'adopted':'r04_c02','changedPixels':int(changed.sum()),'changedGlobalBox':changebox,'nextTile':'r05_c02'},ensure_ascii=False))
