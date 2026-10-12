from pathlib import Path
from PIL import Image
import json,hashlib,sys,shutil
T=Path(__file__).resolve().parent
Q=T/'qa'/'final-review';Q.mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
C=T/'candidates'/f'{T.name}.candidate.png'
if sys.argv[1]=='initialize':
 baseline=Path(sys.argv[2])
 if C.exists(): raise RuntimeError('Existing final candidate preserved')
 shutil.copy2(baseline,C)
 (Path(str(C)+'.generation.json')).write_text(json.dumps({'tile':T.name,'file':str(C),'sha256':sha(C),'nativeSize':[4096,4096],'operation':'Integer native core crop/paste','coreBaseline':{'file':str(baseline),'sha256':sha(baseline)},'repairs':[],'sourceResampling':False,'finalArtUpscaled':False,'actualModel':None,'actualQuality':None},indent=2),encoding='utf-8')
im=Image.open(C).convert('RGB')
if im.size!=(4096,4096): raise RuntimeError('Expected 4096 native candidate')
for r in range(1,5):
 montage=Image.new('RGB',(1152,1024))
 for c in range(1,4):
  crop=im.crop((c*1024-192,(r-1)*1024,c*1024+192,r*1024))
  crop.save(Q/f'v-{r}-{c}-100pct.png');montage.paste(crop,((c-1)*384,0))
 montage.save(Q/f'v-row{r}-100pct.png')
for c in range(1,5):
 montage=Image.new('RGB',(1024,1152))
 for r in range(1,4):
  crop=im.crop(((c-1)*1024,r*1024-192,c*1024,r*1024+192))
  crop.save(Q/f'h-{r}-{c}-100pct.png');montage.paste(crop,(0,(r-1)*384))
 montage.save(Q/f'h-col{c}-100pct.png')
for r in range(1,4):
 for c in range(1,4):
  im.crop((c*1024-450,r*1024-450,c*1024+450,r*1024+450)).save(Q/f'intersection-{r}-{c}-100pct.png')
external=[]
for axis,tid in [('north','r05_c14'),('west','r06_c13')]:
 p=T.parent/tid/'candidates'/f'{tid}.candidate.png'
 if not p.exists(): continue
 adj=Image.open(p).convert('RGB')
 for i in range(4):
  if axis=='north':
   canvas=Image.new('RGB',(1024,384));canvas.paste(adj.crop((i*1024,3904,(i+1)*1024,4096)),(0,0));canvas.paste(im.crop((i*1024,0,(i+1)*1024,192)),(0,192))
  else:
   canvas=Image.new('RGB',(384,1024));canvas.paste(adj.crop((3904,i*1024,4096,(i+1)*1024)),(0,0));canvas.paste(im.crop((0,i*1024,192,(i+1)*1024)),(192,0))
  canvas.save(Q/f'{axis}-{i+1}-100pct.png')
 external.append({'tile':tid,'candidate':str(p),'sha256':sha(p),'axis':axis,'segments':4})
(Q/'qa-crops.json').write_text(json.dumps({'candidate':str(C),'sha256':sha(C),'internalPairs':24,'intersections':9,'external':external,'resampling':False,'visualStatus':'awaiting review'},indent=2),encoding='utf-8')
print(json.dumps({'candidate':str(C),'sha256':sha(C),'qa':str(Q),'external':external}))

