import json, sys, hashlib
from pathlib import Path
r=Path(sys.argv[1]); d=json.loads(r.read_text(encoding='utf-8')); p=Path(d['promptFile'])
prefix=Path(sys.argv[2]).read_text(encoding='utf-8')
d['prompt']=prefix+'\n'+d['prompt']; p.write_text(d['prompt'],encoding='utf-8',newline='')
d['promptSha256']=hashlib.sha256(p.read_bytes()).hexdigest()
r.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
