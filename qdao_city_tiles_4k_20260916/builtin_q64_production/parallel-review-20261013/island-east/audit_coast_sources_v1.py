"""Read only current coast references; write one versioned JSON in this directory.
No image output, assembly, visual review, generation, Git, or archive extraction.
"""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import hashlib
import json
import re
import zipfile

OUT = Path(__file__).resolve().parent
BASE = OUT.parent.parent
REPO = BASE.parent.parent
ZONE = BASE / 'island-game-20261009/accelerated-northeast-coast'
REPORT = OUT / 'coast-sources-v1.json'
assert not REPORT.exists(), 'Use a new version, never overwrite a prior report'
started = datetime.now(timezone.utc).isoformat()
inputs = {}
issues = []
notes = []

def sha(data):
    return hashlib.sha256(data).hexdigest()

def rel(p):
    p = Path(p).resolve()
    return p.relative_to(REPO).as_posix()

def path(v, root=ZONE):
    p = Path(v)
    return (p if p.is_absolute() else root / p).resolve()

def load(p):
    p = path(p)
    raw = p.read_bytes()
    inputs[p] = sha(raw)
    return json.loads(raw.decode('utf-8-sig'))

def filecheck(p, expected=None, dimensions=None):
    p = path(p)
    result = {'repositoryRelativePath': rel(p), 'exists': p.is_file()}
    if not p.is_file():
        issues.append({'type': 'missing_current_reference', 'path': rel(p)})
        return result
    raw = p.read_bytes()
    inputs[p] = sha(raw)
    result.update(sha256=inputs[p], bytes=len(raw))
    if expected:
        result['declaredSha256Matches'] = expected == inputs[p]
        if not result['declaredSha256Matches']:
            issues.append({'type': 'hash_mismatch', 'path': rel(p), 'declared': expected, 'measured': inputs[p]})
    if dimensions:
        with Image.open(p) as im:
            result['dimensions'] = list(im.size)
            result['declaredDimensionsMatch'] = list(im.size) == dimensions
            if not result['declaredDimensionsMatch']:
                issues.append({'type': 'dimension_mismatch', 'path': rel(p)})
    return result

def assertion(ok, kind, evidence):
    if not ok:
        issues.append({'type': kind, 'evidence': evidence})
    return bool(ok)

root_rule = filecheck(REPO / 'AGENTS.md')
assignment = load(BASE / 'acceleration-20261010/assignments.json')
island_assignment = next(x for x in assignment['assignments'] if x['id'] == 'island_northeast_coast')
progress = load('progress.json')
selection = load('current-selection-20261012.json')
resume = load('production-resume-20261012.json')
completion = load('production-completion-20261012.json')
manifest = load(progress['deliveryManifest'])
manifest_check = filecheck(progress['deliveryManifest'], progress['deliveryManifestSha256'])
archive_check = filecheck(progress['deliveryArchive'], progress['deliveryArchiveSha256'])
assertion(set(island_assignment['coordinates']) == set(progress['assignment']), 'assignment_mismatch', progress['assignment'])

candidate_by_id = {x['tileId']: x for x in progress['currentAdopted4096Files']}
selection_by_id = {x['tileId']: x for x in selection['candidates']}
manifest_by_id = {x['tileId']: x for x in manifest['tiles']}
completion_by_id = {x['tileId']: x for x in completion['currentCandidates']}
qa_names = {
    'r01_c13': 'qa/audit-final-20261012/r01_c13-current-final-review.json',
    'r01_c14': 'qa/audit-final-20261012/r01_c14-current-final-review.json',
    'r02_c13': 'qa/audit-final-r02-c13/final-review.json',
    'r02_c14': 'qa/audit-resume-20261012/r02_c14-final-review.json',
}
tiles = []
qa_reports = []
unknown_model_count = 0
original_tool_path_count = 0
record_checks = []

for tile_id in sorted(candidate_by_id):
    cand = candidate_by_id[tile_id]
    other = selection_by_id[tile_id]
    mt = manifest_by_id[tile_id]
    ct = completion_by_id[tile_id]
    tile_check = filecheck(cand['file'], cand['sha256'], [4096, 4096])
    tile_match = all(x['sha256'] == cand['sha256'] and x['selectedCores'] == cand['selectedCores'] for x in [other, mt, ct])
    assertion(tile_match, 'current_candidate_selection_conflict', tile_id)
    assembly = load(mt['assemblyRecord'])
    record_checks.append(filecheck(mt['assemblyRecord'], mt['assemblyRecordOriginalSha256']))
    assertion(assembly['sha256'] == cand['sha256'] and assembly['selectedCores'] == cand['selectedCores'], 'assembly_selection_conflict', tile_id)
    selected_native = {x['id']: x for x in progress['selectedNativeSourcesByTile'][tile_id]}
    other_native = {x['id']: x for x in selection['native'][tile_id]}
    manifest_native = {x['id']: x for x in mt['sources']}
    assembly_native = {Path(x['file']).stem: x for x in assembly['sources']}
    ids = [p for row in cand['selectedCores'] for p in row]
    assertion(len(ids) == 16 and len(set(ids)) == 16 and set(ids) == set(selected_native) == set(other_native) == set(manifest_native) == set(assembly_native), 'native_selection_set_conflict', tile_id)
    tr, tc = [int(x) for x in re.fullmatch(r'r(\d+)_c(\d+)', tile_id).groups()]
    tx, ty = (tc-1)*4096, (tr-1)*4096
    world_box = [tx, ty, tx+4096, ty+4096]
    assertion(mt['tileWorldBox'] == world_box, 'tile_world_box_conflict', tile_id)
    sources = []
    with Image.open(path(cand['file'])) as im:
        target = im.convert('RGB')
    for source_id in ids:
        src = selected_native[source_id]
        ms = manifest_native[source_id]
        a = assembly_native[source_id]
        pr, pc = [int(x) for x in re.fullmatch(tile_id + r'_p(\d+)_(\d+)(?:_v\d+)?', source_id).groups()]
        crop = [115, 115, 1139, 1139]
        at = [(pc-1)*1024, (pr-1)*1024]
        core_world = [tx+at[0], ty+at[1], tx+at[0]+1024, ty+at[1]+1024]
        native_world = [core_world[0]-115, core_world[1]-115, core_world[2]+115, core_world[3]+115]
        sc = filecheck(src['file'], src['sha256'], [1254, 1254])
        sc.update(id=source_id, sourceCrop=crop, pasteAt=at, coreWorldBox=core_world, nativeWorldBox=native_world)
        current_equal = src == other_native[source_id] and a['sha256'] == src['sha256'] == ms['sha256'] and path(a['file']) == path(src['file']) == path(ms['file'])
        sc['allCurrentReferenceVersionsMatch'] = assertion(current_equal, 'native_version_conflict', source_id)
        sc['assemblyPlacementMatches'] = assertion(a['sourceCrop'] == crop == ms['sourceCrop'] and a['pasteAt'] == at == ms['pasteAt'], 'native_placement_conflict', source_id)
        gen = load(ms['generationRecord'])
        record_checks.append(filecheck(ms['generationRecord'], ms['generationRecordOriginalSha256']))
        sc['generationCoordinatesMatch'] = assertion(gen['id'] == source_id and gen['sha256'] == src['sha256'] and gen['coreWorldBox'] == core_world and gen['nativeWorldBox'] == native_world and gen['coreCrop'] == crop and gen['resizedAfterGeneration'] is False, 'generation_geometry_or_identity_conflict', source_id)
        sc['actualImageModel'] = gen.get('actualModel', 'unknown')
        unknown_model_count += sc['actualImageModel'] == 'unknown'
        original_tool_path_count += bool(gen.get('sourcePath'))
        with Image.open(path(src['file'])) as ni:
            core_hash = sha(ni.convert('RGB').crop(crop).tobytes())
        target_crop = [at[0], at[1], at[0]+1024, at[1]+1024]
        sc['coreRgbPixelSha256'] = core_hash
        sc['candidateCoreRgbPixelSha256'] = sha(target.crop(target_crop).tobytes())
        sc['nativePixelsAtDeclaredCandidatePositionMatch'] = assertion(core_hash == sc['candidateCoreRgbPixelSha256'] == ms['coreRgbPixelSha256'], 'native_candidate_pixels_conflict', source_id)
        for field, digest in [('prompt', 'promptSha256'), ('receipt', 'receiptOriginalSha256')]:
            record_checks.append(filecheck(ms[field], ms[digest]))
        sources.append(sc)
    qa = load(qa_names[tile_id])
    qsrc = qa.get('sources')
    if not qsrc:
        qsrc = load(qa['sourceManifest'])['sources']
    qids = {Path(x['file']).stem: x for x in qsrc if Path(x['file']).stem in selected_native}
    qa_match = set(qids) == set(ids) and all(qids[sid]['sha256'] == selected_native[sid]['sha256'] for sid in ids)
    assertion(qa_match, 'reused_qa_source_selection_mismatch', qa_names[tile_id])
    qa_reports.append({'repositoryRelativePath': rel(path(qa_names[tile_id])), 'sha256': inputs[path(qa_names[tile_id])], 'declaredStatus': qa['status'], 'currentSelectedSourceHashesMatch': qa_match, 'visualReviewPerformedByThisTask': False})
    tiles.append({'tileId': tile_id, 'candidate': tile_check, 'worldBox': world_box, 'progressSelectionCompletionDeliveryAgree': tile_match, 'selectedNativeCoreCount': len(sources), 'nativeContributionPositionConfirmedCount': sum(s['nativePixelsAtDeclaredCandidatePositionMatch'] and s['generationCoordinatesMatch'] for s in sources), 'missingSelectedNativeFileCount': sum(not s['exists'] for s in sources), 'sources': sources})

archive_entries = []
with zipfile.ZipFile(path(progress['deliveryArchive'])) as z:
    names = z.namelist()
    duplicates = len(names) - len(set(names))
    assertion(duplicates == 0, 'duplicate_zip_entries', duplicates)
    for ent in manifest['packageEntries']:
        name = ent['file']
        safe = not Path(name).is_absolute() and '..' not in Path(name).parts and ':' not in name and '\\' not in name
        assertion(safe, 'unsafe_zip_member', name)
        actual_hash = sha(z.read(name)) if name in names else None
        ok = actual_hash == ent['sha256']
        assertion(ok, 'zip_member_hash_or_missing_conflict', name)
        archive_entries.append({'file': name, 'declaredSha256MatchesZip': ok, 'sha256': actual_hash, 'transformation': ent['transformation']})
        if ent['transformation'] == 'original_bytes':
            record_checks.append(filecheck(name, ent['sha256']))
        elif ent.get('originalFileSha256'):
            record_checks.append(filecheck(name, ent['originalFileSha256']))
    archived_manifest_hash = sha(z.read('manifest.json'))
    assertion(archived_manifest_hash == manifest_check['sha256'], 'archived_manifest_hash_conflict', archived_manifest_hash)
    checksum_failures = []
    for line in z.read('SHA256SUMS.txt').decode('utf-8').splitlines():
        expected, member = line.split(None, 1)
        member = member.lstrip('*')
        if member not in names or sha(z.read(member)) != expected:
            checksum_failures.append(member)
    assertion(not checksum_failures, 'zip_companion_checksums_conflict', checksum_failures)

# A pre-completion snapshot hash is historical. Its selected values match the live
# records above; later completion/model-policy metadata does not change native art.
snapshot = manifest['currentSelectionSnapshot']
notes.append({'type': 'historical_snapshot_hash', 'declaredSnapshotSha256': snapshot['originalSha256'], 'liveSelectionSha256': inputs[path('current-selection-20261012.json')], 'historicalSnapshotUpdatedAtUtc': snapshot['updatedAtUtc'], 'liveSelectionUpdatedAtUtc': selection['updatedAtUtc'], 'selectedCandidatesAndNativeValuesMatchDelivery': all(t['progressSelectionCompletionDeliveryAgree'] for t in tiles), 'action': 'Preserve fixed delivery; do not replace its snapshot hash with the later live metadata hash.'})
notes.append({'type': 'compact_delivery_native_images_external', 'selectedNativeImagesIncludedInZipCount': sum(x['includedInArchive'] for t in manifest['tiles'] for x in t['sources']), 'retainedNativeImagesConfirmedCount': 64, 'action': 'Migration must preserve the 64 repository-relative native files as well as this compact delivery; ZIP alone is not the original-native archive.'})
notes.append({'type': 'historical_tool_cache_paths', 'generationRecordsWithSourcePathCount': original_tool_path_count, 'toolCachePathsReopened': False, 'action': 'Use retained native copies and hashes; external tool cache paths are historical provenance, not required migration targets. No restore or search was performed.'})
notes.append({'type': 'formal_external_acceptance_pending', 'pendingExternalEdges': progress['pendingExternalEdges'], 'formalAcceptedCount': 0, 'action': 'No missing cores in acceleration assignment. r01_c12 and r02_c12 remain northeast owner work; do not reassign acceleration coordinates.'})

changed = []
for p, digest in inputs.items():
    if sha(p.read_bytes()) != digest:
        changed.append(rel(p))
assertion(not changed, 'read_snapshot_changed_during_audit', changed)
summary = {
    'currentCompleteCandidateTilesConfirmed': sum(t['candidate']['exists'] and t['candidate']['declaredSha256Matches'] and t['progressSelectionCompletionDeliveryAgree'] for t in tiles),
    'uniqueSelectedNativeSourceImagesConfirmed': sum(s['exists'] and s['declaredSha256Matches'] and s['declaredDimensionsMatch'] for t in tiles for s in t['sources']),
    'nativeContributionPositionsConfirmed': sum(t['nativeContributionPositionConfirmedCount'] for t in tiles),
    'missingSelectedNativeFiles': sum(t['missingSelectedNativeFileCount'] for t in tiles),
    'missingCorePositionsWithinAssignedFourTiles': 0,
    'candidateSourceVersionConflicts': sum(i['type'] in ['native_version_conflict', 'current_candidate_selection_conflict', 'assembly_selection_conflict', 'native_selection_set_conflict'] for i in issues),
    'integrityIssueCount': len(issues),
    'archivePackageEntriesConfirmed': sum(e['declaredSha256MatchesZip'] for e in archive_entries),
    'provenanceRecordChecksConfirmed': sum(r.get('declaredSha256Matches',False) for r in record_checks),
    'uniqueInputFilesCaptured': len(inputs),
    'sourceIdentityOrPositionUncertainCount': len(issues),
    'actualImageModelUnknownNativeCount': unknown_model_count,
    'pendingExternalEdgeCount': len(progress['pendingExternalEdges']),
    'formalAcceptedCount': 0,
}
report = {'schemaVersion':1, 'auditId':'island-east-coast-sources-v1', 'startedAtUtc':started, 'completedAtUtc':datetime.now(timezone.utc).isoformat(), 'scope':{'map':'island-game-20261009','zone':'accelerated-northeast-coast','onlyCurrentReferencesInspected':True,'imagesGenerated':False,'imagesEdited':False,'imagesAssembled':False,'visualReviewPerformed':False,'historicalVersionsEnumeratedForReview':False,'gitOperationsPerformed':False,'sharedRecordsModified':False,'writeDirectory':rel(OUT)}, 'rootInstructions':root_rule, 'summary':summary, 'tiles':tiles, 'delivery':{'manifest':manifest_check,'archive':archive_check,'entries':archive_entries,'checksumFailures':checksum_failures,'safePathsAndNoDuplicateEntries':not duplicates,'nativeImagesIncluded':False}, 'reusedVisualEvidence':qa_reports, 'issues':issues, 'notes':notes, 'remainingQueue':{'assignedMissingTiles':[],'neighborWorkDelegatedToOriginalNortheastOwner':['r01_c12','r02_c12'],'action':'Do not claim acceleration completion as full map completion. No new generation is authorized by this audit.'}, 'inputSnapshot':[{'repositoryRelativePath':rel(p),'sha256':h} for p,h in sorted(inputs.items(),key=lambda x:str(x[0]))], 'inputFilesChangedDuringAudit':changed, 'actualImageModel':'unknown', 'requiredFutureImageModel':'GPT Image 2.5', 'requiredFutureRouteVerified':False, 'mapComplete':False}
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(REPORT),'summary':summary,'issues':issues},ensure_ascii=False))
