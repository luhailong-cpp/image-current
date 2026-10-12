"""Verify shipped files, exact provenance and current preview dependencies."""
from pathlib import Path
from PIL import Image
import hashlib, json, datetime
ROOT = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
frames = manifest['frames']
assert len(frames) == 196
assert len({f['sha256'] for f in frames}) == 196
assert len({f['derivedFrom']['sha256'] for f in frames}) == 196
counts = {}
for f in frames:
    path = (ROOT/f['file']).resolve()
    assert path.is_relative_to(ROOT) and path.is_file()
    assert sha(path) == f['sha256']
    with Image.open(path) as im:
        assert im.size == (1024,1024) and im.mode == 'RGBA'
        assert im.getchannel('A').getextrema() == (0,255)
    adjacent = Path(str(path)+'.generation.json')
    assert json.loads(adjacent.read_text(encoding='utf-8')) == f
    origin = ROOT/f['derivedFrom']['generationRecord']
    assert origin.is_file() and sha(origin) == f['derivedFrom']['generationRecordSha256']
    assert min(f['derivedFrom']['nativeSize']) >= 1024
    key = f['slot'].rsplit('/',1)[0]
    counts[key] = counts.get(key,0)+1
assert counts == {**{f'run/{d}':16 for d in ['N','NE','E','SE','S','SW','W','NW']},
                 **{f'{a}/{d}':n for a,n in [('hit',6),('attack',12),('cast',16)] for d in ['E','W']}}
raw = (ROOT/'preview/data.js').read_text(encoding='utf-8')
groups = json.loads(raw.removeprefix('window.PREVIEW_DATA=').removesuffix(';'))
assert len(groups) == 14
profiles = json.loads((ROOT/'run-timing.json').read_text(encoding='utf-8-sig'))
for g in groups:
    assert len(g['frames']) == counts[g['key']]
    assert (ROOT/'preview'/(g['key'].replace('/','-')+'-contact.png')).is_file()
    if g['key'].startswith('run/'):
        p = profiles['directions'][g['key'].split('/')[1]]
        assert g['frameMs'] == p['frameMs']
        assert len(p['frameMs']) == len(p['phases']) == 16
        assert sum(p['frameMs']) == profiles['normalCycleMs'] == 960
        assert p['frameMs'] == [60]*16 and g['ms'] == 60
        assert all(ms > 0 for ms in p['frameMs'])
    for uri in g['frames']:
        p = (ROOT/'preview'/uri.split('?')[0]).resolve()
        assert p.is_relative_to(ROOT/'runtime') and p.is_file()
        assert uri.endswith(sha(p)[:12])
report = {'verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'pass':True,'runtimeFrames':196,'groups':counts,'uniqueSourceSHA':196,
          'canvas':[1024,1024],'mode':'RGBA','alphaExtrema':[0,255],
          'provenanceClosed':True,'previewFileReferencesClosed':True,
          'runTimingProfiles':8,'normalRunCycleMs':960,'runFrameMs':60,
          'artisticAcceptanceProvenByThisScript':False,'clientValidated':False}
(ROOT/'provenance/delivery-technical-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
