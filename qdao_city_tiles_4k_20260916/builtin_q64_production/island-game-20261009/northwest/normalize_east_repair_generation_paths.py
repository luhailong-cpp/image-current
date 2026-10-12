from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parent
for s in ['r04_c02_repair_eastupper_a01','r04_c02_repair_eastroof_a01']:
 p=Z/'native'/f'{s}.png.generation.json'
 d=json.loads(p.read_text(encoding='utf-8-sig'))
 old=d['prompt']; q=Z/old
 assert hashlib.sha256(q.read_bytes()).hexdigest()==d['promptSha256']
 d['prompt']=q.as_posix()
 d['pathNormalizationEvidence']=dict(originalRecord=dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),originalPromptValue=old,reason='original ingest ran with cwd-relative prompt; immutable corrected sibling resolves same hash-identical submitted file',artModified=False)
 out=Z/'native'/f'{s}.png.generation-pathfixed-v1.json'
 with out.open('x',encoding='utf-8') as h:json.dump(d,h,ensure_ascii=False,indent=2)
 print(out.as_posix())

