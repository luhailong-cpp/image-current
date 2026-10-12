import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest")
p=z/'qa/joint-r09c04-c05-finalrail-v1-trace.json'
t=json.loads(p.read_text(encoding='utf-8-sig'))
ind=z/'qa/joint-r09c04-c05-finalrail-v1-independent-rail-audit.json'
v={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','status':'shared_edge_art_review_passed','inputTrace':{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},'reviewedImages':[q['path'] for q in t['qa']]+[(z/'qa/joint-r09c04-c05-finalrail-v1-rail-after-100pct.png').as_posix()],'inspectionScale':'100 percent native crops','findings':['Both diagonal rails continuous in shape, warm material and highlights after repair.','Closed mask boundaries have no obvious new seams.','All five native shared-edge sections checked: stone pavement, wall, lamp and sandy ground continuous.'],'independentAudit':{'path':ind.as_posix(),'sha256':hashlib.sha256(ind.read_bytes()).hexdigest()},'acceptanceScope':'This one shared edge only; full 2x2 pending staircase and southern tile edges.','formalAcceptedCount':0}
(z/'qa/joint-r09c04-c05-finalrail-v1-root-shared-edge-audit.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'reviewed':len(v['reviewedImages']),'status':v['status']}))

