import json
from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/'inventory-hit.json'
j=json.loads(p.read_text(encoding='utf-8-sig'))
for f in j['frames']:
    if (f['action']=='hit' and f['direction']=='E' and f['frame'] in (4,5,6)) or (f['action']=='run' and f['direction']=='SW' and f['frame']==11):
        f['visual_status']='local_anatomy_independently_reviewed_sequence_pending'
        f['visual_evidence']='records/hit-and-SW11-independent-review-20261003.json'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('4 slots: independent local anatomy review recorded; sequence remains pending')

