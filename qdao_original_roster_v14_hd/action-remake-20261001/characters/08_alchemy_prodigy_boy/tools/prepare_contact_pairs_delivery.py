"""Merge the five reviewed selections and publish their contact-pair timing.

Run only after reviewing the completed eight-direction sheets. This script
does not certify artwork and does not export PNGs.
"""
from pathlib import Path
import datetime, json, sys

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'provenance/contact-pairs-20261004'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
write = lambda p, x: p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')
names = ['east', 'south-east', 'north', 'south', 'west']
selected = {}
for name in names:
    source = read(BATCH / (name + '-selection.json'))
    assert not selected.keys() & source.keys(), name
    for slot, value in source.items():
        assert slot.startswith('run/') and value['staticReviewed'] is True, slot
        assert (ROOT / value['source']).is_file(), slot
    selected.update(source)
directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
counts = {d: sum(s.startswith('run/' + d + '/') for s in selected) for d in directions}
assert all(counts.values()), counts
if '--apply' not in sys.argv:
    print(json.dumps({'selected': len(selected), 'byDirection': counts, 'written': False}))
    raise SystemExit(0)

write(ROOT / 'contact-pairs-selection.json', dict(sorted(selected.items())))
profile = read(ROOT / 'run-timing.json')
profile.update({'version': 3, 'updatedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'normalCycleMs': 1200,
    'basis': 'Two distinct poses per support-position segment; 16 independent frames at uniform 75ms.',
    'contactPairPlan': read(BATCH / 'plan.json')['pairPlan']})
phases = [
    '右足前落点·承重', '右足身下·压重', '右足身下·身体经过',
    '右足稍后·支撑', '右足稍后·后移承重', '右足更后·前掌支撑', '右足更后·末段推蹬',
    '左足前落点·初接触', '左足前落点·承重', '左足身下·压重', '左足身下·身体经过',
    '左足稍后·支撑', '左足稍后·后移承重', '左足更后·前掌支撑', '左足更后·末段推蹬',
    '右足前落点·初接触']
for d in directions:
    profile['directions'][d] = {'frameMs': [75] * 16, 'phases': phases,
        'positionPairMs': 150, 'supportFootByFrame': ['right'] * 7 + ['left'] * 8 + ['right']}
write(ROOT / 'run-timing.json', profile)
print(json.dumps({'selected': len(selected), 'byDirection': counts, 'written': True}))
