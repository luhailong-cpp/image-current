"""Refresh timing fields only; preserves images, provenance and visual-review dates."""
import json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
files=[ROOT/f'work/run-{d}/grounding-review-20261003.json' for d in ['W','N','NW','NE']]
files.append(ROOT/'work/run-NW/north-final-review-20261003.json')
changed=[]
for p in files:
    doc=json.loads(p.read_text(encoding='utf-8-sig'))
    rows=doc.get('fourDirectionPhaseReview',doc.get('frames',[]))
    for row in rows:
        row['durationMs']=75
        row['trialDurationMs']=75
        if row.get('action')=='shorten_trial':row['action']='review_flight_pose_at_uniform_75ms'
    doc['timing']={'status':'user_requested_uniform_1200ms_client_unconfirmed','cycleMs':1200,'frameMs':75,'durationsMs':[75]*16,'phaseWeightsApplied':False,'uniform':True,'reason':'最新人类明确正常跑步16×75ms＝1200ms；时长不代替姿态与总循环验收。'}
    doc['timingUpdatedAt']=now
    p.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
    changed.append({'file':p.relative_to(ROOT).as_posix(),'phaseRows':len(rows)})
print(json.dumps({'timingOnly':True,'cycleMs':1200,'uniformFrameMs':75,'changed':changed},ensure_ascii=True))
