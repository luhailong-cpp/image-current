import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,subprocess
from PIL import Image
Q=Path(__file__).resolve().parent
m=json.loads((Q/'repair-r08_c05-internal-v1.manifest.json').read_text());m['outputPrefix']='repair-r08_c05-internal-v2'
for p in m['repairs']:
 if p['id']=='d_shadow':p['repairBounds']=[0,0,1254,1254];p['margin']=6
 if p['id']=='e_water':p['repairBounds']=[0,0,1254,1254];p['margin']=6
mp=Q/'repair-r08_c05-internal-v2.manifest.json';assert not mp.exists();mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
subprocess.run([sys.executable,'-B',str(Q/'repair-compose-open-perimeter-v1.py'),'--manifest',str(mp)],check=True)
im=Image.open(Q/'repair-r08_c05-internal-v2-context-native.png')
for p in m['repairs']:im.crop(p['contextBox']).save(Q/('repair-r08_c05-internal-v2-'+p['id']+'-after-100pct.png'))
im.crop((600,650,1854,1904)).save(Q/'r08_c05_repair_j_stairjoint_v1-source-1254.png')
