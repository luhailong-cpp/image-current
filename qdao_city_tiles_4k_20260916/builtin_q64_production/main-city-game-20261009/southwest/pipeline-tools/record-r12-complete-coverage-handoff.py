from pathlib import Path
import json,sys,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
now=datetime.now(timezone.utc).isoformat();a=B/'r12_c05/pipeline/output/0dd17020392cb9ed/assembly.json';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
F=B/'full64-continuation-20261011.json';f=json.loads(F.read_text());f.update(updatedAtUtc=now,independentQaWorker=None,reviewPolicy='Root independently reviews outputs of regional and dedicated repair workers; pre-repair independent audits remain immutable.')
for t in f['tiles']:
    if t['tile']=='r12_c05':t.update(owner='/root/resume_crossedge_audit',role='dedicated macro/material/internal seam repairs after full16 native coverage',independentFinalReviewer='/root')
atomic_json(F,f)
P=B/'progress.json';p=json.loads(P.read_text());p.update(activeTile='r09_c05',primaryNewTile='r09_c05',activeCoordinate='r09_c05:p01_01',activeTiles=['r09_c05','r12_c05','r09_c01','r09_c07'],lastNewCompleteCandidate={'tile':'r12_c05','assembly':str(a),'assemblySha256':sha(a),'candidate':str(a.parent/'r12_c05.candidate.png'),'candidateSha256':sha(a.parent/'r12_c05.candidate.png'),'nativeSlots':16,'internalAccepted':False,'formalAccepted':False})
for k in list(p):
    if k.startswith('activeCandidate') or k in ['partial','partialSha256','partialPixels','partialCoreWorldBox','partialAssembly']:p.pop(k)
p['workerStatus'].update(activeGenerationWorkers=['/root','/root/resume_crossedge_audit','/root/resume_r11c06','/root/resume_r10c06'],activeGenerationTiles=['r09_c05','r12_c05','r09_c01','r09_c07'],productionLines=4,independentQaWorker=None,reportedAtUtc=now)
p.update(partialIsHistorical=False,nextStep='Root continues r09_c05 native production while dedicated r12_c05 worker repairs topology/material/shared edges; complete all64 and independent acceptance.')
atomic_json(P,p)
C=B/'continuation-round-20261011.json';c=json.loads(C.read_text());c.update(recordedAtUtc=now,currentCoordinate='root r09_c05:p01_01; r12_c05 full16 candidate under dedicated repair',currentR12C05Assembly=str(a),currentR12C05AssemblySha256=sha(a))
c['counts'].update(complete4kCandidates=p['complete4kCandidateCount'],partialNativeSlotsInR12C05=16,selectedNativeSlotsTotal=p['selectedNativePatchCount'],countsSnapshotUtc=p['countsSnapshotUtc'])
c['nextSteps']=['Continue all64 assigned native coverage on four builtin generation lines.','Repair r12_c05 macro topology, material and all internal joins; root independently verifies repair outputs.','Complete shared and cross-region boundaries before formal acceptance.']
atomic_json(C,c)
print(json.dumps({'recordedAtUtc':now,'rootTile':'r09_c05','repairTile':'r12_c05','countsSnapshotUtc':p['countsSnapshotUtc'],'full4kCandidates':p['complete4kCandidateCount'],'formalAccepted':p['formalAcceptedCount']}))
