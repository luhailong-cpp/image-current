import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
z=Path(__file__).resolve().parents[1];q=z/'qa';ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
m={'outputPrefix':'pair-r08c06-r09c06-v2','basePairTrace':ref(q/'pair-r08c06-r09c06-v1-trace.json'),'repairs':[]}
for rid,cb,bounds,margin in [('south_canopy',[415,3615,1669,4869],[255,335,1200,1100],50),('south_lantern',[3072,3565,4326,4819],[550,70,1254,990],35)]:
 stem='r08_c06_r09_c06_repair_'+rid+'_v1'
 m['repairs'].append({'id':rid,'contextBox':cb,'source':ref(q/(stem+'-source-1254.png')),'repair':ref(z/'native'/(stem+'.png')),'generationRecord':ref(z/'native'/(stem+'.png.generation.json')),'repairBounds':bounds,'margin':margin})
p=q/(m['outputPrefix']+'.manifest.json')
with p.open('x',encoding='utf-8') as f:json.dump(m,f,indent=2)

