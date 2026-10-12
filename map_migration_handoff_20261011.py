from pathlib import Path
from datetime import datetime, timezone
import json

root = Path('D:/work/image')
base = root / 'qdao_city_tiles_4k_20260916/builtin_q64_production'
def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

fields = ['status','updatedAt','updatedAtUtc','fullyCovered4kCount','complete4kCandidateCount','currentComplete4kCandidateCount','assembled4kCandidateCount','tilesComplete','candidate4kCount','formalAcceptedCount','internalPassed4kCount','externalPassed4kCount','withinRegionSeamsReviewed','currentTile','currentPatch','nextStep','nextAction','deliveryManifest','artDeliveryIndex','scopeCompletion','underlyingTaskComplete']
snapshots = []
for name in ['main-city-game-20261009','fishing-village-game-20261009','island-game-20261009']:
    folder = base / name
    contract = load(folder / 'production-contract.json')
    sections = []
    for section in sorted(folder.iterdir()):
        p = section / 'progress.json'
        if section.is_dir() and p.exists():
            progress = load(p)
            sections.append({'section':section.name,'source':p.relative_to(root).as_posix(),'lastFileWriteUtc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'recordedProgress':{k:progress[k] for k in fields if k in progress}})
    snapshots.append({'map':name,'productionContract':(folder/'production-contract.json').relative_to(root).as_posix(),'rows':contract['rows'],'columns':contract['columns'],'formalTilePixels':contract['formalTilePixels'],'wholeMapComplete':bool(contract.get('finalMapComplete',contract.get('finalCityComplete',False))),'formalAcceptedCountRecordedInContract':contract.get('formalAcceptedCount'),'sections':sections})

plan = load(base / 'acceleration-20261010/assignments.json')
handoff = {
 'schemaVersion':1,'snapshotAtUtc':datetime.now(timezone.utc).isoformat(),'userFacingTimeZone':'America/New_York',
 'ownerThreadId':'01a10997-f575-7002-8029-c9cdf6a0e32a',
 'coordinationNotice':{'sourceThread':'01a11b5e-158a-77d0-8c02-e8e503b7abe4','sourceTitle':'清理过大的图片素材','scope':'Git commit and push centralized in migration chat; map art continues.'},
 'localCommitment':{'gitMutationsPerformedForThisHandoff':False,'gitCommitPushOrAutomationAllowedHere':False,'migrationPrivateAreaTouched':False,'privateAreaToLeaveUntouched':'.git/migration-sync-20261011','knownGitAutomationOwnedByCurrentMapWork':[],'processesTerminated':False,'imageDeletionPerformed':False,'preserveAllExistingArtworkDuringMigration':True},
 'currentUserRequirements':{'artOnly':True,'runtimeTestingRequested':False,'builtinImageGenerationOnly':True,'paidImageApiAllowed':False,'networkRestorationConfirmedByUser':'已恢复网络权限','previousUserSuppliedAGENTSInstructionsStillApply':False,'maps':['主城日景','渔村日景','八仙岛日景'],'appearance':'Approved rounded bright Q Daoist style, Spring Festival walls/doors/windows plus sparse Lantern Festival and Mid-Autumn details; varied natural pale grey/blue-grey paving, spent firecracker scraps; trees only beside buildings/walls, short north/south exit roads; preserve approved layout and buildings.','capacityEvidence':'Each map has a conditional 5000-foot static layout trial. No runtime capacity approval is claimed, and user excluded runtime work.'},
 'completionCaveat':'All three complete maps remain unfinished. Candidate pixel coverage, interior checks and external seam acceptance are distinct. These are source-record snapshots, not fresh pixel QA. Several progress files lag their working subdirectories; do not sum mismatched legacy count fields.',
 'handoffEntryPoints':{'allocation':'qdao_city_tiles_4k_20260916/builtin_q64_production/acceleration-20261010/assignments.json','artResume':'qdao_city_tiles_4k_20260916/builtin_q64_production/resume-production-20261010/production-resume.json','networkResume':'qdao_city_tiles_4k_20260916/builtin_q64_production/acceleration-20261010/network-restored-20261011.json','styleIndex':'designs/README.md','approvedPreviews':'qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009'},
 'acceleratedOwnership':plan['assignments'],
 'importantNotes':['Jewelry approach original r03/r04 c10/c11 four 4K candidates passed interior and within-region seam checks; outer seams remain. Its same worker now owns additional r05_c10/r05_c11, so original four-task completion does not mean six-task completion.','City yamen north four candidates still have recorded roof/structure/material failures; do not mark them accepted just because four files exist.','Existing workers own separate coordinates; keep source and repair files during migration, including previews, raw images and unfinished unique native sources.','Absolute references in JSON point to D:/work/image. New machine must preserve this path or deliberately remap references; snapshot does not prove migration/upload completion.','This thread will not start/restart git helpers or modify migration index/object files. No upload progress is claimed here.'],
 'maps':snapshots
}
out = root / 'MAP_MIGRATION_HANDOFF_20261011.json'
out.write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'handoff':str(out),'maps':len(snapshots),'sections':sum(len(x['sections']) for x in snapshots),'wholeMapsFinished':sum(x['wholeMapComplete'] for x in snapshots)},ensure_ascii=False))
