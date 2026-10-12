from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
b=Path(__file__).resolve().parents[1];e=b/'resume-20261012'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(e/'candidate-manifest.json');r=read(e/'root-region-subset-review.json');h=read(e/'region-horizontal-review.json')
assert r['status']=='PASS_ROOT_SUBSET' and h['status']=='PASS'
assert r['candidateSha256']==h['candidate']['sha256']==m['regionCandidate']['sha256']==sha(m['regionCandidate']['file'])
rows=r['inheritedReviews']+r['freshReviews']+h['files'];assert len(rows)==len({x['file'] for x in rows})==30
for s in rows:assert sha(s['file'])==s['sha256'] and (s.get('status')=='PASS' or s.get('verdict')=='PASS')
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'PASS_INTERNAL_QA','candidate':m['regionCandidate']['file'],'candidateSha256':m['regionCandidate']['sha256'],'regionNativeReviewCount':30,'freshNativeReviewCount':13,'inheritedExactNativeReviewCount':17,'files':rows,'blockingFindings':[],'evidence':[{'file':str(p),'sha256':sha(p)} for p in [e/'root-region-subset-review.json',e/'region-horizontal-review.json']],'scope':'All inter-tile boundaries and both four-way intersections of the assigned six-tile region; external neighboring regions remain unavailable.'}
(e/'root-final-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'nativeRegionCrops':len(rows)}))
