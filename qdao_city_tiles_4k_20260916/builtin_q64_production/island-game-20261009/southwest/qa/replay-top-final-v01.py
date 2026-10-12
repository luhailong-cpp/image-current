"""Replay reviewed top joins on stable bases; stop before continuing on any trial mismatch."""
from pathlib import Path
import sys, json, hashlib, gc
from datetime import datetime, timezone
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'qa'
sys.path.insert(0, str(ROOT))
from native_multi_tile_repair import apply_repair

def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def save(name, data):
    target = QA / name
    tmp = QA / (name + '.stage')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(target)

def now():
    return datetime.now(timezone.utc).isoformat()

def right_half(prefix):
    p = QA / (prefix + '-repair-area-base-left-candidate-right-100pct.png')
    with Image.open(p) as im:
        assert im.size == (2508, 1254)
        return np.array(im.convert('RGBA').crop((1254, 0, 2508, 1254)))

mapping = {
    'r09_c03': 'multi-boundary-v02-r09_c03',
    'r09_c04': 'c04-cylinder-join-v01-r09_c04',
    'r10_c03': 'r10c03-roof-trial-v05-r10_c03',
    'r10_c04': 'c04-int-lowrib-v01-r10_c04',
}
initial = dict(mapping)
steps = [
    ('package', 'c03pkg-trial-v01', 'r09_r10_c03_package_join_v01', ['r09_c03','r10_c03']),
    ('flower', 'c03flower-trial-v01', 'r09_r10_c03_wallfoot_join_v01', ['r09_c03','r10_c03']),
    ('rightsteps', 'rightsteps-trial-v01', 'r09_r10_c04_steps_join_v01', ['r09_c03','r09_c04','r10_c03','r10_c04']),
    ('leftsteps', 'leftsteps-trial-v01', 'r09_r10_c03_steps_join_v01', ['r09_c03','r10_c03']),
    ('court1', 'court-trial-join1-v01', 'r09_r10_c04_court_join1_v01', ['r09_c04','r10_c04']),
    ('court2', 'court-trial-join2-resume-v01', 'r09_r10_c04_court_join2_v01', ['r09_c04','r10_c04']),
]
records = []
for label, trial, stem, tiles in steps:
    prefix = 'top-final-' + label + '-v01'
    reference = load(QA / (trial + '-manifest.json'))
    reference_report = load(reference['tiles'][0]['report']['path'])
    specs = [[QA / (mapping[t] + suffix) for suffix in ('-candidate-4096.png', '-source-id-mask.png', '-report.json')] for t in tiles]
    print(json.dumps({'event':'starting_step','label':label,'prefix':prefix,'bases':{t:mapping[t] for t in tiles}}), flush=True)
    existing = QA / (prefix + '-manifest.json')
    if existing.exists():
        result = load(existing)
        for tile in tiles:
            report = load(QA / (prefix+'-'+tile+'-report.json'))
            assert report['baseCandidate']['path'] == str(QA / (mapping[tile]+'-candidate-4096.png')).replace('\\','/')
    else:
        result = apply_repair(specs, stem, prefix,
            band=reference_report['parameters']['bandPixels'],
            repair_rois=reference['repairRois'], mandatory_targets=reference['mandatoryTargets'],
            flush_edges=reference['flushOuterEdges'])
    actual, expected = right_half(prefix), right_half(trial)
    mismatched = int(np.count_nonzero(np.any(actual != expected, axis=2)))
    mask_same = result['sharedSelectionMask']['sha256'] == reference['sharedSelectionMask']['sha256']
    record = {
        'label':label, 'prefix':prefix, 'repairStem':stem, 'reviewedTrial':trial,
        'band':reference_report['parameters']['bandPixels'], 'repairRois':reference['repairRois'],
        'mandatoryTargets':reference['mandatoryTargets'], 'flushOuterEdges':reference['flushOuterEdges'],
        'selectionMaskSha256':result['sharedSelectionMask']['sha256'], 'maskMatchesReviewedTrial':mask_same,
        'repairGlobalBox':result['repairGlobalBox'],
        'candidateRepairAreaRgbaSha256':hashlib.sha256(actual.tobytes()).hexdigest(),
        'reviewedTrialRepairAreaRgbaSha256':hashlib.sha256(expected.tobytes()).hexdigest(),
        'candidateRepairAreaMismatchedPixels':mismatched,
        'tiles':[{'tile':t['tile'], 'candidate':t['candidate'], 'validation':t['validation']} for t in result['tiles']],
    }
    records.append(record)
    save('top-final-replay-v01-comparisons.json', {'updatedAtUtc':now(), 'steps':records, 'status':'running' if mask_same and mismatched==0 else 'mismatch_stopped', 'formalAccepted':False})
    print(json.dumps({'event':'step_compared','label':label,'maskMatches':mask_same,'mismatchedPixels':mismatched}), flush=True)
    if not mask_same or mismatched:
        sys.exit(3)
    for tile in tiles:
        mapping[tile] = prefix + '-' + tile
    del actual, expected, result
    gc.collect()

spec = {**mapping, 'topSourceStems':[s[2] for s in steps], 'initialBases':initial,
    'createdAtUtc':now(), 'status':'Stable internal bases plus six reviewed top repairs; per-step binary masks and candidate RGBA regions exactly reproduce reviewed trials',
    'comparisonReport':str(QA / 'top-final-replay-v01-comparisons.json').replace('\\','/'),
    'qaReferences':['c03pkg-trial-v01-visual-review.json','c03flower-trial-v01-visual-review.json','rightsteps-trial-v01-visual-review.json','leftsteps-trial-v01-visual-review.json','court-replay-resume-v01-visual-review.json'],
    'formalAccepted':False,
    'mergeInstructions':'Use these six source stems to merge top contributions by original global coordinates/source IDs into the independent finial branch. No scaling, feathering or color changes.'}
save('top-final-spec-v01.json', spec)
save('top-final-replay-v01-comparisons.json', {'updatedAtUtc':now(), 'steps':records, 'status':'all_six_steps_match_reviewed_trials_exactly', 'formalAccepted':False})
print(json.dumps({'event':'complete','spec':spec}), flush=True)
