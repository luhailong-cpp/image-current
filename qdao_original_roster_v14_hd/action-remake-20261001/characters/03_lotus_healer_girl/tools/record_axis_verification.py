"""Record the actual CUA checks performed for the selected video-axis revision."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, hashlib
B=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
overview_path=B/'review/all-actions-selection.json'
overview=read(overview_path)
decision_path=B/'review/axis-revision-decisions-20261004.json'
decision=read(decision_path)
assert decision['status'] in ('selected_pending_rebuild','verified_ready_for_retention')
assert overview['selectedExported']==196
groups=[]
for action,directions,count,cycle in [('run',['E','NE','N','NW','W','SW','S','SE'],16,1200),('hit',['E','W'],6,240),('attack',['E','W'],12,360),('cast',['E','W'],16,720)]:
    for direction in directions:
        groups.append(dict(action=action,direction=direction,decoded=count,selected=count,cycleMs=cycle,rate=1))
sources=[]
for item in decision['decisions']:
    g=next(g for g in overview['groups'] if g['action']=='run' and g['direction']==item['direction'])
    f=g['frames'][item['frame']-1]
    assert (B/f['source']).resolve()==(B/item['source']).resolve()
    sources.append(dict(direction=item['direction'],frame=item['frame'],source=item['source'],sourceSha256=f['sourceSha256'],observedInBrowser=True))
stamp=datetime.now(ZoneInfo('America/New_York')).isoformat()
record=dict(checkedAt=stamp,method='CUA actual browser selectors, rendered DOM and screenshot; file contact sheets viewed separately',url='http://127.0.0.1:8873/qdao_original_roster_v14_hd/action-remake-20261001/characters/03_lotus_healer_girl/preview/actions.html',overviewSha256=hashlib.sha256(overview_path.read_bytes()).hexdigest(),groups=groups,selectedRevisions=sources,loopCheck=dict(direction='SW',nextFrom16=1,prevFrom1=16),slowCheck=dict(rate=0.25,cycleMs=4800,frameMs=300),finalPlayback=dict(action='run',direction='NE',rate=1,size=256,playing=True),viewedFinalContactSheets=['NE','N','NW','W','SW'],visualAcceptance=False,clientAcceptance=False,limitations=['N06 retains a small lateral offset; NW12 and SW14 are improved but not equal-distance trajectories.','Contact sheets and preview do not establish in-game displacement, contact collision, or skill event correctness.'])
write(B/'review/axis-browser-verification-20261004.json',record)
decision['status']='verified_ready_for_retention'
decision['verifiedAt']=stamp
decision['browserVerification']='review/axis-browser-verification-20261004.json'
decision['exportVerification']='review/all-actions-technical-verification.json'
write(decision_path,decision)
print(json.dumps(dict(groups=len(groups),newSources=len(sources),selected=196)))
