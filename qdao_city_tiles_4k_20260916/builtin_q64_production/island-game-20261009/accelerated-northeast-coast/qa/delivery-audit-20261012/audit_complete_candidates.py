"""Read-only candidate audit. Writes only a new report in this directory."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import argparse
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
B = OUT.parent.parent
ORDER = ['r02_c13', 'r02_c14', 'r01_c13', 'r01_c14']
QA = {
    'r02_c13': 'qa/audit-final-r02-c13/final-review.json',
    'r02_c14': 'qa/audit-resume-20261012/r02_c14-final-review.json',
    'r01_c13': 'qa/audit-final-20261012/r01_c13-current-final-review.json',
    'r01_c14': 'qa/audit-final-20261012/r01_c14-row4-review.json',
}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--r01-c14-final-review', help='Final QA JSON path inside B; absolute or relative to B.')
args = parser.parse_args()
if args.r01_c14_final_review:
    QA['r01_c14'] = args.r01_c14_final_review

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def phash(im):
    return hashlib.sha256(im.tobytes()).hexdigest()

def inside(path):
    return Path(path).resolve().is_relative_to(B.resolve())

def geometry(ident):
    match = re.fullmatch(r'r(\d+)_c(\d+)_p(\d+)_(\d+)(?:_v\d+)?', ident)
    tr, tc, pr, pc = map(int, match.groups())
    x, y = (tc-1)*4096+(pc-1)*1024, (tr-1)*4096+(pr-1)*1024
    return {'id': ident, 'coreWorldBox': [x,y,x+1024,y+1024],
            'nativeWorldBox': [x-115,y-115,x+1139,y+1139],
            'coreCrop': [115,115,1139,1139]}, [(pc-1)*1024, (pr-1)*1024]

def latest(ident):
    paths = [p for p in (B/'native').glob(ident+'*.png')
             if re.fullmatch(re.escape(ident)+r'(?:_v\d+)?\.png',p.name)]
    return max(paths, key=lambda p: int(re.search(r'_v(\d+)',p.stem).group(1))
               if '_v' in p.stem else 1) if paths else None

started = datetime.now(timezone.utc).isoformat()
selection_path = B/'current-selection-20261012.json'
selection_hash_before = sha(selection_path)
selection = read(selection_path)
selected_candidates = {c['tileId']: c for c in selection['candidates']}
progress = read(B/'progress.json')
resume = read(B/'production-resume-20261012.json')
script_records = [{'file': (B/name).as_posix(), 'sha256': sha(B/name)}
                  for name in ['coast_work.py','resume_progress_20261012.py']]
tiles = []
problems = []
for tile in ORDER:
    candidate_path = B/'candidates'/f'{tile}.4096-candidate.png'
    if not candidate_path.exists():
        continue
    assembly_path = candidate_path.with_suffix('.png.assembly.json')
    assembly = read(assembly_path)
    candidate_sha = sha(candidate_path)
    with Image.open(candidate_path) as opened:
        candidate_size, candidate_mode = list(opened.size), opened.mode
        candidate = opened.convert('RGB')
    reconstructed = Image.new('RGB', (4096,4096))
    grid = assembly['selectedCores']
    native_selection = {p['id']:p for p in selection['native'][tile]}
    qa_path = B/QA[tile]
    assert inside(qa_path), qa_path
    qa = read(qa_path)
    qa_sources = qa.get('sources')
    qa_manifest_path = None
    if not qa_sources and qa.get('sourceManifest'):
        qa_manifest_path = Path(qa['sourceManifest'])
        assert inside(qa_manifest_path)
        qa_sources = read(qa_manifest_path)['sources']
    qa_sources = {Path(s['file']).stem:s for s in (qa_sources or [])}
    core_checks = []
    for source in assembly['sources']:
        source_path = Path(source['file'])
        assert inside(source_path), source_path
        record_path = Path(source['generationRecord'])
        assert inside(record_path), record_path
        record = read(record_path)
        ident = source_path.stem
        expected_geo, at = geometry(ident)
        native_sha = sha(source_path)
        with Image.open(source_path) as opened:
            size, mode = list(opened.size), opened.mode
            native = opened.convert('RGB')
        core = native.crop((115,115,1139,1139))
        destination_box = [at[0],at[1],at[0]+1024,at[1]+1024]
        current_core = candidate.crop(destination_box)
        reconstructed.paste(core, tuple(at))
        source_index_record = native_selection.get(ident, {})
        qa_source = qa_sources.get(ident, {})
        unversioned = re.sub(r'_v\d+$','',ident)
        latest_source = latest(unversioned)
        prompt_path, receipt_path = Path(record['prompt']), Path(record['receipt'])
        assert inside(prompt_path) and inside(receipt_path)
        checks = {
            'nativePngHashMatchesAssembly': native_sha == source['sha256'],
            'nativePngHashMatchesGenerationRecord': native_sha == record['sha256'],
            'nativePngHashMatchesCurrentSelection': native_sha == source_index_record.get('sha256'),
            'nativePngHashMatchesQaSelectedSource': native_sha == qa_source.get('sha256'),
            'nativeDimensionsExactly1254': size == [1254,1254],
            'nativeDimensionsMatchGenerationAndAssembly': size == record['size'] == [record['nativeWidth'],record['nativeHeight']] == source['nativeSize'],
            'nativeDimensionsMatchCurrentSelection': size == source_index_record.get('dimensions'),
            'nativeModeMatchesGenerationRecord': mode == record['mode'],
            'recordGeometryMatchesCoordinate': all(record.get(k)==v for k,v in expected_geo.items()),
            'assemblyCropExactly1024': source['sourceCrop'] == [115,115,1139,1139] and core.size==(1024,1024),
            'assemblyPasteMatchesCoordinate': source['pasteAt'] == at,
            'gridEntryMatchesSource': grid[at[1]//1024][at[0]//1024] == ident,
            'selectedSourceIsLatestVersion': latest_source == source_path,
            'candidateCorePixelsExactlyEqualNativeCrop': current_core.tobytes() == core.tobytes(),
            'resizedAfterGenerationFalse': record['resizedAfterGeneration'] is False,
            'promptExistsAndHashMatches': prompt_path.exists() and sha(prompt_path) == record['promptSha256'],
            'receiptExists': receipt_path.exists(),
            'builtinToolAndRouteRecorded': record.get('tool')=='image_gen.imagegen' and record.get('route')=='builtin',
            'actualModelAndQualityTruthfulUnknown': record.get('actualModel')=='unknown' and record.get('actualQuality')=='unknown',
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            problems.append({'tileId':tile, 'coreId':ident, 'failedChecks':failed})
        core_checks.append({'id':ident, 'file':source_path.as_posix(), 'fileBytes':source_path.stat().st_size,
            'sha256':native_sha, 'dimensions':size, 'mode':mode,
            'generationRecord':record_path.as_posix(), 'generationRecordSha256':sha(record_path),
            'sourcePathRecordedOnlyNotReopened':record.get('sourcePath'),
            'coreCrop':[115,115,1139,1139], 'pasteAt':at, 'candidateCoreBox':destination_box,
            'coreRgbPixelSha256':phash(core), 'candidateCoreRgbPixelSha256':phash(current_core),
            'prompt':prompt_path.as_posix(), 'promptSha256':record['promptSha256'],
            'receipt':receipt_path.as_posix(), 'receiptSha256':sha(receipt_path) if receipt_path.exists() else None,
            'actualModel':record.get('actualModel'), 'actualQuality':record.get('actualQuality'),
            'metadataStatusAtCreation':record.get('status'), 'checks':checks, 'passed':not failed})
    selected_candidate = selected_candidates.get(tile,{})
    tile_checks = {
        'candidateHashMatchesAssembly': candidate_sha == assembly['sha256'],
        'candidateHashMatchesCurrentSelection': candidate_sha == selected_candidate.get('sha256'),
        'candidateDimensions4096': candidate_size == [4096,4096],
        'candidateDimensionsMatchAssemblyAndSelection': candidate_size == assembly['dimensions'] == selected_candidate.get('dimensions'),
        'complete16UniqueCores': len(core_checks)==16 and len({p['id'] for p in core_checks})==16,
        'complete4x4Grid': len(grid)==4 and all(len(row)==4 for row in grid),
        'selectedGridMatchesCurrentSelection': grid == selected_candidate.get('selectedCores'),
        'entireCandidateRgbExactlyReconstructed': candidate.tobytes() == reconstructed.tobytes(),
        'resizedFinalPixelsFalse': assembly['resizedFinalPixels'] is False,
        'formalAcceptedRemainsFalse': assembly['formalAccepted'] is False and selected_candidate.get('formalAccepted') is False and qa['formalAccepted'] is False,
        'allCoreChecksPassed': all(c['passed'] for c in core_checks),
    }
    failed = [name for name,ok in tile_checks.items() if not ok]
    if failed:
        problems.append({'tileId':tile,'failedChecks':failed})
    tiles.append({'tileId':tile, 'file':candidate_path.as_posix(), 'fileBytes':candidate_path.stat().st_size,
        'sha256':candidate_sha,'dimensions':candidate_size,'mode':candidate_mode,
        'assemblyRecord':assembly_path.as_posix(),'assemblyRecordSha256':sha(assembly_path),
        'method':assembly['method'], 'nativeInputDimensions':[1254,1254],
        'coreDimensions':[1024,1024], 'resizedFinalPixels':False,'formalAccepted':False,
        'metadataStatusAtCreation':assembly['status'], 'selectedCores':grid,
        'candidateRgbPixelSha256':phash(candidate),'reconstructedRgbPixelSha256':phash(reconstructed),
        'qaReport':qa_path.as_posix(),'qaReportSha256':sha(qa_path),'qaStatus':qa['status'],
        'qaSourceManifest':qa_manifest_path.as_posix() if qa_manifest_path else None,
        'qaSourceManifestSha256':sha(qa_manifest_path) if qa_manifest_path else None,
        'qaSummary':qa.get('summary'), 'qaVisualReviewRepeated':False,
        'checks':tile_checks,'coreChecks':core_checks,'passed':not failed})

missing = []
covered_by_tile = {}
for tile in ORDER:
    covered_by_tile[tile] = 0
    for r in range(4,0,-1):
        for col in range(1,5):
            ident = f'{tile}_p{r:02}_{col:02}'
            if latest(ident):
                covered_by_tile[tile] += 1
            else:
                missing.append(ident)

report = {
    'auditType':'candidate_delivery_integrity_and_index_requirements',
    'auditStartedAtUtc':started, 'auditCompletedAtUtc':datetime.now(timezone.utc).isoformat(),
    'scope':{'productionRoot':B.as_posix(),'assignment':ORDER,
        'writesRestrictedTo':OUT.as_posix(), 'existingFilesModified':False,
        'imagesGenerated':False,'visualQaRepeated':False,'gitOperationsPerformed':False,
        'uploadOperationsPerformed':False,'historicalFreezeFilesModified':False,
        'originalGeneratedSourcePathsReopened':False},
    'summary':{'candidateTilesAudited':len(tiles),'nativeCoresAudited':sum(len(t['coreChecks']) for t in tiles),
        'allAuditedCandidatesPassed':not problems,'failureCount':len(problems),
        'formalAcceptedCount':0,'productionAll4Complete':len(tiles)==4 and not missing,
        'nativeInputResolution':[1254,1254],'deliverableResolution':[4096,4096],
        'resolutionClaim':'4096x4096 assembled from sixteen exact unscaled 1024 cores cropped from measured 1254 native inputs; not native 4K generation',
        'actualImageModel':'unknown','actualImageQuality':'unknown'},
    'scriptRecords':script_records,
    'selectionSnapshot':{'file':selection_path.as_posix(),'sha256Before':selection_hash_before,
        'sha256After':sha(selection_path),'changedDuringAudit':sha(selection_path)!=selection_hash_before,
        'updatedAtUtc':selection['updatedAtUtc']},
    'liveProductionSnapshot':{'progressUpdatedAtUtc':progress.get('updatedAtUtc'),
        'progressStatus':progress.get('status'),'resumeUpdatedAtUtc':resume.get('updatedAtUtc'),
        'resumeStatus':resume.get('status'),'currentPatchInProgress':progress.get('currentPatch'),
        'currentPatchInResume':resume.get('currentPatch'),
        'completedCandidateTileIds':[t['tileId'] for t in tiles],
        'coveredCoresByTileFromFilesystem':covered_by_tile,'coveredCoreCountFromFilesystem':64-len(missing),
        'remainingCoreCountFromFilesystem':len(missing),'remainingCoordinatesFromFilesystem':missing,
        'rawNativePngCountIncludingSupersededVersions':len(list((B/'native').glob('*.png'))),
        'snapshotCanBecomeStaleWhileOtherAgentProduces':True},
    'tiles':tiles,'problems':problems,
    'deliveryIndexRequirements':{
        'topLevelFields':['schemaVersion','createdAtUtc','productionRoot','assignment','regionWorldBox',
            'candidateTileCount','coveredCoreCount','remainingCoreCount','productionComplete','formalAcceptedCount',
            'builtinOnly','paidApiAllowed','actualImageModel','actualImageQuality','resolutionClaim',
            'tiles','regionSeamQa','pendingExternalEdges','auditReports','uploadState','gitState'],
        'perTileFields':['tileId','file','relativeFile','sha256','fileBytes','dimensions','mode','tileWorldBox',
            'assemblyRecord','assemblyRecordSha256','method','nativeInputDimensions','coreDimensions',
            'selectedCores','sources','resizedFinalPixels','qaReports','qaStatus','formalAccepted'],
        'perSourceFields':['id','file','relativeFile','sha256','dimensions','generationRecord',
            'generationRecordSha256','sourceCrop','pasteAt','prompt','promptSha256','receipt',
            'receiptSha256','actualModel','actualQuality','resizedAfterGeneration'],
        'regionWorldBox':[49152,0,57344,8192],
        'tileWorldBoxes':{'r01_c13':[49152,0,53248,4096],'r01_c14':[53248,0,57344,4096],
            'r02_c13':[49152,4096,53248,8192],'r02_c14':[53248,4096,57344,8192]},
        'truthfulFlags':{'formalAcceptedCount':0,'formalAccepted':False,'builtinOnly':True,
            'paidApiAllowed':False,'native4k':False,'actualImageModel':'unknown','actualImageQuality':'unknown'},
        'pendingExternalEdges':[{'tileId':'r01_c13','side':'west','adjacentTile':'r01_c12','status':'neighbor_unavailable_not_reviewed'},
            {'tileId':'r02_c13','side':'west','adjacentTile':'r02_c12','status':'neighbor_unavailable_not_reviewed'}],
        'outOfScopeExternalActions':{'upload':'other window responsible; record as not performed by this audit',
            'git':'other window responsible; record as not performed by this audit'},
    },
    'stateUpdateFindings':[
        'coast_work.assemble uses latest native version per coordinate. Before assembling r01_c14, reconcile all 16 latest selections with the accepted QA selected hashes; latest existing does not by itself mean visually accepted.',
        'coast_work.assemble asserts the destination PNG does not already exist. Do not rerun assemble on an existing candidate or delete it. If selection changes later, preserve existing files and assemble under a new explicitly versioned candidate path using the same exact crop operation.',
        'resume_progress_20261012.refresh writes current-selection, progress and production-resume. It records raw PNG count separately from covered core count; raw count includes superseded variants and must not be presented as selected core count.',
        'refresh unconditionally writes status=active_builtin_production and nextStep=Continue next missing native patch and pending seam checks even when missing is empty. After final refresh, set a truthful completion status and nextStep in live records; do not call refresh again unless resetting those final fields afterwards.',
        'refresh does not clear currentPatch and propagates it from progress into production-resume. Clear currentPatch/currentTile/nextMissingCore after all four are complete; inFlightRequestCount must be zero.',
        'refresh carries internalFullyReviewedTiles/internalReviewPending from progress without deriving them from QA. Set all four reviewed only after final r01_c14 QA; pending list should then be empty.',
        'generationRecord.status=candidate_unreviewed and assembly.status=candidate_awaiting_full_review are creation-time provenance fields. Preserve those records and carry later QA status in the new delivery index.',
        'r02_c14 older final QA north edge pending is superseded for those source hashes by r01_c14-row4-review.json: four south edge segments passed. Merge newer evidence in the delivery index without rewriting historical QA.',
        'r01_c13 older final QA east edge pending is partially superseded by r01_c14-row4-review.json (one west segment passed). Final r01_c14 report must cover all four west segments and current source hashes.',
        'r02_c13 historical final QA pending north/east requires evidence merging from r01_c13 current-final review (four south segments) and r02_c14 final review (four west segments). West c12 remains unavailable.',
        'Production of the requested four-tile region can be complete while formal map acceptance remains false due to missing c12 west sources. Do not conflate region production completion, QA completion, upload, Git, and formal acceptance.',
    ],
    'whenR01C14Finishes':[
        'Finish and QA all 16 selected r01_c14 native inputs, 24 internal seams, 9 internal crossings, four south joins against r02_c14, four west joins against r01_c13, and the 2x2 center crossing. Reuse existing passed evidence only when source hashes match.',
        'Assemble the not-yet-existing r01_c14.4096-candidate.png with coast_work.assemble and its assembly record; keep exact crop [115,115,1139,1139] and 1024-grid paste without resize.',
        'Run this script with --r01-c14-final-review <final QA JSON path inside B> to mechanically audit all four candidates. Without this option, the r01_c14 QA path initially points at incremental row4 QA and cannot certify all 16 final selected source hashes.',
        'Run resume_progress_20261012.refresh once all selected sources and assembly records are final. Expect candidate count=4, covered cores=64, remaining cores=0, remainingCoordinates=[], nextMissingCore=null, and all candidate formalAccepted=false.',
        'Then update only current live records with productionComplete=true, status=completed_region_candidates_pending_formal_external_acceptance, nextStep=Hand off verified four-tile candidate index to the upload/Git window, currentPatch=null, currentTile=null, inFlightRequestCount=0, internalFullyReviewedTiles=all four and internalReviewPending=[]. Keep historical freeze snapshots unchanged.',
        'Create a new delivery index with four candidate hashes, 64 selected source IDs and hashes, all assembly/generation/prompt/receipt references, latest QA reports and their hashes, exact crop/paste geometry, unknown actual model/quality and explicit unavailable west c12 state.',
        'Package the four candidate PNGs plus their assembly records, selected native PNGs and generation records, prompt/receipt provenance, QA reports/source manifests and the index/checksum list. Use relative paths under this production root and retain originals. QA previews are previews only and must not be substituted for candidate/native artwork.',
        'After packaging, verify package entries against the delivery index hashes. Upload/Git actions remain assigned to the other window; record their eventual result only from that window confirmation.',
    ],
}
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
report_path = OUT/f'delivery-integrity-audit-{stamp}.json'
assert not report_path.exists()
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':report_path.as_posix(),'summary':report['summary'],
    'liveProductionSnapshot':report['liveProductionSnapshot'],'problems':problems,
    'selectionChangedDuringAudit':report['selectionSnapshot']['changedDuringAudit']},ensure_ascii=False))
