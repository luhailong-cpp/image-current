"""Preserve the completed first-row visual review with verified source pixels.

The four 512x1024 windows were inspected using view_image(detail='original').
This script verifies those exact artifacts and writes only a new JSON report.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parent
TILE = OUT.parent.parent
SIGNATURE = '0e9feb587f4ac73c3cdc'
EXPORT = TILE / 'qa' / 'first-row-v20261012' / SIGNATURE


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rgb(path):
    with Image.open(path) as im:
        return im.convert('RGB')


def require(condition, message):
    if not condition:
        raise ValueError(message)


data = json.loads((EXPORT / 'export.json').read_text(encoding='utf-8-sig'))
require(data['inputSignature'] == SIGNATURE, 'Export signature changed')
source_images = []
for source in data['nativeSources']:
    require(sha(source['file']) == source['sha256'], 'Native source hash changed: ' + source['file'])
    im = rgb(source['file'])
    require(im.size == (1254, 1254), 'Native source dimensions differ')
    source_images.append(im)
require(hashlib.sha256(''.join(source['sha256'] for source in data['nativeSources']).encode()).hexdigest()[:20] == SIGNATURE,
        'Sources do not match visually reviewed signature')
west, *cores = source_images
require(len(cores) == 4, 'Expected 4 first-row sources')
row = Image.new('RGB', (4096, 1024))
for col, core in enumerate(cores):
    row.paste(core.crop((115, 115, 1139, 1139)), (col * 1024, 0))
verified_artifacts = []
for artifact in data['artifacts']:
    path = Path(artifact['file'])
    require(sha(path) == artifact['sha256'], 'Reviewed artifact SHA256 changed: ' + str(path))
    actual = rgb(path)
    require(list(actual.size) == artifact['size'], 'Artifact dimensions differ')
    if artifact['kind'] == 'first-row-native-core-paste':
        replay = row
    elif artifact['kind'] == 'internal-seam':
        replay = row.crop(tuple(artifact['crop']))
    elif artifact['kind'] == 'shared-west-seam':
        replay = Image.new('RGB', (512, 1024))
        replay.paste(west.crop((883, 115, 1139, 1139)), (0, 0))
        replay.paste(cores[0].crop((115, 115, 371, 1139)), (256, 0))
    else:
        raise ValueError('Unexpected artifact kind')
    require(actual.size == replay.size and actual.tobytes() == replay.tobytes(), 'Artifact is not exact native crop/paste: ' + str(path))
    verified_artifacts.append(dict(artifact, integerCropPastePixelReplay=True))

findings = {
    'vertical-p11-p12-join-100pct.png': {
        'sourceIndices': [1, 2],
        'conclusion': 'pass_no_P2',
        'observation': 'At seam x=256 the gold scroll/edge, dark teal fascia and red supporting beam continue without a height step or doubled contour. The cream wall and lower window trim also remain structurally continuous. Fine surface-texture variation is not a structural gap.',
    },
    'vertical-p12-p13-join-100pct.png': {
        'sourceIndices': [2, 3],
        'conclusion': 'pass_no_P2',
        'observation': 'Roof tile end ornaments, the sloping teal fascia, red beam and diagonal cast-shadow boundary remain continuous across x=256. The wall texture has small natural variation without an obvious straight patch boundary.',
    },
    'vertical-p13-p14-join-100pct.png': {
        'sourceIndices': [3, 4],
        'conclusion': 'pass_no_P2',
        'observation': 'The pale stone parapet cap, beveled edges and diagonal masonry courses cross x=256 without an offset or missing block. The visible vertical masonry joints are consistent with the wall construction rather than a full-height cut at the patch seam.',
    },
    'west-r07c15-p14-r07c16-p11-join-100pct.png': {
        'sourceIndices': [0, 1],
        'conclusion': 'pass_no_P2',
        'observation': 'The cylindrical roof tile rows, highlights and dark joints continue across x=256. The bottom gold fascia and red beam join with matching slope and thickness; no orphan trim, duplicated roof row or structural break is visible.',
    },
}
windows = []
for artifact in verified_artifacts:
    name = Path(artifact['file']).name
    if name not in findings:
        continue
    finding = findings[name]
    windows.append({
        'file': artifact['file'], 'sha256': artifact['sha256'], 'size': artifact['size'], 'seamX': 256,
        'sourceImages': [data['nativeSources'][index] for index in finding['sourceIndices']],
        'inspection': 'view_image original: 512x1024 native-pixel seam window',
        'integerCropPastePixelReplay': True, 'verdict': finding['conclusion'],
        'observation': finding['observation'], 'P2Issues': [], 'repairRequired': False,
    })
require(len(windows) == 4, 'Expected 4 visually reviewed seam windows')
result = {
    'tile': TILE.name, 'inputSignature': SIGNATURE, 'reviewedAt': datetime.now(timezone.utc).isoformat(),
    'status': 'pass_no_P2_in_reviewed_first_row_windows',
    'scope': 'Three first-row internal vertical seams and the first-row west shared seam only.',
    'fullTileAccepted': False, 'northBoundaryStatus': 'absent_neighbor_pending_future_connection_not_audited',
    'sourceAuditReport': str(OUT / 'source-audit-20261012T150310772735Z.json'),
    'nativeSources': data['nativeSources'], 'windows': windows,
    'overview': {'file': str(EXPORT / 'first-row-native.png'), 'nativeSize': [4096, 1024],
                 'displaySize': [2048, 512], 'purpose': 'Supporting overall composition only; seam judgments use the four original-size windows.'},
    'verifiedArtifacts': verified_artifacts, 'P2Issues': [], 'repairRequired': False,
    'sourceDataModified': False,
}
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
report = OUT / f'first-row-visual-review-{SIGNATURE}-{stamp}.json'
with report.open('x', encoding='utf-8') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'status': result['status'], 'windowsReviewed': len(windows), 'P2Count': 0, 'nativeSourceHashesVerified': len(source_images), 'artifactsPixelReplayed': len(verified_artifacts), 'report': str(report)}))
