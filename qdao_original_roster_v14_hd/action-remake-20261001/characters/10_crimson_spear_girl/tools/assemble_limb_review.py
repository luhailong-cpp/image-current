from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,argparse
R=Path(__file__).resolve().parents[1];W=R/'full-limb-review-20261004'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
args=argparse.ArgumentParser();args.add_argument('--current',action='store_true');a=args.parse_args()
records={}
sources=['ns-audit/audit.json','east-audit/frames.json','west-audit/audit.json','battle-audit/audit.json']
for name in sources:
    source=load(W/name)
    for frame in source['frames']:
        slot=frame['slot'];assert slot not in records,slot
        records[slot]={**frame,'auditSource':'full-limb-review-20261004/'+name}
assert len(records)==196
delivery=load(R/'delivery-current.json')
rows={g+'/'+str(f['frame']).zfill(2):f for g,fs in delivery['groups'].items() for f in fs}
assert set(rows)==set(records)
selected={}
for p in W.glob('*/selection.json'):
    for slot,value in load(p).get('slots',{}).items():
        assert slot not in selected,'Duplicate selected slot: '+slot
        selected[slot]={'file':value if isinstance(value,str) else value.get('file') or value.get('path'),'reviewSelection':p.relative_to(R).as_posix()}
published={x['slot']:x for x in load(W/'publish-report.json')['slots']} if a.current else {}
result=[];unresolved=[]
for slot,f in rows.items():
    prior=records[slot];status=prior.get('reviewStatus',prior.get('status','unknown'))
    assert sha(R/f['file'])==f['sha256']
    row={'slot':slot,'file':f['file'],'sha256':f['sha256'],'beforeVisualReview':prior}
    if a.current and slot in published:
        change=published[slot]
        assert f['sha256']==change['newSHA'] and prior['sha256']==change['oldSHA']
        row.update(status='repaired-and-visually-reviewed',selectedSource=selected[slot],oldSHA=change['oldSHA'])
    else:
        assert prior['sha256']==f['sha256'],slot
        row['status']=status
        if 'fail' in status.lower() or status.lower()=='unknown':unresolved.append(slot)
    result.append(row)
summary=[
    'E14：修正近侧摆动腿与远侧支撑腿的前后遮挡，保持13→14→15支撑归属连续。',
    'W09–12：修正提前换支撑腿的画面归属，保留同一腿的连续四位置推进。',
    'SW15/16：收回过长的侧向后蹬，保持自然屈膝、前掌支撑及两张独立姿态。',
    'NW11/12：减小突增的后蹬跨距；NW02/03/05–16同时修正下枪杆与枪尾偏离上枪杆延长线的问题。'
]
data={'reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'reviewed-current' if a.current else 'pre-repair-audit','inventorySHA256':sha(R/'delivery-current.json'),'reviewedCurrentFrames':196,'knownUnresolvedFailures':len(unresolved),'unresolvedSlots':unresolved,'changedRuntimeFrames':len(published),'method':'Actual full-canvas and fixed-coordinate limb views by directional reviewers, plus independently accepted repair candidates; SHA ties judgments to current pixels.','sourceAudits':sources,'changeSummary':summary if a.current else [],'limits':['Hidden joints are not claimed fully visible.','NW01/04 lower spear is occluded; no measurable lower-shaft claim.','Game client placement and cross-action transition are untested.'],'frames':result}
if a.current:assert not unresolved,'Known failures remain: '+str(unresolved)
write(W/('current-frame-review.json' if a.current else 'pre-repair-frame-review.json'),data)
print(json.dumps({k:v for k,v in data.items() if k not in ['frames','changeSummary']},ensure_ascii=False))
