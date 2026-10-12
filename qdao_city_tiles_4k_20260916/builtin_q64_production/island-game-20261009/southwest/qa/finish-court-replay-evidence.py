"""Same-coordinate QA crops and raw RGB hashes for replaying the two court repairs."""
from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'qa'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def crop(prefix, box):
    out = Image.new('RGB', (box[2]-box[0], box[3]-box[1]))
    for tile in ('r09_c04', 'r10_c04'):
        report = json.loads((QA / f'{prefix}-{tile}-report.json').read_text())
        bb = report['candidateGlobalBox']
        clip = [max(box[0], bb[0]), max(box[1], bb[1]), min(box[2], bb[2]), min(box[3], bb[3])]
        if clip[2] <= clip[0] or clip[3] <= clip[1]:
            continue
        image = Image.open(QA / f'{prefix}-{tile}-candidate-4096.png').convert('RGB')
        out.paste(image.crop((clip[0]-bb[0], clip[1]-bb[1], clip[2]-bb[0], clip[3]-bb[1])), (clip[0]-box[0], clip[1]-box[1]))
    return out

steps = [
    ('court-trial-join1-v01', 'r09_r10_c04_court_join1_v01', [13500,36280,14754,37534]),
    ('court-trial-join2-resume-v01', 'r09_r10_c04_court_join2_v01', [14500,36280,15754,37534]),
]
evidence = []
for prefix, stem, box in steps:
    manifest = json.loads((QA / (prefix+'-manifest.json')).read_text())
    im = crop(prefix, box)
    file = QA / (prefix+'-candidate-native1254.png')
    if not file.exists():
        im.save(file)
    evidence.append({
        'prefix': prefix, 'repairStem': stem, 'globalBox': box,
        'repairROI': manifest['repairRois'], 'mandatoryTargets': manifest['mandatoryTargets'], 'band': 70,
        'selectionMaskSha256': manifest['sharedSelectionMask']['sha256'],
        'candidateRepairAreaRgbSha256': digest(im.tobytes()),
        'candidateRepairAreaPng': str(file).replace('\\','/'),
        'candidateRepairAreaPngSha256': digest(file.read_bytes()),
        'validation': [{'tile': t['tile'], 'pixelCount': t['validation']['pixelCount'], 'mismatchedPixels': t['validation']['mismatchedPixels'], 'sameGlobalCoordinateExact': t['validation']['sameGlobalCoordinateExact']} for t in manifest['tiles']],
    })
union = [13500,36280,15754,37534]
im = crop(steps[-1][0], union)
for label, box in [('left', [13500,36280,14754,37534]), ('right', [14500,36280,15754,37534]), ('overlap', [14400,36480,14854,37330])]:
    fp = QA / f'court-final-trial-{label}-native100.png'
    if not fp.exists():
        crop(steps[-1][0], box).save(fp)
out = {
    'createdAtUtc': datetime.now(timezone.utc).isoformat(),
    'status': 'QA trial candidates with native pixel verification; visual review recorded separately; not formal acceptance',
    'steps': evidence,
    'finalUnionRegion': {'globalBox': union, 'mode': 'RGB', 'hashEncoding': 'uncompressed RGB bytes, row-major, 3 channels', 'sha256': digest(im.tobytes())},
    'replayCondition': 'Base updates outside these native footprints do not change the masks or repair-area hashes. Compare both mask hashes and native RGB region hashes after replay.',
}
fp = QA / 'court-replay-resume-v01-evidence.json'
fp.write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(out, ensure_ascii=True))
