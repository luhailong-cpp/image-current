from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
independent=read(R/'review/axis-final-independent-review-20261004.json')
assert independent.get('passed') is True and not independent.get('remainingRequiredRepairs'), 'Independent review still requires repair'
revision=read(R/'review/axis-revision-selection-20261004.json');assert len(revision['changes'])==8
reviewed={f['path']:f['sha256'] for f in independent['reviewedDrafts'] if f['passed']}
for f in revision['changes']:
 assert sha(R/f['file'])==f['sha256']
 assert reviewed[f['source']]==f['nativeSha256']
now=datetime.now(timezone.utc).isoformat()
records=[]
for p in sorted((R/'review').glob('*selection.json')):
 s=read(p)
 if s.get('action') not in ['run','hit','attack','cast']:continue
 if s.get('direction') in ['E','W'] and s.get('action')=='run':
  s.update(finalReviewClosedAt=now,finalAxisReview='review/axis-final-independent-review-20261004.json',remainingRequiredImageRepairs=[],offlineArtworkReviewComplete=True)
  write(p,s)
 records.append({'selection':p.relative_to(R).as_posix(),'selectionSha256':sha(p),'action':s['action'],'direction':s['direction'],'offlineArtworkReviewComplete':s.get('offlineArtworkReviewComplete',False)})
assert len(records)==14 and all(x['offlineArtworkReviewComplete'] for x in records)
write(R/'review/final-artwork-review.json',{'reviewedAt':now,'status':'complete','scope':'196 selected sprites; video axis review retained 188 and revised eight side-facing swing poses. No exact external-video foot angle or world-space grounding claim.','sequences':records,'priorArtReview':'review/final-artwork-review-before-axis-20261004.json','axisRevision':'review/axis-revision-selection-20261004.json','axisIndependentReview':'review/axis-final-independent-review-20261004.json','clientIntegrated':False,'clientRuntimeVerified':False,'userAcceptanceClaimed':False})
print(json.dumps({'reviewClosed':True,'revisedFrames':8,'sequences':14}))
