from pathlib import Path
import json,hashlib
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=[]
for rp in sorted(T.rglob('*.png.generation.json')):
 d=json.loads(rp.read_text(encoding='utf-8-sig'))
 for ref in d['references']:
  p=Path(ref['path'])
  if not p.exists() or sha(p)!=ref['sha256']:m.append({'record':str(rp),'reference':ref,'currentSha256':sha(p) if p.exists() else None})
(T/'qa'/'reference-audit-initial.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
print(json.dumps(m,indent=2))

