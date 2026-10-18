from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib,numpy as np
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261013'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v3=read(Q/'composition-v3.json');v4=read(Q/'composition-v4.json')
src=Path(v3['candidate']);assert sha(src)==v3['candidateSha256'];original=Image.open(src).convert('RGB');out=original.copy()
layers=[]
for layer in v4['layers']:
 f=Path(layer['file']);assert sha(f)==layer['sha256'];layer=dict(layer)
 if layer['id']=='wall-right':
  im=Image.open(f).convert('RGB');old=Image.open(Q/'wall-right-input-v2.png').convert('RGB');diff=np.abs(np.asarray(im).astype(float)-np.asarray(old).astype(float)).mean(axis=2)
  bounds=[]
  for axis,limits in enumerate([(0,170),(0,200),(1085,1254),(1090,1254)]):
   vals=[(float((diff[max(p-2,0):min(p+3,1254),:] if axis in [1,3] else diff[:,max(p-2,0):min(p+3,1254)]).mean()),p) for p in range(*limits)];bounds.append(min(vals)[1])
  layer['crop']=bounds;layer['edgeSelection']='Expanded native crop boundary selected by minimum line difference; pixels unmodified.'
 a,b,c,d=layer['crop'];x,y=layer['origin'];out.paste(Image.open(f).convert('RGB').crop([a,b,c,d]),(x+a,y+b));layers.append(layer)
dest=T/'candidates/r02_c14.local-repairs-v5-20261013.png';assert not dest.exists();out.save(dest)
check=out.copy()
for layer in layers:
 x,y=layer['origin'];a,b,c,d=layer['crop'];box=[x+a,y+b,x+c,y+d];check.paste(original.crop(box),box[:2])
assert ImageChops.difference(check,original).getbbox() is None
out.crop([1870,420,3124,1674]).save(Q/'wall-right-composed-v5.png')
binding={**v4,'baseCandidate':str(src),'baseSha256':sha(src),'candidate':str(dest),'candidateSha256':sha(dest),'layers':layers,'windows':[str(Q/'wall-right-composed-v5.png')],'priorComposition':str(Q/'composition-v3.json'),'status':'visual_review_pending'}
(Q/'composition-v5.json').write_text(json.dumps(binding,indent=2)+'\n')
print(json.dumps(binding))

