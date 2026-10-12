from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re, shutil

ZONE = Path(__file__).resolve().parent
ROOT = Path('D:/work/image')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.freeze-tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(p)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
stamp = datetime.now(timezone.utc).isoformat()
freeze = read(ZONE / 'migration-freeze-20261011.json')
records = [read(p) for p in sorted((ZONE / 'native').glob('*.png.generation.json'))]
by_id = {r['id']: r for r in records}
known = {r['sha256'] for r in records}
local_hash_issues = []
original_copies = []
source_dirs = set()
refs = {}
def collect_refs(value):
    if isinstance(value, dict):
        file = value.get('file')
        if isinstance(file, str) and re.match(r'^[A-Za-z]:[/\\]', file):
            p = Path(file)
            if not p.is_relative_to(ZONE): refs[str(p)] = {'file': str(p), 'sha256': value.get('sha256'), 'role': value.get('role'), 'exists': p.exists(), 'outsideWorkspace': not p.is_relative_to(ROOT)}
        for v in value.values(): collect_refs(v)
    elif isinstance(value, list):
        for v in value: collect_refs(v)
for r in records:
    p = Path(r['file'])
    actual = sha(p) if p.exists() else None
    if actual != r['sha256']: local_hash_issues.append({'id': r['id'], 'file': str(p), 'expected': r['sha256'], 'actual': actual})
    source = r.get('evidence', {}).get('originalToolPath')
    if source:
        source_path = Path(source)
        if source_path.parent.exists(): source_dirs.add(source_path.parent)
        original_copies.append({'originalToolPath': source, 'projectCopy': str(p), 'sha256': r['sha256'], 'projectCopyHashMatches': actual == r['sha256']})
    collect_refs(r.get('references', []))
unknown = []
audited_dirs = []
for folder in sorted(source_dirs):
    files = sorted(folder.glob('*.png'), key=lambda p: p.stat().st_mtime, reverse=True)[:12]
    audited_dirs.append({'directory': str(folder), 'recentFilesChecked': len(files)})
    for p in files:
        digest = sha(p)
        if digest not in known: unknown.append({'file': str(p), 'sha256': digest})
audit = {'savedAtUtc': stamp, 'scope': 'All registered local native hashes and latest 12 PNGs in each original-output directory evidenced by this zone generation records; no image QA.', 'registeredNativeCount': len(records), 'localHashIssues': local_hash_issues, 'directories': audited_dirs, 'unregisteredRecentOutputPaths': unknown, 'originalToProjectCopies': original_copies, 'referencesOutsideZone': list(refs.values())}
audit_path = ZONE / 'qa/migration-unsaved-output-audit-20261011.json'
write(audit_path, audit)
workers = {}
for name in ('repair', 'southeast', 'west'):
    p = ZONE / 'qa' / ('migration-freeze-' + name + '-worker-20261011.json')
    workers[name] = {'checkpoint': str(p), 'checkpointPresent': p.exists(), 'inFlightImagegen': 0, 'reportedUnsavedSuccessfulOutputs': [], 'state': 'worker_reported_stopped'}
    if p.exists():
        data = read(p)
        workers[name]['snapshot'] = data
        workers[name]['checkpointSha256'] = sha(p)
selections = {p.stem[10:]: read(p) for p in sorted(ZONE.glob('selection-r??_c??.json'))}
bases = {re.sub(r'_v\d+$', '', r['id']) for r in records if re.fullmatch(r'r\d{2}_c\d{2}_p\d{2}_\d{2}(?:_v\d+)?', r['id'])}
excluded = {'r01_c13', 'r01_c14', 'r02_c13', 'r02_c14'}
inventory = []
full = []
passed = []
candidates = []
selected_count = 0
for tr in range(1, 8):
    for tc in range(8, 15):
        tid = f'r{tr:02d}_c{tc:02d}'
        if tid in excluded: continue
        s = selections.get(tid, {'cores': [[None]*4 for _ in range(4)]})
        ids = [v for row in s['cores'] for v in row if v]
        selected_count += len(ids)
        chosen = {re.sub(r'_v\d+$', '', v) for v in ids}
        coords = [f'{tid}_p{r:02d}_{c:02d}' for r in range(1, 5) for c in range(1, 5)]
        dp = ZONE / 'tiles' / (tid + '.png.derivation.json')
        d = read(dp) if dp.exists() else {}
        covered = len(ids) == 16 and dp.exists()
        internal = covered and str(d.get('internalReview', '')).startswith('passed')
        if covered:
            full.append(tid)
            image = ZONE / 'tiles' / (tid + '.png')
            digest = sha(image)
            candidates.append({'tileId': tid, 'path': str(image), 'sha256': digest, 'derivationHashMatches': digest == d.get('sha256'), 'internalReview': d.get('internalReview'), 'formalAccepted': False})
        if internal: passed.append(tid)
        inventory.append({'tileId': tid, 'selectedCoreCount': len(ids), 'selectedCoreIds': ids, 'selectedCandidatePaths': [by_id[i]['file'] for i in ids], 'completeNativeCoverage': covered, 'internalPassed': internal, 'formalAccepted': False, 'missingGeneratedCoordinates': [c for c in coords if c not in bases], 'unselectedCoordinates': [c for c in coords if c not in chosen], 'pendingIssues': s.get('pendingIssues', []) + s.get('pendingNativeRepairs', [])})
summary = {'ownedTileCount': 45, 'targetCoreCoordinates': 720, 'generatedNativeFiles': len(records), 'uniqueGeneratedCoreCoordinates': len(bases), 'selectedCoreCoordinates': selected_count, 'missingGeneratedCoreCoordinates': 720-len(bases), 'missingSelectedCoreCoordinates': 720-selected_count, 'fullCoverageTiles': len(full), 'internallyPassedTiles': len(passed), 'formalAcceptedTiles': 0, 'excludedElsewhere': sorted(excluded)}
inventory_path = ZONE / 'qa/migration-inventory-20261011.json'
write(inventory_path, {'savedAtUtc': stamp, **summary, 'tileInventory': inventory})
freeze.update(savedAtUtc=stamp, status='frozen_for_migration', workers=workers, currentTileCandidates=candidates, selectedCandidatePaths=[c['path'] for c in candidates], coverage=summary, inventory=str(inventory_path), localProvenanceAudit=str(audit_path), unsavedOutputAuditStatus='registered native copies verified; recent output audit recorded; worker runtime reports zero unsaved', unsavedSuccessfulOutputPaths=[], unregisteredRecentOutputPaths=unknown, externalReferencePaths=[r for r in refs.values() if r['outsideWorkspace']], workspaceReferencesOutsideZone=[r for r in refs.values() if not r['outsideWorkspace']], externalReferenceAuditStatus='generation-record reference paths inventoried; outside-workspace original output copies documented in provenance audit', originalToolOutputsAlreadyCopiedToWorkspace=len(original_copies), localHashIssues=local_hash_issues, pendingRepairs=freeze['pendingRepairs'] + ['Formal outer boundary acceptance remains pending; all current tiles are candidates.'], metadataOnlyFinalization=True)
if unknown or local_hash_issues or not all(w['checkpointPresent'] for w in workers.values()):
    freeze['status'] = 'frozen_for_migration_archive_audit_pending'
history = ZONE / 'qa/history/migration-pre-freeze-20261011'
for filename in ('progress.json', 'handoff.json', 'continuation-round-20261011.json'):
    path = ZONE / filename
    backup = history / filename
    if not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
    data = read(path)
    data.update(status='frozen_for_migration', updatedAtUtc=stamp, generationStopped=True, inFlightImagegen=0, inFlightStatus='stopped: zero requests in flight; migration hold', migrationCheckpoint=str(ZONE / 'migration-freeze-20261011.json'), continuationInventory=str(inventory_path), generatedNativeCount=len(records), generatedCoreCoordinateCount=len(bases), selectedCoreCoordinateCount=selected_count, fullyCovered4kCount=len(full), internalPassed4kCount=len(passed), complete4kCount=len(passed), formalAcceptedCount=0, missingFullCoverage4kCount=45-len(full), currentTile=None, currentPatch=None, activeTiles=[], pausedIncompleteTiles=[t['tileId'] for t in inventory if 0<t['selectedCoreCount']<16], nextStep='Resume only after migration hold is released; use migration checkpoint and worker breakpoints.', nextAction='Preserve all files for migration; no new artwork generation or QA.')
    data.update(generatedNativeFiles=len(records), generatedCoreCoordinates=len(bases), selectedCoreCoordinates=selected_count, completeNativeCoverageTiles=len(full), internalPassedTiles=passed, formalAcceptedTiles=0, missingFullCoverageTiles=45-len(full), currentCoordinate=None, inventory=str(inventory_path), tileSummary={t['tileId']: {'coreCoverage': t['selectedCoreCount'], 'missingCores': 16-t['selectedCoreCount'], 'internalPassed': t['internalPassed'], 'pendingIssues': t['pendingIssues']} for t in inventory}, finishedInternalCandidates=['tiles/'+t+'.png' for t in passed], pixelCoveredCandidates=['tiles/'+t+'.png' for t in full])
    data.pop('nextSteps', None)
    write(path, data)
write(ZONE / 'migration-freeze-20261011.json', freeze)
print(json.dumps({'status': freeze['status'], 'coverage': summary, 'unknownRecentOutputs': unknown, 'hashIssues': local_hash_issues, 'workerCheckpointsPresent': {k:v['checkpointPresent'] for k,v in workers.items()}, 'externalReferencePaths': freeze['externalReferencePaths'], 'candidatesHashMatches': all(c['derivationHashMatches'] for c in candidates)}, ensure_ascii=False))
