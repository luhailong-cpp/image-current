"""Record the inspected cap append; never alter source or candidate pixels."""
from pathlib import Path
import json, hashlib
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
TILE = HERE.parents[1]
ZONE = TILE.parent

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

recipe_path = HERE/'replay.json'
recipe = read(recipe_path)
verification = read(HERE/'verification.json')
candidate = Path(recipe['output'])
assert sha(candidate) == recipe['outputSha256'] == verification['outputSha256']
assert verification['pixelReplayIdentical'] and verification['outsideMaskPixelIdentical']
assert sha(recipe['source']) == recipe['sourceSha256']
assert sha(recipe['mask']) == recipe['maskSha256']
assert sha(recipe['sourceGenerationRecord']['file']) == recipe['sourceGenerationRecord']['sha256']
review_path = HERE/'visual-review.json'
review = {
    'tile': 'r06_c13',
    'scope': 'One existing r07_c13 p14 gold cap halo appended to north neighbor only.',
    'status': 'source replay and actual 1:1 shared cap review passed; not formal acceptance',
    'oldCandidateSha256': recipe['prefixImageSha256'],
    'newCandidateSha256': recipe['outputSha256'],
    'source': recipe['source'],
    'sourceSha256': recipe['sourceSha256'],
    'mask': recipe['mask'],
    'maskSha256': recipe['maskSha256'],
    'sourceGenerationRecordUnchanged': True,
    'sourceNativeUnchanged': True,
    'changedPixelBox': recipe['changedPixelBox'],
    'changedPixelCount': recipe['changedPixelCount'],
    'outsideMaskPixelIdentical': True,
    'binaryMask': True,
    'sourceResized': False,
    'imageBlur': False,
    'geometricWarp': False,
    'feathering': False,
    'replayVerification': {'file': str(HERE/'verification.json'), 'sha256': sha(HERE/'verification.json')},
    'sourceReplay': str(HERE/'apply.py'),
    'nativeCoreCount': 16,
    'priorRepairLayerCount': 6,
    'newRepairLayerCount': 1,
    'pixelReplayIdentical': True,
    'visualEvidence': {'file': str(HERE/'after-shared-cap-1to1.png'), 'sha256': sha(HERE/'after-shared-cap-1to1.png'), 'scale': '1:1 original pixels'},
    'visualFinding': 'The rounded gold cap joins the same-source p14 core across the horizontal tile boundary. Its curved left and right silhouette has no rectangular crop edge. Stone, blue ribs and the adjacent gold rail remain continuous around the cap.',
    'openP1': 0,
    'openP2': 0,
    'previousInternalReview': str(TILE/'qa/finish-20261010/records/final-visual-review.json'),
    'previousInternalReviewApplicability': 'All previous internal seam windows are outside the changed bottom 19 rows and retain exactly the same pixels. Existing P3 material notes remain.',
    'nextStep': 'Root to regenerate the existing connected 2x2 evidence and update its source snapshot; this record does not assert that external re-export has run.',
    'formalAcceptedCount': 0,
    'actualModel': None,
    'actualQuality': None,
    'reviewedAt': datetime.now(timezone.utc).isoformat(),
}
save(review_path, review)
recipe['status'] = 'one binary cap appended; full source replay and actual 1:1 shared cap review passed'
recipe['visualReview'] = {'file': str(review_path), 'sha256': sha(review_path)}
save(recipe_path, recipe)
side_path = Path(str(candidate)+'.generation.json')
side = read(side_path)
side.update({'recipeSha256': sha(recipe_path), 'pixelReplayVerified': True, 'appendedRepairReview': str(review_path), 'appendedRepairReviewSha256': sha(review_path), 'pixelReplayVerification': {'file': str(HERE/'verification.json'), 'sha256': sha(HERE/'verification.json')}})
save(side_path, side)
progress_path = TILE/'tile-progress.json'
progress = read(progress_path)
progress.update({'updatedAt': datetime.now(timezone.utc).isoformat(), 'additionalBoundaryReview': str(review_path), 'additionalBoundaryReviewSha256': sha(review_path), 'pixelReplayVerified': True})
save(progress_path, progress)
row_path = ZONE/'r07_c13/qa/row1-final/visual-review.json'
row = read(row_path)
assert len(row['openP2']) == 1 and row['openP2'][0]['id'] == 'p14-north-cap-crop'
resolved = row.pop('openP2')
resolved[0]['solution'] = 'Applied the exact p14 cap with a binary object mask into r06_c13 bottom edge; original p14 native unchanged.'
resolved[0]['integrationReview'] = str(review_path)
resolved[0]['northCandidateSha256'] = recipe['outputSha256']
row.update({'openP2': [], 'resolvedP2': resolved, 'status': 'four native patches complete; north gold cap integrated and reviewed at 1:1'})
save(row_path, row)
worker_path = ZONE/'r07_c13/worker-row1.json'
worker = read(worker_path)
worker.update({'pendingParentIntegration': None, 'completedBoundaryIntegration': {'review': str(review_path), 'northCandidateSha256': recipe['outputSha256'], 'nativeP14Unchanged': True}, 'updatedAt': datetime.now(timezone.utc).isoformat()})
save(worker_path, worker)
assert sha(recipe['source']) == recipe['sourceSha256']
assert sha(candidate) == recipe['outputSha256']
assert read(side_path)['recipeSha256'] == sha(recipe_path)
print(json.dumps({'candidateSha256': sha(candidate), 'review': str(review_path), 'row1OpenP2': len(row['openP2']), 'outsideMaskPixelIdentical': True, 'changedPixelCount': recipe['changedPixelCount']}, ensure_ascii=False))
