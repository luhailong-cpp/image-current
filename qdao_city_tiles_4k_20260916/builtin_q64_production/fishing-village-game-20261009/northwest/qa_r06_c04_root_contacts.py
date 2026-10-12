from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parent;W=B/'work-r06_c04/final-v2';Q=W/'qa';O=W/'root-qa-contacts';O.mkdir(exist_ok=True)
def pack(files,cols,name):
 ims=[Image.open(Q/f).convert('RGB') for f in files];w=max(i.width for i in ims);h=max(i.height for i in ims);out=Image.new('RGB',(w*cols,h*((len(ims)+cols-1)//cols)))
 for k,i in enumerate(ims):out.paste(i,((k%cols)*w,(k//cols)*h))
 p=O/(name+'.png');out.save(p);return {'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'members':files,'resampled':False}
rec=[]
for r in (1,3):
 for c in (1,3):rec.append(pack([f'core-{rr}-{cc}.100pct.png' for rr in (r,r+1) for cc in (c,c+1)],2,f'cores-{r}-{c}'))
rec.append(pack([f'junction-{r}-{c}.100pct.png' for r in range(1,4) for c in range(1,4)],3,'junctions'))
rec.append(pack([f'north-{k}.100pct.png' for k in range(1,5)],2,'north'))
for side in ('west','east'):rec.append(pack([f'{side}-interior-{k}.100pct.png' for k in range(1,5)],2,side))
rec.append(pack([f'south-interior-{k}.100pct.png' for k in range(1,5)],2,'south'))
(O/'manifest.json').write_text(json.dumps({'records':rec,'noResampling':True},indent=2))
print(json.dumps({'contacts':len(rec)}))
