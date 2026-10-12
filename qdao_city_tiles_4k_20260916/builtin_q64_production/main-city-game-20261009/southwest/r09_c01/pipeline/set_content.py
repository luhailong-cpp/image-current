from pathlib import Path
import json,hashlib,sys
q=Path(sys.argv[1]); content=Path(sys.argv[2])
d=json.loads(q.read_text(encoding='utf-8-sig'))
f=q.with_name(q.name.replace('.request.json','.actual-prompt.txt'))
assert not f.exists()
prompt=content.read_text(encoding='utf-8-sig').rstrip()+'\n\n'+d['prompt']
f.write_text(prompt,encoding='utf-8')
d.update(prompt=prompt,promptFile=str(f),promptSha256=hashlib.sha256(f.read_bytes()).hexdigest())
q.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(str(q))
