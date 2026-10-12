from pathlib import Path
import json
B=Path(__file__).resolve().parent.parent
paths=['r09_c03/pipeline/local-review-20261013-v01/left-lane-local-review-handoff.json','r10_c08/pipeline/qa/right-lane-review-20261013-v01/lane-review-and-repair-queue.json','pipeline-tools/col5-local-audit-20261013-v01/actual-views-and-findings.json']
for p in paths:
 d=json.loads((B/p).read_text(encoding='utf-8-sig'))
 print(p);print(json.dumps({k:(list(v.keys()) if isinstance(v,dict) else {'length':len(v)} if isinstance(v,list) else v) for k,v in d.items()},ensure_ascii=False)[:5000])
