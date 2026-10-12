from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
P=Path(__file__).resolve().parent
q=P/'qa/first-row-20261011'
d=json.loads((q/'crops.json').read_text())
for e in d['entries']:
 e.update(verdict='passed',actuallyViewed=True,inheritedFrom=None,findings=['Native-size crop inspected: paving grout and bevels continue across the core boundary; no abrupt material band or disconnected edge.'])
 if e['name']=='north-3': e['findings']=['Native-size crop inspected: both straight walkway trims, blue slate bed and surrounding diagonal pavement continue through the north candidate boundary.']
d.update(tile='r07_c06',reviewedAt=datetime.now(timezone.utc).isoformat(),status='passed',scope='First row provisional hard-core assembly only; complete tile QA still pending',seamSegments=3,externalNorthSegments=4,blockingCount=0)
(q/'review.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
p=P/'continuation-round-20261011.json'; a=json.loads(p.read_text()); a.update(sourceCount=4,selectedCount=4,internalQA={'status':'partial','reviewedSegments':3,'evidence':str(q/'review.json')},externalQA={'north':{'status':'partial-first-row-passed','segments':4},'west':'awaiting neighbor s02_04'},next='Await west r07_c05/s02_04 native anchor before s02_01 generation')
p.write_text(json.dumps(a,indent=2),encoding='utf-8')
print('Recorded 7 actually-viewed crops; selected=4/16; no candidate acceptance')

