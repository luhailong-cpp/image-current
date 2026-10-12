from pathlib import Path
import json,sys
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
id=sys.argv[1]; assert id.startswith('r04_c13_')
now=datetime.now(timezone.utc).isoformat()
for anchor in sys.argv[2:]:
 p=Z/'qa'/f'{anchor}__{id}.json'
 r=json.loads(p.read_text(encoding='utf-8-sig'))
 r.update(status='passed_internal_only' if anchor.startswith('r04_c13_') else 'passed_cross_tile_core_segment_only',reviewedAtUtc=now,geometryChecks={'contours':'pass','slabJoints':'pass','inspection':'viewed exact100pct core join'},notes='Coherent contours and paving; restrained paint texture difference. This records one native1024 segment only, not formal acceptance.')
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
p=Z/'native'/f'{id}.png.generation.json'; r=json.loads(p.read_text(encoding='utf-8-sig')); r.update(status='usable_native_candidate',internalSeams='submitted anchored joins reviewed pass; other edges pending'); p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
p=Z/'selection-r04_c13.json'
r=json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else {'tileId':'r04_c13','cores':[[None]*4 for _ in range(4)],'overlays':[],'formalAccepted':False}
parts=id.split('_'); row=int(parts[2][1:]); col=int(parts[3]);r['cores'][row-1][col-1]=id;r['updatedAtUtc']=now
t=p.with_name('selection-r04_c13.next.json');t.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');t.replace(p)
print(id+' selected; anchors recorded only; shared progress untouched')

