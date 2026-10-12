from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(B))
from checkpoint_resume import atomic_json
now=datetime.now(timezone.utc).isoformat()
P=B/'progress.json';p=json.loads(P.read_text(encoding='utf-8-sig'))
a=B/'r12_c05/pipeline/output/65a8077a665d5b93/assembly.json'
p.update(activeTile='r12_c05',primaryNewTile='r12_c05',activeTiles=['r12_c05','r09_c01','r09_c07'],activeCoordinate='r12_c05:p03_01',partialIsHistorical=False)
for k in list(p):
    if k.startswith('activeCandidate'): p.pop(k)
p['current4kCandidateCatalog']=str(B/'current-candidates.json')
p['workerStatus'].update(activeGenerationWorkers=['/root','/root/resume_r11c06','/root/resume_r10c06'],activeGenerationTiles=['r12_c05','r09_c01','r09_c07'],productionLines=3,independentQaWorker='/root/resume_crossedge_audit',reportedAtUtc=now)
partial=a.parent/'r12_c05.partial-p01_01-p02_04.png'
p.update(partial=str(partial),partialSha256=hashlib.sha256(partial.read_bytes()).hexdigest(),partialPixels=[4096,2048],partialCoreWorldBox=[16384,45056,20480,47104],partialAssembly=str(a),nextStep='Continue all 64 southwest tiles; coordinate macro grout geometry and quiet material repairs, then internal/external boundary acceptance.')
atomic_json(P,p)
C=B/'continuation-round-20261011.json';c=json.loads(C.read_text(encoding='utf-8-sig'))
c.update(recordedAtUtc=now,currentCoordinate='r12_c05:p03_01 new native coverage; full16 macro topology audit in progress',currentMergedAssembly=str(B/'integrated-20261011/v5/assembly.json'),currentPartialAssembly=str(a))
c['counts'].update(complete4kCandidates=p['complete4kCandidateCount'],partialNativeSlotsInR12C05=8,internalAcceptedCurrent=0,formalAccepted=0,selectedNativeSlotsTotal=p['selectedNativePatchCount'],countsSnapshotUtc=p['countsSnapshotUtc'])
c['network'].update(lastRootCallStartedAt='2026-10-11T12:09:05.221Z',lastRootCallReturnedImage=True,currentBuiltinSuccessVerified=True)
c['nextSteps']=['Continue native coverage in assigned exclusive columns.','Correct full-tile grout topology and quiet stone material before final tile acceptance.','Complete shared borders and cross-region checks when all required neighboring files exist.']
atomic_json(C,c)
print(json.dumps({'updatedAtUtc':now,'activeCoordinate':p['activeCoordinate'],'partial':p['partial'],'selectedNativeSlots':p['selectedNativePatchCount']}))
