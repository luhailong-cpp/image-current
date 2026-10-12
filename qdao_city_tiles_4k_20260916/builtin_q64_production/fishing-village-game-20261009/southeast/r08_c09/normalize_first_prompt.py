from pathlib import Path
import json
T=Path(__file__).resolve().parent
p=T/'p41-v1.prompt.txt';s=p.read_text(encoding='utf-8-sig').replace('\r\n','\n').rstrip('\n');p.write_bytes(s.encode('utf-8'))
r=T/'p41-v1.request.json';d=json.loads(r.read_text(encoding='utf-8-sig'));d['prompt']=s;r.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
