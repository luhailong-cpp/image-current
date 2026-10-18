from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261013'
j=json.loads((Q/'composition-v3.json').read_text());p=Path(j['candidate']);assert hashlib.sha256(p.read_bytes()).hexdigest()==j['candidateSha256']
im=Image.open(p)
boxes={'wall-top':[1300,423,2410,723],'wall-right':[2250,580,2600,1650],'leaf-right':[3667,680,3990,1820],'rock-bottom':[2450,3500,3710,3900]}
out=[]
for k,b in boxes.items():
 f=Q/(k+'-boundary-v3.png');assert not f.exists();im.crop(b).save(f);out.append({'id':k,'file':str(f),'box':b})
(Q/'boundary-windows-v3.json').write_text(json.dumps({'candidate':str(p),'candidateSha256':j['candidateSha256'],'windows':out,'operation':'Integer native crops only; no resizing'},indent=2)+'\n')
print(json.dumps(out))

