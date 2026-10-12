import json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parent;NORTH=ROOT.parent/'r11_c09'
ns=json.loads((NORTH/'selected-patches.json').read_text(encoding='utf-8-sig'))['patches']
ss=json.loads((ROOT/'selected-patches.json').read_text(encoding='utf-8-sig'))['patches']
items=[];contact=Image.new('RGB',(1024,1024))
for c in range(1,5):
 a=f'p4{c}';b=f'p1{c}';ap=NORTH/ns[a];bp=ROOT/ss[b]
 aa=np.array(Image.open(ap).convert('RGB'));bb=np.array(Image.open(bp).convert('RGB'))
 strip=np.concatenate([aa[1011:1139,115:1139],bb[115:243,115:1139]],axis=0)
 out=ROOT/'qa'/f'gate-north-c{c}-100pct.png';Image.fromarray(strip).save(out);contact.paste(Image.fromarray(strip),(0,(c-1)*256))
 items.append({'northPatch':a,'southPatch':b,'north':str(ap),'northSha256':hashlib.sha256(ap.read_bytes()).hexdigest(),'south':str(bp),'southSha256':hashlib.sha256(bp.read_bytes()).hexdigest(),'strip':str(out),'sameCoordinateOverlapMeanAbsRGB':float(np.abs(aa[1024:1254,115:1139].astype(float)-bb[:230,115:1139].astype(float)).mean())})
contact.save(ROOT/'qa/gate-north-4strips-100pct.png')
(ROOT/'qa/gate-north-boundary-evidence.json').write_text(json.dumps({'status':'preliminary_readonly_visual_QA_no_formal_acceptance','sources':items},indent=2),encoding='utf-8')
print(json.dumps(items))

