import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
tile,patch,attempt,base_attempt,target,prefix=sys.argv[1:]
B=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest')
P=B/tile/'pipeline'; source=P/'prompts'/f'{patch}.{base_attempt}.request.json'
r=json.loads(source.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prompt=Path(prefix).read_text(encoding='utf-8-sig')+'\n\n'+r['prompt'].split('Use case:',1)[1]
prompt=prompt.replace('\n\nprecise-object-edit.','\n\nUse case: precise-object-edit.',1)
out=P/'prompts'/f'{patch}.{attempt}.request.json'; pf=out.with_name(out.name.replace('.request.json','.prompt.txt'))
assert not out.exists() and not pf.exists()
pf.write_text(prompt,encoding='utf-8'); r.update(prompt=prompt,promptFile=str(pf),promptSha256=sha(pf),preparedAtUtc=datetime.now(timezone.utc).isoformat())
r['referenced_image_paths'][0]=target
r['references'][0]={'file':target,'sha256':sha(target),'role':'explicit refinement edit target; viewed before builtin call'}
r['explicitRefinementOf']={'file':str(source),'sha256':sha(source)}
out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(out),'target':target}))
