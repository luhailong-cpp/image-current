"""Collect actual UI samples; do not infer continuous watching or client testing."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
R = Path(__file__).resolve().parents[1]
read = lambda p: json.loads((R / p).read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256((R / p).read_bytes()).hexdigest()
run = read('reviews/full-limb-run-browser-samples-20261005.json')
controls = read('reviews/full-limb-run-browser-controls-20261005.json')
oldbattle = read('reviews/full-limb-battle-browser-samples-20261005.json')
cast = read('reviews/full-limb-cast-E-final-browser-20261005.json')
delivery = read('reviews/full-limb-final-page-browser-20261005.json')
assert run['frameMs'] == 60 and run['cycleMs'] == 960
assert {s['direction'] for s in run['samples']} == {'N','NE','E','SE','S','SW','W','NW'}
for s in run['samples']:
    assert s['before']['images'][0]['src'] != s['after']['images'][0]['src'], s['direction']
    for t in ['before','after']:
        assert '正常60ms/帧' in s[t]['status']
        assert all(im['complete'] and im['width'] == im['height'] == 1024 for im in s[t]['images'])
c = controls['controls']
assert '第 16 /16' in c['last']['labels'][0]
assert '第 01 /16' in c['wrapToFirst']['labels'][0]
assert '第 16 /16' in c['wrapToLast']['labels'][0]
battle = [s for s in oldbattle['samples'] if (s['action'],s['direction']) != ('cast','E')] + cast['samples']
assert {(s['action'],s['direction']) for s in battle} == {(a,d) for a in ['hit','attack','cast'] for d in ['E','W']}
for s in battle:
    for t in ['before','after']:
        v = s[t]
        assert v['width'] == v['height'] == 1024
        assert sha(v['detail']['path']) == v['detail']['sha256'], v['detail']['path']
assert sha(cast['frame04']['detail']['path']) == cast['frame04']['detail']['sha256']
assert cast['frame04']['detail']['frame'] == 4
assert '60ms' in delivery['status'] and '离线复核完成' in delivery['status']
files = ['reviews/full-limb-run-browser-samples-20261005.json','reviews/full-limb-run-browser-controls-20261005.json','reviews/full-limb-battle-browser-samples-20261005.json','reviews/full-limb-cast-E-final-browser-20261005.json','reviews/full-limb-final-page-browser-20261005.json']
result = {
    'reviewedAtUtc': datetime.now(timezone.utc).isoformat(),
    'sequences':14,'runFrameMs':60,'runCycleMs':960,'runSlowCycleMs':3840,
    'runSamples':run['samples'],'runControls':c,'battleSamples':battle,
    'castE04':cast['frame04'],'battleWrapForward':oldbattle['wrapForward'],'battleWrapBackward':oldbattle['wrapBackward'],
    'finalPage':delivery,'rawEvidence':{p:sha(p) for p in files},
    'formalSourceHashes':{f['path']:sha(f['path']) for f in read('reviews/final-review.json')['frames']},
    'scope':'Actual browser normal/slow frame samples, image loading, current hashes and boundary stepping; per-frame visual review recorded separately. Short samples may fall within the same slow frame; not continuous-video observation, client locomotion or game timing validation.',
    'supersededSamples':'Earlier cast/E browser samples predate the final E04 revision and are excluded from current samples; original evidence retained.',
    'clientIntegrated':False,'knownUnresolvedBrowserFailures':[]
}
(R/'reviews/full-limb-browser-20261005.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print({'sequences':14,'runFrameMs':60,'runCycleMs':960,'currentBattleSamples':len(battle),'clientIntegrated':False})
