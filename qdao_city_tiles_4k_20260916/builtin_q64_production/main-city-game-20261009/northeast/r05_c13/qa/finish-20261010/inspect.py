from pathlib import Path
from PIL import Image
import json,hashlib
HERE=Path(__file__).resolve().parent
TILE=HERE.parents[1]
p=TILE/'candidates/r05_c13.candidate.png'
im=Image.open(p).convert('RGB')
out=HERE/'before'
out.mkdir(parents=True,exist_ok=True)
items=[]
for r in range(4):
 for c in range(1,4):
  box=(c*1024-160,r*1024,c*1024+160,(r+1)*1024)
  name=f'v-r{r+1}-c{c}.png'; im.crop(box).save(out/name);items.append({'file':str(out/name),'box':box})
for r in range(1,4):
 for c in range(4):
  box=(c*1024,r*1024-160,(c+1)*1024,r*1024+160)
  name=f'h-r{r}-c{c+1}.png'; im.crop(box).save(out/name);items.append({'file':str(out/name),'box':box})
for r in range(1,4):
 for c in range(1,4):
  box=(c*1024-400,r*1024-400,c*1024+400,r*1024+400)
  name=f'i-r{r}-c{c}.png'; im.crop(box).save(out/name);items.append({'file':str(out/name),'box':box})
for name,box in {'m02-context':(1421,2350,2675,3604),'m03-context':(2445,2300,3699,3554),'lower-context':(1700,2842,2954,4096),'roof-context':(2445,2842,3699,4096)}.items():
 im.crop(box).save(out/f'{name}.png');items.append({'file':str(out/f'{name}.png'),'box':box})
(HERE/'before-manifest.json').write_text(json.dumps({'candidate':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'noResampling':True,'crops':items},indent=2)+'\n',encoding='utf-8')
print(len(items))
