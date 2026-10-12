import json
from pathlib import Path
z=Path(__file__).resolve().parent
q=json.loads((z/'qa/r05_c02_v4_internal_review/qa_index.json').read_text())
o=json.loads((z/'qa/r05_c02_v1_owner_native33_review_20261013.json').read_text())
old={Path(i['path']).name:i for i in o['items']}
for i in q['seamAndJunctionCrops']:
 p=Path(i['path']);prev=old[p.name];print(p.name, 'REUSE_'+prev['status'] if i['sha256']==prev['sha256'] else 'CHANGED',prev['note'])

