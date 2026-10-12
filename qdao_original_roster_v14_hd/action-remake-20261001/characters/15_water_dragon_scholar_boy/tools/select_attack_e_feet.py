from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1]
p=B/'audit/attack-selection.json'
data=json.loads(p.read_text(encoding='utf-8-sig'))
for row in data['frames']:
    if row['direction']!='E': continue
    key=f"attack-E-{row['frame']:02}-foot-v1"
    source=f'sources/new/{key}.png'
    if row['source']!=source:
        row['priorSelection']={k:row[k] for k in ('source','sha256','generationRecord','review')}
    row.update(source=source,sha256=hashlib.sha256((B/source).read_bytes()).hexdigest(),generationRecord=f'provenance/generation/{key}.json')
    row['review']={'reviewer':'root','reviewedAt':datetime.now(timezone.utc).isoformat(),'notes':'逐图看过：修正屏幕左后靴外撇，鞋头朝屏幕右/E并与前靴一致。保留原脚位、右扇左空手及原选帧顺序。静态修正通过，连续动作另行验收。'}
data['updatedAt']=datetime.now(timezone.utc).isoformat()
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('attack E 12 feet selections updated')
