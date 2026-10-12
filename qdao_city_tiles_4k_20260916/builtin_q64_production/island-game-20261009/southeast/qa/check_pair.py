from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
a=ROOT/'native'/sys.argv[1];b=ROOT/'native'/sys.argv[2];direction=sys.argv[3];identifier=sys.argv[4]
left=Image.open(a).convert('RGB');right=Image.open(b).convert('RGB')
if direction=='vertical':
    out=Image.new('RGB',(1254,512));out.paste(left.crop((0,883,1254,1139)),(0,0));out.paste(right.crop((0,115,1254,371)),(0,256))
    x=np.array(left)[1024:1254,:,:].astype(float);y=np.array(right)[:230,:,:].astype(float)
else:
    out=Image.new('RGB',(512,1254));out.paste(left.crop((883,0,1139,1254)),(0,0));out.paste(right.crop((115,0,371,1254)),(256,0))
    x=np.array(left)[:,1024:1254,:].astype(float);y=np.array(right)[:,:230,:].astype(float)
output=ROOT/'qa'/f'{identifier}.hard-seam-100pct.png';out.save(output)
report={'sources':[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [a,b]],'qaImage':str(output),'operation':'mechanical hard-cut at adjacent core boundary, no blending/resize, 100-percent native pixels','direction':direction,'overlapMAE':float(np.abs(x-y).mean()),'pixelExactOverlapFraction':float(np.all(x==y,axis=2).mean()),'status':'pending_visual_review'}
(ROOT/'qa'/f'{identifier}.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
