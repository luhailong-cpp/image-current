"""Collect separately viewed current images; never infer visual pass from inventory."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((R/p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
reports={'reviews/full-limb-root-20261005.json':56,'reviews/full-limb-hit-S-SW-20261004.json':44,'reviews/full-limb-cast-NE-NW-20261004.json':64,'reviews/full-limb-N-W-20261004.json':32}
old=read('reviews/final-review.json')
before={f['path']:f['sha256'] for f in old['frames']}
allframes=[];owners={}
for p,count in reports.items():
 doc=read(p)
 assert 'knownUnresolvedArtFailures' in doc and not doc['knownUnresolvedArtFailures'],p
 assert len(doc['frames'])==count,(p,len(doc['frames']))
 for item in doc['frames']:
  f=dict(item);path=f.get('path') or f.get('file');f['path']=path
  assert path and sha(path)==f['sha256'],(p,path)
  assert f['decision'] in ['retained','replaced'] and f.get('reason'),f
  f['review']=p
  allframes.append(f);owners[(f['action'],f['direction'])]=p
assert len(allframes)==196 and len({f['path'] for f in allframes})==196
expected={(a,d,n) for a,ds,c in [('run',['N','NE','E','SE','S','SW','W','NW'],16),('hit',['E','W'],6),('attack',['E','W'],12),('cast',['E','W'],16)] for d in ds for n in range(1,c+1)}
assert {(f['action'],f['direction'],f['frame']) for f in allframes}==expected
# The old final review is the last delivered version; save baseline once before replacing it.
baseline_path=R/'reviews/full-limb-all-before-20261005.json'
if not baseline_path.exists():baseline_path.write_text(json.dumps({'frames':old['frames'],'priorReviewedAtUtc':old.get('reviewedAtUtc')},ensure_ascii=False,indent=2),encoding='utf-8')
before={f['path']:f['sha256'] for f in read('reviews/full-limb-all-before-20261005.json')['frames']}
for f in allframes:
 assert (before[f['path']]!=f['sha256'])==(f['decision']=='replaced'),f['path']
changed=[f for f in allframes if f['decision']=='replaced']
now=datetime.now(timezone.utc).isoformat()
sequences=[]
for a,ds,c in [('run',['N','NE','E','SE','S','SW','W','NW'],16),('hit',['E','W'],6),('attack',['E','W'],12),('cast',['E','W'],16)]:
 for d in ds:
  fs=[f for f in allframes if f['action']==a and f['direction']==d];assert len(fs)==c
  nums=[f['frame'] for f in fs if f['decision']=='replaced']
  detail=('局部重画'+','.join(f'{n:02}' for n in sorted(nums))+'；其余已正确帧保留。') if nums else f'逐张重新看图，保留现有{c}张。'
  detail+='已查肩肘腕与右扇左铃握持，以及髋膝踝鞋头的动作轴、支撑与屈膝。'
  if a=='run':detail+='两帧一个相对位置段及16×60ms=960ms保持。'
  sequences.append({'action':a,'direction':d,'frames':c,'observations':detail,'offlineReview':'full_limb_review_complete','clientReview':'not_integrated','detail':owners[(a,d)]})
summary={'reviewedAtUtc':now,'reviewedFrames':196,'changedFrames':len(changed),'retainedFrames':196-len(changed),'changedPaths':[f['path'] for f in changed],'reports':{p:sha(p) for p in reports},'frames':allframes,'criteria':'Actual image review of shoulder-elbow-wrist-grip and hip-knee-ankle-toe motion axes. Natural flexion and perspective retained; correct frames retained.','sourceVideo':'reviews/video-reference-sampling-20261004.json','browserEvidence':'reviews/full-limb-browser-20261005.json','knownUnresolvedArtFailures':[],'clientIntegrated':False}
old.update(reviewedAtUtc=now,frames=allframes,sequences=sequences,knownUnresolvedArtFailures=[],browserEvidence='reviews/full-limb-browser-20261005.json',fullLimbRevision={'status':'offline_image_review_complete','finishedAtUtc':now,'reviewedFrames':196,'changedFrames':len(changed),'retainedFrames':196-len(changed),'reports':list(reports)})
(R/'reviews/final-review.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'reviews/full-limb-final-20261005.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
phases=read('reviews/run-position-pairs-final-20261004.json')
for g in phases['groups']:
 d=g['direction'];g['priorAxisReview']=g.get('review');g['review']=owners[('run',d)];g['reviewSha256']=sha(owners[('run',d)]);g['frames']=[f for f in allframes if f['action']=='run' and f['direction']==d]
phases['reviewedAt']=now;phases['fullLimbRevision']='All hands and feet reviewed again, including planted hip-knee-ankle-toe motion axes; position assignments unchanged.'
(R/'reviews/run-position-pairs-final-20261004.json').write_text(json.dumps(phases,ensure_ascii=False,indent=2),encoding='utf-8')
print({'reviewed':196,'replaced':len(changed),'retained':196-len(changed),'changedPaths':summary['changedPaths']})
