"""Consolidate current SHA-bound static observations. Does not approve motion from counts."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from current_run_pairs import current_run_pairs,SOURCES
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];pairs=current_run_pairs();expected={f'runtime/run/{d}/{n:02d}.png' for d in ['N','NE','E','SE','S','SW','W','NW'] for n in range(16)}
missing=sorted(expected-set(pairs))
for rel,c in sorted(pairs.items()):
    d=rel.split('/')[2];n=int(Path(rel).stem)
    rows.append({'file':rel,'direction':d,'frame':n,**c})
out={'recordedAt':datetime.now(timezone.utc).isoformat(),'latestUserRequirement':'同一支撑脚直脚着地两帧，再旁边点两帧，依次推进；各位置真实独立姿态','frameMs':60,'pairMs':120,'cycleMs':960,'frameCount':len(rows),'missingCurrentObservations':missing,'sourceReports':['review/'+s for s in SOURCES if (R/'review'/s).exists()],'frames':rows,'clientIntegrated':False,'userFinalApproved':False,'note':'每条均检查当前PNG SHA；静态报告不自动判定整圈美术或客户端通过'}
(R/'review/current_run_contactpairs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'currentObservations':len(rows),'missing':missing},ensure_ascii=False))
if missing:raise SystemExit(1)
