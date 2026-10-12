from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
DIRS=['N','NE','E','SE','S','SW','W','NW']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
frames=[];sequences=[]
for direction in DIRS:
 rel=f'audit/run-{direction}-paired-ground-review.json';d=read(ROOT/rel)
 for row in d['frames']:
  n=int(row.get('frame') or row['slot'].split('/')[-1]);slot=f'run/{direction}/{n:02d}'
  assert row['sha256']==sha(ROOT/f'runtime/{slot}.png'),slot
  evidence=row.get('evidence') or row.get('inspection') or row.get('staticContactReading')
  if direction=='W':
   seg=d['intendedSegments'][0 if n<=8 else 1];pair=((n-1)%8)//2
   evidence=seg['spatialEvidence'][pair]+' '+seg['reason']
  limb=row.get('fullLimbInspection',{})
  if limb.get('afterEvidence'):
   evidence=(str(evidence)+' '+limb['afterEvidence']).strip()
  frames.append({**row,'slot':slot,'status':row.get('status','needs_review'),'staticInspected':True,
   'evidence':evidence,'pairedGroundReview':rel,'footOrientation':row.get('footOrientation') or d.get('evidence',{}).get('footAxis'),
   'dynamicStatus':'not_verified','dynamicVisualAcceptance':False})
 sequences.append({'sequence':f'run/{direction}','status':'not_verified','frameSha256':[r['sha256'] for r in d['frames']],
  'pairedGroundReview':rel,'staticReviewStatus':d.get('staticPairedGroundStatus') or d.get('status'),
  'sameAnatomicalFootConfirmed':d.get('sameAnatomicalFootConfirmed'),
  'dynamicVisualAcceptance':False,'reason':'Current static evidence does not constitute real-time or game-engine acceptance.'})
assert len(frames)==128
historical=[]
for p in sorted((ROOT/'review-parts').glob('*.json')):
 if p.name=='run-current-paired.json':continue
 d=read(p);oldframes=d.get('frames',[]);oldseqs=d.get('sequences',[])
 removedframes=[r for r in oldframes if str(r.get('slot','')).startswith('run/')]
 def key(r):return r.get('sequence') or (str(r.get('action'))+'/'+str(r.get('direction')))
 removedseqs=[r for r in oldseqs if key(r).startswith('run/')]
 if not removedframes and not removedseqs:continue
 historical.append({'file':p.relative_to(ROOT).as_posix(),'removedFrames':removedframes,'removedSequences':removedseqs})
 d['frames']=[r for r in oldframes if not str(r.get('slot','')).startswith('run/')]
 d['sequences']=[r for r in oldseqs if not key(r).startswith('run/')]
 d['currentRunReview']='review-parts/run-current-paired.json';write(p,d)
if historical:
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 write(ROOT/f'audit/superseded-run-review-parts-{stamp}.json',{'archivedAtUtc':now,'historicalOnly':True,'parts':historical})
write(ROOT/'review-parts/run-current-paired.json',{'updatedAtUtc':now,'automaticApproval':False,
 'scope':'Current exact-SHA static inspections; no inferred dynamic approval','frames':frames,'sequences':sequences})
print(json.dumps({'runFramesMerged':128,'historicalPartsRetainedAsText':len(historical),'dynamicApproval':False}))
