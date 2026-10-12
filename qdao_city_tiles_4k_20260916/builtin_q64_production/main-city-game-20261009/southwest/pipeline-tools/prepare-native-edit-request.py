from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
tile,patch,attempt,base_attempt,source,prompt_input,*extra=sys.argv[1:]
T=B/tile;base=T/'pipeline/prompts'/f'{patch}.{base_attempt}.request.json';r=json.loads(base.read_text(encoding='utf-8-sig'))
source=Path(source);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pp=T/'pipeline/prompts'/f'{patch}.{attempt}.prompt.txt';rp=pp.with_name(f'{patch}.{attempt}.request.json')
assert source.is_file() and not pp.exists() and not rp.exists()
prompt=Path(prompt_input).read_text(encoding='utf-8-sig');pp.write_text(prompt,encoding='utf-8')
r.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedAtUtc=datetime.now(timezone.utc).isoformat(),neighborSources=[],cornerTreatment={'bothSourcesPresent':False,'reason':'Actual native edit target; preserve exact approved geometry except explicitly requested corrections.'})
r['references']=r['references'][:4];r['references'][0]={'file':str(source),'sha256':sha(source),'role':'actual builtin native output to edit; preserve fixed crop and explicitly stated invariants'}
if extra:
    f=Path(extra[0]);r['references'].append({'file':str(f),'sha256':sha(f),'role':extra[1] if len(extra)>1 else 'supporting exact approved layout reference only'})
r['referenced_image_paths']=[q['file'] for q in r['references']];r['editBaseRequest']={'file':str(base),'sha256':sha(base)};atomic_json(rp,r);print(rp)
