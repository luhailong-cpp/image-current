import json,sys,hashlib
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from checkpoint_resume import atomic_json
B=Path(__file__).resolve().parent.parent
p=json.loads((B/'progress.json').read_text(encoding='utf-8-sig'))
s=json.loads((B/'production-resume-20261012.json').read_text(encoding='utf-8-sig'))
stamp=datetime.now(timezone.utc).isoformat()
root_tile='r12_c06'
latest=max(list((B/root_tile/'native').glob('*.generation.json'))+list((B/root_tile/'refinement/versions').glob('*/*.generation.json')),key=lambda p:p.stat().st_mtime_ns)
g=json.loads(latest.read_text(encoding='utf-8-sig'))
next_patch=next((f'p{r:02}_{c:02}' for r in range(1,5) for c in range(1,5) if not (B/root_tile/'native'/f'p{r:02}_{c:02}.png.generation.json').exists()),'full-tile-and-cross-tile-QA')
lanes={'root':'r12_c06 and remaining column6; shared catalog and cross-tile QA','sol_left_20261012':'columns1-4; r09_c03 production and r09_c02 retry','sol_right_20261012':'columns7-8; active r10_c07','sol_r12_repair_20261012':'r12_c05 v14 provisional handed off; active r14_c05 then rows15-16 column5'}
if s.get('currentPermissionErrors'):
    s['historicalPermissionErrors']=s.get('historicalPermissionErrors',[])+s['currentPermissionErrors']
s.update(updatedAtUtc=stamp,status='parallel_native_production_in_progress',rootNextCoordinate='r09_c06:p02_01',workerLanes=lanes,currentPermissionErrors=[],permissionRecoveryEvidence={'note':'Actual builtin outputs succeeded in root and all three replacement Sol ultra agents after previous worker errors.','rootGenerationRecord':str(latest),'sha256':hashlib.sha256(latest.read_bytes()).hexdigest()},latestSavedOutput={'file':g['file'],'sha256':g['sha256'],'generationRecord':str(latest),'formalAccepted':False},countsSnapshot=p.get('countsSnapshot'),countsSnapshotUtc=p.get('countsSnapshotUtc'),currentCounts={k:p.get(k) for k in ['generatedNativeCount','rejectedNativeCount','selectedNativePatchCount','complete4kCandidateCount','formalAcceptedCount','remainingCorePatchCount']})
p.update(updatedAtUtc=stamp,activeTile=root_tile,currentStage='full_tile_native_repair_and_external_QA',holdNewImageGeneration=False,productionInProgress=True)
s['rootNextCoordinate']=root_tile+':'+next_patch
p['workerStatus'].update(activeGenerationWorkers=list(lanes),activeGenerationTiles=[root_tile,'r09_c03','r10_c07','r14_c05'],productionLines=4)
atomic_json(B/'production-resume-20261012.json',s)
atomic_json(B/'progress.json',p)
print(json.dumps({'status':s['status'],'counts':s['currentCounts']},ensure_ascii=False))
