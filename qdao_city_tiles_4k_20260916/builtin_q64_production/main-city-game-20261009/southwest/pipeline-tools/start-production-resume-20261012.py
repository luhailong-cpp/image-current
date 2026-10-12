from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,shutil
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
authority=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json');a=read(authority);assert a['newArtworkGenerationAllowed'] and not a['paidApiAllowed']
freeze=B/'migration-freeze-20261011.json';f=read(freeze);index=B/'current-candidates.json';snap=B/'current-candidates.before-resume-20261012.json'
if not snap.exists():shutil.copy2(index,snap)
now=datetime.now(timezone.utc).isoformat()
record={'schemaVersion':1,'startedAtUtc':now,'updatedAtUtc':now,'status':'active_native_production','userAuthorization':a['userAuthorization'],'authority':{'file':str(authority),'sha256':sha(authority)},'historicalFreeze':{'file':str(freeze),'sha256':sha(freeze)},'assignmentAuthority':a['assignmentAuthority'],'assignedTiles':'r09-r16 c01-c08, all64; no acceleration exclusions intersect this zone','builtinOnly':True,'paidApiUsed':False,'actualModel':None,'actualQuality':None,'historicalFreezeAndAuditFilesUnmodified':True,'gitMutationsAllowed':False,'rootNextCoordinate':'r09_c06:p01_03','workerLanes':{'root':'columns5-6 except r12_c05; currently r09_c06','resume_r11c06':'columns1-4; resume saved p03_02v02 in r09_c01 before next missing patch','resume_r10c06':'columns7-8; r09_c07 p03_03 prepared never submitted','resume_crossedge_audit':'r12_c05 exact repair lane from integrated-local-v06'},'baselineCounts':f['latestCounts'],'baselineSelectedCandidates':f['selectedCandidatePaths'],'firstNewOutput':None,'priorCandidateIndexSnapshot':str(snap),'nextStage':'Generate next native missing patch then update actual output record; all prior unaccepted seam/layout issues remain open.'}
rp=B/'production-resume-20261012.json';assert not rp.exists();atomic_json(rp,record)
catalog={'schemaVersion':2,'updatedAtUtc':now,'status':'active_native_candidates_with_open_qa','productionResume':str(rp),'tiles':{x['tile']:x for x in f['selectedCandidatePaths']},'complete4kCandidateCount':6,'formalAcceptedCount':0,'note':'Current adopted candidates include protected local repairs. Native coverage and visual acceptance are separate.'}
atomic_json(index,catalog)
p=read(B/'progress.json');p.update(updatedAtUtc=now,status='native_production_resumed_during_upload',holdNewImageGeneration=False,generationStopped=False,freezeFinalized=False,productionLines=4,generationResumeAuthority=str(authority),productionResume=str(rp),inFlightStatus='resumed_active_preparation',activeTile='r09_c06',activeCoordinate='r09_c06:p01_03',activeTiles=['r09_c06','r12_c05','r09_c01','r09_c07'],currentCandidateCatalog=str(index),current4kCandidateCatalog=str(index),nextStep='Continue latest saved native patches and unresolved repairs under 2026-10-12 authority; old migration freeze is historical evidence.')
atomic_json(B/'progress.json',p)
print(json.dumps({'resume':str(rp),'freezeSha256':sha(freeze),'candidateCount':len(catalog['tiles'])},ensure_ascii=False))

