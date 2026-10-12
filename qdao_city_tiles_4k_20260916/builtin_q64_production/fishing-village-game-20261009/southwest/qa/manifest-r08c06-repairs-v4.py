import sys
sys.dont_write_bytecode=True
import json,hashlib,copy
from pathlib import Path
qa=Path(__file__).resolve().parent;z=qa.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((qa/'repair-r08_c06-internal-v3.manifest.json').read_text(encoding='utf-8-sig'))
m['outputPrefix']='repair-r08_c06-internal-v4'
r=copy.deepcopy(next(r for r in m['repairs'] if r['id']=='f_goldedge'))
r['id']='f_goldedge_join';r['repairBounds']=[790,480,1100,770];r['margin']=40
p=z/'native/r08_c06_repair_f_goldedge_v3.png';g=Path(str(p)+'.generation.json')
r['repair']={'path':p.as_posix(),'sha256':sha(p)};r['generationRecord']={'path':g.as_posix(),'sha256':sha(g)}
m['repairs'].append(r)
with (qa/(m['outputPrefix']+'.manifest.json')).open('x',encoding='utf-8') as f:json.dump(m,f,indent=2)

