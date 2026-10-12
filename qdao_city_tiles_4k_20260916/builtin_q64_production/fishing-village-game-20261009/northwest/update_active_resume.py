from pathlib import Path
import json,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ident=sys.argv[1]; inflight=len(sys.argv)>2 and sys.argv[2]=='true'; now=datetime.now(timezone.utc).isoformat()
idx=read(B/'current-artifacts.json')
if 'work-r06_c04' not in idx['adjacentWork']:
 idx['adjacentWork'].append('work-r06_c04')
 write(B/'current-artifacts.json',idx)
p=read(B/'progress.json');p.update(currentTile='r05_c02',currentPatch=ident,inFlightGeneration=inflight,updatedAt=now,nextStep='Complete r05_c02 and r06_c04 native candidates; review and adopt r02_c03/r02_c04 final candidates and independent neighbor deltas.')
write(B/'progress.json',p)
r=read(B/'production-resume-20261012.json');r.update(currentPatch=ident,updatedAtUtc=now,inFlightGeneration=inflight,selectedCurrentTilePatches=len(list((B/'work-r05_c02/selections').glob('*.json'))),activeWorkers={'root':'r05_c02 native 16-patch production','sol_paving':'r02_c02 native 16-patch production','sol_e3':'r02_c05 native 16-patch production','sol_north':'r06_c04 native 16-patch production'})
write(B/'production-resume-20261012.json',r)
print(json.dumps({'currentPatch':ident,'selected':r['selectedCurrentTilePatches'],'inFlight':inflight}))
