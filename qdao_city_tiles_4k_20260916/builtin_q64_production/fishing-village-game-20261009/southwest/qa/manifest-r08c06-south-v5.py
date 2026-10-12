import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
q=Path(__file__).resolve().parent;z=q.parent;ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
m=json.loads((q/'pair-r08c06-r09c06-v4.manifest.json').read_text(encoding='utf-8-sig'));m['outputPrefix']='pair-r08c06-r09c06-v5'
stem='r08_c06_r09_c06_repair_south_canopy_right_v1'
m['repairs'].append({'id':'south_canopy_right','contextBox':[1439,3615,2693,4869],'source':ref(q/(stem+'-source-1254.png')),'repair':ref(z/'native'/(stem+'.png')),'generationRecord':ref(z/'native'/(stem+'.png.generation.json')),'repairBounds':[0,0,1254,1254],'margin':100})
with (q/(m['outputPrefix']+'.manifest.json')).open('x',encoding='utf-8') as f:json.dump(m,f,indent=2)

