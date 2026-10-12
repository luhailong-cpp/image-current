import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,subprocess
from PIL import Image
Q=Path(__file__).resolve().parent; Z=Q.parent
def ref(p):
 p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,d):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,ensure_ascii=False)
t=json.loads((Q/'repair-r08_c05-internal-v2-trace.json').read_text())
a=Q/'repair-r08_c05-internal-v2-base-adapter.json';save(a,{'context':t['context'],'output':t['candidate'],'provenance':ref(Q/'repair-r08_c05-internal-v2-trace.json')})
stem='r08_c05_repair_j_stairjoint_v1'
common={'source':ref(Q/(stem+'-source-1254.png')),'repair':ref(Z/'native'/(stem+'.png')),'generationRecord':ref(Z/'native'/(stem+'.png.generation.json')),'tileContextBox':[485,535,1739,1789],'contextBox':[600,650,1854,1904],'margin':30}
m={'schemaVersion':1,'outputPrefix':'repair-r08_c05-internal-v3','baseAssembly':ref(a),'expectedBaseCandidateSha256':t['candidate']['sha256'],'repairs':[{**common,'id':i,'repairBounds':b} for i,b in [('j_stairnose',[210,520,530,870]),('j_wallsliver',[980,340,1215,580]),('j_lowerriser',[710,990,970,1220])]]}
mp=Q/'repair-r08_c05-internal-v3.manifest.json';save(mp,m)
subprocess.run([sys.executable,'-B',str(Q/'repair-compose.py'),'--manifest',str(mp)],check=True)
im=Image.open(Q/'repair-r08_c05-internal-v3-context-native.png');im.crop((600,650,1854,1904)).save(Q/'repair-r08_c05-internal-v3-j-after-100pct.png')
im.crop((115,115,4211,4211)).resize((1400,1400),Image.Resampling.LANCZOS).save(Q/'repair-r08_c05-internal-v3-preview-only.png')
