import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
qa=Path(__file__).resolve().parent;z=qa.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((qa/'repair-r08_c06-internal-v3.manifest.json').read_text(encoding='utf-8-sig'))
m['outputPrefix']='repair-r08_c06-internal-v5'
r=next(r for r in m['repairs'] if r['id']=='f_goldedge')
r['repairBounds']=[0,0,1254,1254];r['margin']=100
p=z/'native/r08_c06_repair_f_goldedge_v3.png';g=Path(str(p)+'.generation.json')
r['repair']={'path':p.as_posix(),'sha256':sha(p)};r['generationRecord']={'path':g.as_posix(),'sha256':sha(g)}
with (qa/(m['outputPrefix']+'.manifest.json')).open('x',encoding='utf-8') as f:json.dump(m,f,indent=2)

