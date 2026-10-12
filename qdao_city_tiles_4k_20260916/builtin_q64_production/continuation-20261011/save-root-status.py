from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image

base = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
outdir = base / 'continuation-20261011'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

inventory = read(outdir / 'delivery-inventory.json')
evidence = []
for rel in [
    'main-city-game-20261009/northwest/continuation-round-20261011.json',
    'main-city-game-20261009/southeast/r15_c13/continuation-round-20261011.json',
]:
    record = read(base / rel)
    output = record.get('firstActualNewOutput') or record.get('firstNewOutputThisRound')
    path = Path(output.get('file') or output['path'])
    actual_hash = hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()
    with Image.open(path) as image:
        dimensions = list(image.size)
    evidence.append({
        'sourceRecord': str(base / rel), 'sourceStatus': record['status'],
        'path': str(path), 'dimensions': dimensions, 'sha256': actual_hash,
        'recordedHashMatches': actual_hash == output['sha256'],
        'countsAsComplete4096Tile': False,
        'visualAcceptance': record.get('currentPatchQA', record.get('QA')),
    })

review_path = base / 'island-game-20261009/southwest/root-review-20261011/review.json'
review = read(review_path)
status = {
    'schemaVersion': 1,
    'snapshotAtUtc': datetime.now(timezone.utc).isoformat(),
    'wholeMapsComplete': False,
    'workStatus': 'Continuation dispatched to 15 existing production chats; actual new native files verified in two main-city areas; candidate completion unchanged by these partial outputs.',
    'dispatchRecord': str(outdir / 'resume-dispatch.json'),
    'candidateInventory': {
        'source': str(outdir / 'delivery-inventory.json'),
        'asOf': inventory['createdAtUtc'],
        'totals': inventory['totals'],
        'mapSummary': inventory['mapSummary'],
        'caveat': 'Candidate-file inventory only, not formal visual acceptance or complete-map delivery. Seven island coordinates have uncertain active revisions. Native partials are not complete 4096 candidates.',
    },
    'actualNewOutputEvidenceVerifiedHere': evidence,
    'independentIslandSouthwestReview': {
        'record': str(review_path), 'decision': review['decision'],
        'candidateCount': review['candidateCount'],
        'internalAndGroupSharedEdgeReviewPassed': review['internalAndGroupSharedEdgeReviewPassed'],
        'formalAcceptanceGranted': False,
        'exteriorJoinsVerified': False,
    },
    'availablePartialPreviews': [
        str(base / 'main-city-game-20261009/northwest/joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/preview-only-1600.png'),
        str(base / 'island-game-20261009/southwest/output/contiguous-r09-r10-c03-c04-v01/preview-2048.png'),
    ],
    'coordinationCorrections': [
        'Fishing village northeast owns 43 tiles after excluding all six jewelry approach coordinates; worker notified.',
        'Fishing village southwest legacy coverage and acceptance totals conflict; worker asked to reconcile using active files.',
        'Jewelry approach error receipt at 09:28:22Z predates this 09:52Z continuation; worker asked to separate historical failure notifications from current requests.',
    ],
    'networkCaveat': 'Successful files show some normal builtin requests are working. This is not a guarantee that every worker route is healthy. No alternate endpoint, permission bypass or paid API was used.',
    'nextWork': 'Existing exclusive owners continue missing native patches, assemble 4096 candidates, and repair actual structural seams. Completed groups remain preserved.',
    'preserveAllArtwork': True,
    'gitMutationsPerformed': False,
    'runtimeWorkIncluded': False,
}
target = outdir / 'root-status.json'
target.write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'file': str(target), 'newNativeFilesVerified': len(evidence), 'allHashesMatch': all(item['recordedHashMatches'] for item in evidence), 'wholeMapsComplete': False}, ensure_ascii=False))
