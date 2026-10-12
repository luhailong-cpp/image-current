from pathlib import Path
from datetime import datetime,timezone
import json,sys
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
p=json.loads((B/'progress.json').read_text(encoding='utf-8-sig'))
p.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),activeTile='r13_c06',activeCoordinate='r13_c06:p01_01_repair',currentStage='native_coverage_and_targeted_repairs',productionInProgress=True,holdNewImageGeneration=False,generationStopped=False)
p['zoneDeliverySummary']={'targetDeduplicatedTiles':64,'full16Native4kCandidates':p['complete4kCandidateCount'],'internalCheckedPassed':p['internalPassed4kCount'],'tilesStillMissingNativePatches':p['missingFullTileCount'],'fullCandidatesPendingRepairOrInternalCheck':p['complete4kCandidateCount']-p['internalPassed4kCount'],'missingNativePatchCount':p['remainingCorePatchCount'],'formalAccepted':p['formalAcceptedCount'],'countsSnapshotUtc':p['countsSnapshotUtc'],'scope':'Only southwest rows9-16 columns1-8; outside-city boundary availability does not count as undrawn local tiles.'}
p['workerStatus'].update(activeGenerationWorkers=['root','sw_left_resume_20261012b','sw_right_resume_20261012b','sw_col5_resume_20261012b'],activeWorkers=['/root','/root/sw_left_resume_20261012b','/root/sw_right_resume_20261012b','/root/sw_col5_resume_20261012b'],activeGenerationTiles=['r13_c06','r09_c03','r10_c07','r14_c05'],productionLines=4)
if p.get('currentWorkerNetworkPermissionErrors'):p['historicalWorkerNetworkPermissionErrors']=p.get('historicalWorkerNetworkPermissionErrors',[])+p.pop('currentWorkerNetworkPermissionErrors')
atomic_json(B/'progress.json',p);print(json.dumps(p['zoneDeliverySummary']))
