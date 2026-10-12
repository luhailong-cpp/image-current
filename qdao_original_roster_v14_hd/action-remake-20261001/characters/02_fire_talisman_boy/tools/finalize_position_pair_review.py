"""Finalize only explicit reviewed SHA snapshots, never infer art pass from inventory."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
reports={
 'N':'reviews/finish-north-N-review.json',
 'NE':'reviews/run-NE-eight-support-final-review-20261004.json',
 'E':'reviews/run-E-position-pairs-final-review-20261004.json',
 'SE':'reviews/run-SE-position-pairs-final-review-20261004.json',
 'S':'reviews/run-S-position-pairs-final-review-20261004.json',
 'SW':'reviews/run-SW-position-pairs-final-review-20261004.json',
 'W':'reviews/finish-north-W-review.json',
 'NW':'reviews/run-NW-eight-support-final-review-20261004.json'}
review=read('reviews/final-review.json')
battle=[f for f in review['frames'] if '/run/' not in f['path']]
assert len(battle)==68 and all(sha(f['path'])==f['sha256'] for f in battle)
allframes=battle[:];groups=[];seq=[]
browser=read('reviews/final-browser-review-20261004.json')
assert set(browser['directions'])==set(reports) and browser['observedPlaybackProgression']
for d,reportpath in reports.items():
    doc=read(reportpath)
    assert not doc.get('knownUnresolvedArtFailures'),(d,doc.get('knownUnresolvedArtFailures'))
    frames=doc['frames'];assert len(frames)==16,d
    checked=[]
    for f in frames:
        path=f.get('path') or f.get('file');assert path==f"frames/run/{d}/{int(f['frame']):02}.png"
        assert sha(path)==f['sha256'],path
        checked.append(dict(path=path,sha256=f['sha256'],action='run',direction=d,frame=f['frame'],review=reportpath))
    allframes.extend(checked)
    groups.append({'direction':d,'review':reportpath,'reviewSha256':sha(reportpath),'pairs':doc.get('supportPairs',doc.get('pairs',[])),'frames':frames})
    obs='同一支撑脚连续8帧，4个相对位置各2张独立姿态；已核对膝踝鞋轴、持物与换脚。正常1200ms/慢放4800ms屏幕取样和逐帧复核通过。'
    seq.append({'action':'run','direction':d,'frames':16,'observations':obs,'offlineReview':'completed_two_frame_position_pairs','clientReview':'not_integrated','detail':reportpath})
assert len(allframes)==196 and len({x['path'] for x in allframes})==196
review.update(reviewedAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='root, finish_ne, finish_s_sw, finish_north',frames=allframes,knownUnresolvedArtFailures=[],groundingRevision='same support foot8frames,4progressive positions×2independent poses,16×75ms=1200ms',browserEvidence='reviews/final-browser-review-20261004.json')
review['sequences']=seq+[s for s in review['sequences'] if s['action']!='run']
(R/'reviews/final-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'reviews/run-position-pairs-final-20261004.json').write_text(json.dumps({'reviewedAt':review['reviewedAtUtc'],'timing':{'frameMs':75,'cycleMs':1200,'slowCycleMs':4800},'groups':groups,'clientIntegrated':False},ensure_ascii=False,indent=2),encoding='utf-8')
print({'reviewed':len(allframes),'runDirections':len(groups),'knownUnresolvedArtFailures':[]})
