from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
version=sys.argv[1] if len(sys.argv)>1 else 'v03'
a=ROOT/'native/r09_c12_p11_v01.png';b=ROOT/f'native/r09_c12_p12_{version}.png'
left=Image.open(a).convert('RGB');right=Image.open(b).convert('RGB')
out=Image.new('RGB',(512,1254));out.paste(left.crop((883,0,1139,1254)),(0,0));out.paste(right.crop((115,0,371,1254)),(256,0));output=ROOT/f'qa/p11-p12-{version}.hard-seam-100pct.png';out.save(output)
x=np.array(left)[:,1024:1254,:].astype(float);y=np.array(right)[:,:230,:].astype(float)
report={'sources':[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [a,b]],'qaImage':str(output),'operation':'mechanical hard-cut at adjacent core boundary, no blending/resize, 100-percent native pixels','leftSourceBox':[883,0,1139,1254],'rightSourceBox':[115,0,371,1254],'overlapMAE':float(np.abs(x-y).mean()),'pixelExactOverlapFraction':float(np.all(x==y,axis=2).mean()),'status':'pending_visual_review'}
(ROOT/f'qa/p11-p12-{version}.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
