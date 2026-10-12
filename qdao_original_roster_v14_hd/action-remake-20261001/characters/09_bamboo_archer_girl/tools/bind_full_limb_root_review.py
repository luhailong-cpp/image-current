from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
p=root/'audit/full-limb-root-repair-review.json'
d=read(p);before={r['file']:r['sha256'] for r in read(root/'audit/full-limb-revision-before.json')['beforeFrames']}
for row in d['frames']:
 f='runtime/'+row['slot']+'.png'
 assert hashlib.sha256((root/f).read_bytes()).hexdigest()==row['sha256'],row['slot']
 row['beforeSha256']=before[f]
d['reviewedAtUtc']=datetime.now(timezone.utc).isoformat()
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
print('Bound six manually inspected repairs to before/current SHA.')
