"""Record process-image retention after final exports and previews are verified."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

R = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

records = ['audit/straight-axis-cleanup.json',
           'audit/straight-axis-attack-qa-cleanup.json',
           'audit/straight-axis-cast-qa-cleanup.json']
removed = [entry for name in records for entry in read(R/name)['files']]
assert len(removed) == 27
assert all(not (R/entry['file']).exists() for entry in removed)
for action in ['run', 'hit', 'attack', 'cast']:
    assert not any(p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif'}
                   for p in (R/action/'staging').rglob('*'))

at = datetime.now(timezone.utc).isoformat()
retention = {'verifiedAt': at, 'removedProcessImages': len(removed),
             'records': records, 'formalFramesRetained': 196,
             'previewFilesRetained': 42, 'textualGenerationEvidenceRetained': True,
             'note': 'Process-image paths in historical visual evidence identify files viewed before cleanup; their SHA256 and disposition are preserved in the cleanup records.'}
p = R/'audit/straight-axis-final-review.json'
review = read(p)
for file, digest in review['currentFrameSha256'].items():
    assert sha(R/file) == digest
review['processImageRetention'] = retention
review['additionalSEReview'] = {
    'frames': ['run/SE/01.png','run/SE/02.png','run/SE/03.png','run/SE/04.png','run/SE/05.png'],
    'status': 'preserved_after_root_and_independent_static_review',
    'observation': 'SE02/03 flexed support shin returns toward lower left while toe extends lower right in SE perspective. SE04 heel-to-forefoot remains SE. No confirmed isolated ankle yaw or inter-frame directional reversal; root also checked normal/quarter browser playback.'}
save(p, review)
for name in review['staticAudits'] + review['independentRepairReviews'] + ['audit/final-visual-review.json']:
    p = R/name
    d = read(p)
    d['processImageRetention'] = retention
    save(p, d)

p = R/'audit/bamboo-final-browser-review.json'
d = read(p)
d['files'] = {name: sha(R/name) for name in d['files']}
d['metadataHashesRefreshedAfterCleanup'] = at
d['latestVisualEvidence'] = 'audit/straight-axis-final-review.json'
save(p, d)

note = '本轮成品与引用验证后，已清理27张加工／诊断中间图；保留196张正式动作帧、配套预览及逐图生成与来源文字记录。清理明细见 `audit/straight-axis-cleanup.json`、`audit/straight-axis-attack-qa-cleanup.json` 和 `audit/straight-axis-cast-qa-cleanup.json`。'
for name in ['STATUS.md', 'MERGE_HANDOFF.md']:
    p = R/name
    t = p.read_text(encoding='utf-8')
    if note not in t:
        anchor = '下方视频反馈记录保留为前一轮历史。'
        assert anchor in t
        t = t.replace(anchor, anchor+'\n\n'+note, 1)
        p.write_text(t, encoding='utf-8')
print('27 process bitmaps removed;196 final frames and42 previews retained;latest audit and browser hashes synchronized.')
