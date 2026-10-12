"""Aggregate explicit new image reviews after the video-axis revision."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((R/p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
reports=['reviews/video-axis-E-SE-20261004.json','reviews/video-axis-N-W-20261004.json','reviews/video-axis-NE-NW-20261004.json','reviews/video-axis-S-SW-20261004.json']
old=read('reviews/final-review.json')
before={f['path']:f['sha256'] for f in old['frames']}
battle=[f for f in old['frames'] if '/run/' not in f['path']]
assert len(battle)==68 and all(sha(f['path'])==f['sha256'] for f in battle)
allrun=[];owners={}
for p in reports:
 doc=read(p)
 assert 'knownUnresolvedArtFailures' in doc and not doc['knownUnresolvedArtFailures'],p
 assert len(doc['frames'])==32,p
 for f in doc['frames']:
  path=f.get('path') or f.get('file')
  assert path and sha(path)==f['sha256'],(p,path)
  assert f['decision'] in ['retained','replaced'],f
  assert f.get('reason'),f
  f=dict(f,path=path,review=p)
  allrun.append(f);owners[f['direction']]=p
assert len(allrun)==128 and len({f['path'] for f in allrun})==128
assert set(owners)=={'N','NE','E','SE','S','SW','W','NW'}
browser=read('reviews/video-axis-browser-20261004.json')
assert browser['observedPlaybackProgression'] and set(browser['directions'])==set(owners)
changed=[f for f in allrun if f['decision']=='replaced']
for f in allrun:
 assert (before.get(f['path'])!=f['sha256'])==(f['decision']=='replaced'),f['path']
now=datetime.now(timezone.utc).isoformat()
sequences=[]
for d in ['N','NE','E','SE','S','SW','W','NW']:
 fs=[f for f in allrun if f['direction']==d];assert len(fs)==16
 nums=[f['frame'] for f in fs if f['decision']=='replaced']
 detail=('局部重画'+','.join(f'{n:02}' for n in sorted(nums))+'的膝踝鞋轴，其余原帧保留。') if nums else '逐帧复核未见本轮所指的鞋掌外扭，保留16张原帧。'
 sequences.append({'action':'run','direction':d,'frames':16,'observations':detail+'按原视频连续帧参考复核运动平面和相邻姿态，保留正常屈膝/透视、两帧位置段及1200ms时长。','offlineReview':'video_axis_revision_reviewed','clientReview':'not_integrated','detail':owners[d]})
old.update(reviewedAtUtc=now,frames=battle+allrun,sequences=sequences+[s for s in old['sequences'] if s['action']!='run'],knownUnresolvedArtFailures=[],browserEvidence='reviews/video-axis-browser-20261004.json',videoAxisRevision={'status':'offline_review_complete','finishedAtUtc':now,'changedFrames':len(changed),'retainedRunFrames':128-len(changed),'reports':reports,'sourceVideo':'reviews/video-reference-sampling-20261004.json'})
(R/'reviews/final-review.json').write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
phases=read('reviews/run-position-pairs-final-20261004.json')
bydir={d:[f for f in allrun if f['direction']==d] for d in owners}
for g in phases['groups']:
 d=g['direction'];g['priorPositionReview']=g.get('review');g['review']=owners[d];g['reviewSha256']=sha(owners[d]);g['frames']=bydir[d]
phases['reviewedAt']=now;phases['videoAxisRevision']='position assignments retained; knee ankle shoe axes independently redrawn in named slots'
(R/'reviews/run-position-pairs-final-20261004.json').write_text(json.dumps(phases,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'reviewedAtUtc':now,'reference':'reviews/video-reference-sampling-20261004.json','reviewedRunFrames':128,'changedFrames':len(changed),'retainedRunFrames':128-len(changed),'reports':{p:sha(p) for p in reports},'frames':allrun,'browserEvidence':'reviews/video-axis-browser-20261004.json','knownUnresolvedArtFailures':[],'clientIntegrated':False}
(R/'reviews/video-axis-final-20261004.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print({'reviewedRun':128,'replaced':len(changed),'retained':128-len(changed),'battleUnchanged':68})

