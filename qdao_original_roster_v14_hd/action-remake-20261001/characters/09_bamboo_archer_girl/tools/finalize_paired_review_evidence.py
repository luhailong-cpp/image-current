from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
for direction in ['N','NE','E','SE','S','SW','W','NW']:
 p=ROOT/f'audit/run-{direction}-paired-ground-review.json';d=read(p)
 refs=[f'preview/qa/run-{direction}-{s}' for s in ['contact.png','paired-contact.png','normal.apng','slow.apng']]
 if 'evidenceFiles' in d:
  d['historicalWorkingEvidenceFiles']=d['evidenceFiles']
  d['evidenceFiles']=refs
 d['currentEvidenceFiles']=refs
 d['inspectionImageRetention']='Canonical preview/qa retained; working inspection images replaced by current equivalent and deletion SHA ledger, per user material retention rule.'
 write(p,d)
for p in (ROOT/'review-parts').glob('combat-*.json'):
 d=read(p)
 for row in d.get('frames',[]):
  action,direction,_=row['slot'].split('/')
  row['currentEvidenceFiles']=[f"runtime/{row['slot']}.png",f'preview/qa/{action}-{direction}-contact.png']
 d['inspectionImageRetention']='Historical closeup/comparison filenames in prose describe prior inspection; current full originals and canonical preview/qa contacts retained.'
 write(p,d)
p=ROOT/'audit/latest-grounding-requirement.json';d=read(p)
d['latestSpatialRequirement']['status']='current_revision_saved_static_reviews_recorded_dynamic_pending'
d['minimumConsecutiveContactFramesPerFoot']=8;d['minimumSupportDurationMs']=600
d['remainingLimits']='Side-view E/W anatomical hip identity occluded; strict world-ground locking and real-time/client visual acceptance not verified.'
write(p,d)
write(ROOT/'audit/live-work-state.json',{'updatedAtUtc':now,'character':'09_bamboo_archer_girl','state':'current_asset_revision_saved_static_reviews_recorded','writeBoundary':'This character directory only; no Git or client writes','latestRequirement':'four progressive support positions, two independent poses each,16 x75ms=1200ms','runDirectionReviews':[f'audit/run-{d}-paired-ground-review.json' for d in ['N','NE','E','SE','S','SW','W','NW']],'dynamicVisualAcceptance':False,'clientIntegrated':False,'remainingLimits':['E/W hip identity occluded; no unsupported anatomical continuity claim','Real-time and engine ground/displacement acceptance not performed'],'nextDeliverySteps':['Verify current previews and review hashes','Remove superseded working images after current-reference verification','Final inventory and handoff']})
print('Current evidence paths and latest requirement state finalized without dynamic approval.')
