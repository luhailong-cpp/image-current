import json,hashlib
from pathlib import Path
Z=Path(__file__).resolve().parent.parent;D=Z/'stair-rebuild';Q=Z/'qa'
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
m=json.loads((Q/'repair-r10_c04-sixstep-v1.manifest.json').read_text(encoding='utf-8-sig'));m['outputPrefix']='repair-r10_c04-sixstep-v2'
for name,bounds,margin in [('topnose',[220,100,820,690],45),('footroad',[40,350,1230,1080],20),('lantern',[180,110,1080,1130],30)]:
 s='r10_c04_sixstep_'+name+'_v1';r=json.loads((D/(s+'.request.json')).read_text())
 m['repairs'].append({'id':name,'source':ref(D/(s+'-source.png')),'repair':ref(D/(s+'.png')),'generationRecord':ref(D/(s+'.png.generation.json')),'tileContextBox':r['coordinates']['tileContextBox'],'repairBounds':bounds,'margin':margin})
(Q/'repair-r10_c04-sixstep-v2.manifest.json').write_text(json.dumps(m,indent=2)+'\n')

