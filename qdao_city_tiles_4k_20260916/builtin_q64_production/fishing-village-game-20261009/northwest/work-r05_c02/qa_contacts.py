from pathlib import Path
from PIL import Image
import json,hashlib
W=Path(__file__).resolve().parent;Q=W/'base-v1/qa';O=W/'base-v1/qa-contacts';O.mkdir(exist_ok=True)
def contact(names,cols,name):
 ims=[Image.open(Q/(n+'.png')).convert('RGB') for n in names]
 w=max(i.width for i in ims);h=max(i.height for i in ims);out=Image.new('RGB',(w*cols,h*((len(ims)+cols-1)//cols)))
 for k,i in enumerate(ims):out.paste(i,((k%cols)*w,(k//cols)*h))
 p=O/(name+'.png');out.save(p)
 return {'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'members':[{'file':str(Q/(n+'.png')),'nativeDimensions':list(i.size),'contactTopLeft':[(k%cols)*w,(k//cols)*h]} for k,(n,i) in enumerate(zip(names,ims))],'resampled':False}
records=[]
for r in (1,3):
 for c in (1,3):records.append(contact([f'core-{rr}-{cc}' for rr in (r,r+1) for cc in (c,c+1)],2,f'cores-r{r}-c{c}'))
for j in range(1,4):
 records.append(contact([f'v{j}-{k}' for k in range(1,5)],2,f'v{j}'))
 records.append(contact([f'h{j}-{k}' for k in range(1,5)],2,f'h{j}'))
records.append(contact([f'junction-{r}-{c}' for r in range(1,4) for c in range(1,4)],3,'junctions'))
records.append(contact([f'north-{k}' for k in range(1,5)],2,'north'))
records.append(contact([f'east-{k}' for k in range(1,5)],2,'east'))
(O/'manifest.json').write_text(json.dumps({'definition':'Exact native cuts placed without resampling; row-major ordering','records':records},indent=2))
print(json.dumps({'contacts':len(records)}))
