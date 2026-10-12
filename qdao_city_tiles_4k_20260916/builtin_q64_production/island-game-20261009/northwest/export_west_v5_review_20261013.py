from pathlib import Path
import json,hashlib
from PIL import Image
import assemble_tile as a
z=Path(__file__).resolve().parent;info=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
v=z/'tiles/r05_c02_candidate-v5_4096.png';d=z/'qa/r05_c02_v5_internal_review';d.mkdir()
q=a.save_qa(d,Image.open(v).convert('RGB'));q['base']=info(v);q['record']=info(v.with_suffix('.native-repair.json'));p=d/'qa_index.json';p.write_text(json.dumps(q,indent=2))
old={Path(i['path']).name:i for i in json.loads((z/'qa/r05_c02_v4_owner_native33_review_20261013.json').read_text())['items']}
print(json.dumps({'qa':info(p),'changed':[Path(i['path']).name for i in q['seamAndJunctionCrops'] if old[Path(i['path']).name]['sha256']!=i['sha256']],'samePass':sum(old[Path(i['path']).name]['sha256']==i['sha256'] and old[Path(i['path']).name]['status']=='PASS' for i in q['seamAndJunctionCrops'])}))

