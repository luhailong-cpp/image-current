from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re, shutil

ZONE = Path(__file__).resolve().parent
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.freeze-tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)
stamp = datetime.now(timezone.utc).isoformat()
selections = {p.stem[10:]: read(p) for p in sorted(ZONE.glob('selection-r??_c??.json'))}
tiles = []
for tid, selection in selections.items():
    deriv = ZONE / 'tiles' / (tid + '.png.derivation.json')
    if deriv.exists():
        data = read(deriv)
        tiles.append({'tileId': tid, 'path': str(ZONE / 'tiles' / (tid + '.png')), 'sha256': data.get('sha256'), 'internalReview': data.get('internalReview'), 'formalAccepted': False})
workers = {}
for worker in ('repair', 'southeast', 'west'):
    path = ZONE / 'qa' / ('migration-freeze-' + worker + '-worker-20261011.json')
    workers[worker] = {'inFlightImagegen': 0, 'generationStopped': True, 'source': 'worker runtime acknowledgement in root conversation', 'checkpoint': str(path), 'checkpointPresent': path.exists()}
out = {
    'schemaVersion': 1,
    'requestedAtUtc': '2026-10-12T02:24:00Z',
    'savedAtUtc': stamp,
    'freezeVerifiedAtUtc': stamp,
    'stoppingTimeNote': 'Actual stop was acknowledged before this verification; exact earlier runtime stop timestamps are available in worker checkpoints when recorded.',
    'status': 'frozen_for_migration_final_inventory_pending',
    'generationStopped': True,
    'doNotStartAdditionalGeneration': True,
    'restartArtOnlyAfterMigration': True,
    'inFlightImagegen': 0,
    'rootInFlightImagegen': 0,
    'workers': workers,
    'activeCoordinates': ['r03_c10', 'r04_c11', 'r05_c12', 'r05_c14'],
    'selectedCandidatePaths': [t['path'] for t in tiles],
    'currentTileCandidates': tiles,
    'selectionIndexes': [str(ZONE / ('selection-' + tid + '.json')) for tid in selections],
    'lastRootSavedCandidate': {'id': 'r03_c10_p02_04_v2', 'path': str(ZONE / 'native/r03_c10_p02_04_v2.png'), 'sha256': '23719d0d8cb30456909e365a11feca0e210916ab962a76de72e8e670042ae1a9', 'status': 'saved_unreviewed_unselected'},
    'nextMissingCoordinate': 'r03_c10_p03_04 after reviewing saved p02_04_v2; other worker coordinates in checkpoints',
    'pendingRepairs': ['r05_c12 p03_02/p04_02 stair junction', 'r03_c10 p02_04_v2 pending review', 'r04_c11 p03_03 pending selection', 'r05_c14 p02_01_v2 pending selection'],
    'unsavedSuccessfulOutputPaths': [],
    'unsavedOutputAuditStatus': 'workers report none; final local provenance comparison pending',
    'externalReferencePaths': [],
    'externalReferenceAuditStatus': 'pending final local metadata inventory',
    'deliveryIndex': str(ZONE / 'exports/20261011-local-v2/delivery-index.json'),
    'preserveAllOriginalsIntermediatesAndPreviews': True,
    'gitOwnerThreadId': '01a11b5e-158a-77d0-8c02-e8e503b7abe4',
    'gitActionsByThisZoneWorker': False,
    'allOwnedTilesComplete': False,
    'actualModel': None, 'actualQuality': None, 'submittedModel': None, 'submittedQuality': None
}
write(ZONE / 'migration-freeze-20261011.json', out)
print(json.dumps({'checkpoint': str(ZONE / 'migration-freeze-20261011.json'), 'inFlight': 0, 'workerCheckpoints': workers, 'candidates': len(tiles)}, ensure_ascii=False))
