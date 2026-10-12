"""Record the independently viewed native horizontal strips and inherited hashes."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageChops
import hashlib
import json

BASE = Path(__file__).resolve().parents[1]
RESUME = Path(__file__).resolve().parent
QA = RESUME / 'qa'
OLD_QA = BASE / 'qa' / 'region-seams'
Image.MAX_IMAGE_PIXELS = 200_000_000
read = lambda path: json.loads(Path(path).read_text(encoding='utf-8-sig'))
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
exact = lambda a, b: a.size == b.size and ImageChops.difference(a, b).getbbox() is None
issues = []

historical_records = [OLD_QA / name for name in
                      ['findings.json', 'reviewed-crop-hashes.json', 'review-validity-v2.json']]
historical_hashes_before = {str(path): sha(path) for path in historical_records}
manifest_path = RESUME / 'candidate-manifest.json'
manifest = read(manifest_path)
candidate = manifest['regionCandidate']
candidate_path = Path(candidate['file'])
candidate_sha = sha(candidate_path)
if candidate_sha != candidate['sha256']:
    issues.append('Current region candidate hash differs from the assembly manifest')
region = Image.open(candidate_path).convert('RGB')
if list(region.size) != candidate['dimensions'] or region.size != (8192, 12288):
    issues.append('Current six-tile region candidate dimensions differ')

observations = {
    0: 'Masonry, timber boards, golden upright and diagonal brace continue across the seam without a horizontal edge, doubled outline or clipped structure.',
    1024: 'Timber boards, golden upright and the rounded drum rim continue smoothly across the seam; curved edges and highlights remain aligned.',
    2048: 'Large stone slab edges, diagonal sandy joints, grit and lighting continue naturally; no straight horizontal tone cut or duplicated pebble appears.',
    3072: 'Braided net border, rope knots and individual dark mesh strands cross the seam continuously; stone and sand edges behind the net stay aligned.',
    4096: 'Golden support ropes, curved border rope and layered mesh knots remain connected across the seam without broken links, ghost ropes or a tone band.',
    5120: 'Mesh, its shadow, paving and the timber support post continue across the seam; wood grain and knot are intact with no clipping or horizontal color jump.',
    6144: 'Plants, sand, rope knot and blue-gray paving joints continue across the seam; diagonal slab edges and shadows preserve their shapes.',
    7168: 'Blue glazed roof cylinders, their diagonal rims, highlights and dark gutters continue across the seam without a split edge, duplicated rim or horizontal lighting step.'
}
files = []
for x, observation in observations.items():
    path = QA / f'horizontal-y8192-x{x}.png'
    image = Image.open(path).convert('RGB')
    box = [x, 8064, x + 1024, 8320]
    crop_exact = exact(image, region.crop(box))
    dimensions_correct = image.size == (1024, 256)
    if not crop_exact:
        issues.append('Fresh native review strip differs from current region crop: ' + path.name)
    if not dimensions_correct:
        issues.append('Fresh native review strip dimensions differ: ' + path.name)
    files.append({'file': str(path), 'filename': path.name, 'sha256': sha(path),
                  'dimensions': list(image.size), 'candidateCropBox': box,
                  'seamAtImageY': 128, 'matchesCandidateNativeCrop': crop_exact,
                  'reviewedAtNativeScale': True, 'visualVerdict': 'PASS',
                  'verdict': 'PASS' if crop_exact and dimensions_correct else 'ISSUES',
                  'finding': observation})

old_review = read(OLD_QA / 'findings.json')
old_hashes = {entry['file']: entry['sha256'] for entry in read(OLD_QA / 'reviewed-crop-hashes.json')}
inherited = []
for entry in old_review['files']:
    old_name = entry['file']
    if old_name.startswith('horizontal-'):
        new_name = old_name.replace('horizontal-', 'horizontal-y4096-', 1)
    elif old_name == 'center-four-way-native.png':
        new_name = 'four-way-y4096.png'
    else:
        new_name = old_name
    old_path = OLD_QA / old_name
    new_path = QA / new_name
    recorded_sha = old_hashes[old_name]
    old_sha = sha(old_path)
    new_sha = sha(new_path)
    same_reviewed_hash = entry['sha256'] == recorded_sha == old_sha == new_sha
    old_image = Image.open(old_path).convert('RGB')
    new_image = Image.open(new_path).convert('RGB')
    matches_region = exact(new_image, region.crop(entry['candidateCropBox']))
    same_dimensions = old_image.size == new_image.size == tuple(entry['dimensions'])
    if not same_reviewed_hash:
        issues.append('Inherited upper-region crop hash differs: ' + old_name)
    if not matches_region or not same_dimensions:
        issues.append('Inherited upper-region native crop no longer matches: ' + old_name)
    inherited.append({'historicalFile': str(old_path), 'currentFile': str(new_path),
                      'reviewedSha256': recorded_sha, 'historicalSha256': old_sha,
                      'currentSha256': new_sha, 'dimensions': list(new_image.size),
                      'candidateCropBox': entry['candidateCropBox'],
                      'hashMatchesHistoricalNativeReview': same_reviewed_hash,
                      'matchesCurrentRegionNativeCrop': matches_region,
                      'dimensionsMatch': same_dimensions,
                      'verdict': 'PASS_INHERITED' if same_reviewed_hash and matches_region and same_dimensions else 'ISSUES'})
if len(inherited) != 17:
    issues.append('Expected all 17 inherited upper-region native reviews')
for path in historical_records:
    if sha(path) != historical_hashes_before[str(path)]:
        issues.append('Historical review record changed during this review: ' + str(path))

report = {
    'schemaVersion': 1,
    'reviewedAt': datetime.now(timezone.utc).isoformat(),
    'reviewer': 'resume_audit independent native visual review',
    'status': 'PASS' if not issues else 'ISSUES',
    'scope': 'Eight native horizontal seam strips at region y8192, between tile rows r04 and r05; all 17 existing upper four-tile-region reviews inherited only after exact hash and current native crop matching.',
    'candidate': {'file': str(candidate_path), 'sha256': candidate_sha, 'dimensions': list(region.size)},
    'assemblyManifest': {'file': str(manifest_path), 'sha256AtRead': sha(manifest_path)},
    'freshVisualReviewCount': len(files),
    'nativeViewMethod': 'view_image with detail original; every 1024x256 file viewed separately without resizing',
    'files': files,
    'blockingFindings': [],
    'issues': issues,
    'inheritedReviewCount': len(inherited),
    'allInheritedReviewsValid': all(entry['verdict'] == 'PASS_INHERITED' for entry in inherited),
    'inheritedUpperRegionReviews': inherited,
    'historicalReviewRecordsPreserved': [{'file': str(path), 'sha256': historical_hashes_before[str(path)]}
                                          for path in historical_records],
    'regionCandidateMutated': False,
    'formalAccepted': False,
    'remainingReviewOwner': 'Root reviews the four lower vertical strips, the lower four-way center and the whole preview separately.'
}
out = RESUME / 'region-horizontal-review.json'
out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: report[key] for key in ['status', 'freshVisualReviewCount',
    'inheritedReviewCount', 'allInheritedReviewsValid', 'issues']}))
