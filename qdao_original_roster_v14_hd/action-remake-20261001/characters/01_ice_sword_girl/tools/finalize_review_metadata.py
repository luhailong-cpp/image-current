"""Close completed artwork review using the final reviewers' records, without altering images."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
nw=read(R/'review/NW-final-independent-review.json')
assert nw['staticReviewPassed'] and nw['positionPairsVerified'] and not nw['hardIssues']
p=R/'review/run-NW-selection.json';s=read(p)
assert [(f['sha256']) for f in s['frames']]==[f['sha256'] for f in nw['frameChecks']]
s.update(artStatus='final_static_sequence_review_passed',positionPairsVerified=True,eightConsecutiveSupportVerified=True,agentVisualReviewPassed=True,agentSequenceContinuityVerified=True,remainingIssues=[],finalReview='review/NW-final-independent-review.json',reviewedAt=now)
write(p,s)
south=read(R/'review/south-completion-handoff.json')
for direction,proof in south['directions'].items():
 assert proof['eightConsecutiveSupportVerified'] and proof['positionPairsVerified'] and not proof['remainingRequiredImageRepairs']
 p=R/f'review/run-{direction}-selection.json';s=read(p)
 assert [f['sha256'] for f in s['frames']]==[f['sha256'] for f in proof['sources']]
 s.update(action='run',eightConsecutiveSupportVerified=True,supportFrameRanges=proof['actualSupportFrames'],finalReview='review/south-completion-handoff.json')
 write(p,s)
records=[]
for p in sorted((R/'review').glob('*selection.json')):
 s=read(p)
 if s.get('action') not in ['run','hit','attack','cast']:continue
 if s['action']=='run':assert s['eightConsecutiveSupportVerified'] and s['positionPairsVerified']
 # Historical dynamicArtAccepted fields have reviewer-dependent scopes; keep them intact.
 s.setdefault('previousArtStatus',s.get('artStatus'))
 s['artStatus']='offline_artwork_review_complete'
 s.update(offlineArtworkReviewComplete=True,offlineArtworkReviewScope='Final source poses and full-sequence contact sheets reviewed; automated playback timing is recorded separately. This is not user acceptance or client integration.',finalReviewClosedAt=now,remainingRequiredImageRepairs=[])
 write(p,s)
 records.append({'selection':p.relative_to(R).as_posix(),'selectionSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'action':s['action'],'direction':s['direction'],'offlineArtworkReviewComplete':True,'remainingRequiredImageRepairs':[]})
assert len(records)==14
write(R/'review/final-artwork-review.json',{'reviewedAt':now,'status':'complete','scope':'196 final sprite poses; root inspected all 14 final contact sheets; targeted independent reviews retained','sequences':records,'evidence':['review/NW-final-independent-review.json','review/south-completion-handoff.json','review/south-final-independent-review.json','review/combat-final-independent-review.json','review/combat-final-continuity-review.md'],'clientIntegrated':False,'clientRuntimeVerified':False,'userAcceptanceClaimed':False})
print(json.dumps({'closedSequences':len(records),'imageChanges':0}))
