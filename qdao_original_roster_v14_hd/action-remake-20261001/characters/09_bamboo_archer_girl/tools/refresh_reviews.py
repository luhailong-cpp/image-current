import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
frames={};sequences={};stale=[]
for p in sorted((ROOT/'review-parts').glob('*.json')):
 d=json.loads(p.read_text(encoding='utf-8-sig'))
 for row in d.get('frames',[]):
  key=row.get('slot');f=ROOT/'runtime'/(str(key)+'.png')
  if not f.exists():continue
  sha=hashlib.sha256(f.read_bytes()).hexdigest()
  r={**row,'sourceReviewFile':p.relative_to(ROOT).as_posix()}
  if r.get('sha256')!=sha:
   stale.append({'slot':key,'reviewFile':p.relative_to(ROOT).as_posix(),'oldSha256':r.get('sha256'),'currentSha256':sha})
   r.update(status='needs_review',staleReview=True)
  frames[key]=r
 for row in d.get('sequences',[]):
  key=row.get('sequence') or (f"{row['action']}/{row['direction']}" if row.get('action') and row.get('direction') else None)
  if key:sequences[key]={**row,'sequence':key,'sourceReviewFile':p.relative_to(ROOT).as_posix()}
out={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'automaticApproval':False,'frames':list(frames.values()),'sequences':list(sequences.values()),'staleReviews':stale}
(ROOT/'review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(frames),'sequences':len(sequences),'staleReviews':len(stale)}))
