import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=R/'qa/full-resume-20261012-v1';b=R/'qa/full-resume-20261012-v3'
changed=[p.name for p in b.glob('*.png') if p.name not in ['candidate-4096.png','preview-QA-1024.png'] and sha(p)!=sha(a/p.name)]
print(json.dumps({'changed':changed,'count':len(changed),'candidateSha256':sha(b/'candidate-4096.png')}))

