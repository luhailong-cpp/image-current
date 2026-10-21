from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261013'
j=json.loads((Q/'composition-v6.json').read_text());p=Path(j['candidate']);assert hashlib.sha256(p.read_bytes()).hexdigest()==j['candidateSha256'];im=Image.open(p)
boxes={'rock-top-v6':[2390,2700,3740,2980],'rock-left-v6':[2290,2840,2640,4070],'rock-bottom-v6':[2410,3860,3710,4096],'wall-top-v6':[1840,380,3135,660],'wall-bottom-v6':[1840,1470,3135,1730],'wall-right-v6':[2840,470,3135,1630]}
items=[]
for key,b in boxes.items():
 f=Q/(key+'.png');assert not f.exists();im.crop(b).save(f);items.append({'id':key,'file':str(f),'box':b})
(Q/'boundary-windows-v6.json').write_text(json.dumps({'candidate':str(p),'candidateSha256':j['candidateSha256'],'windows':items,'operation':'Integer native crops; no scaling'},indent=2)+'\n')
print(json.dumps(items))

