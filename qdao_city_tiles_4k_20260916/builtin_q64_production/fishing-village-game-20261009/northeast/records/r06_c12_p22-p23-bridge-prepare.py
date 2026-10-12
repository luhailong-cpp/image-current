"""Mechanical preparation for one native p22/p23 bridge repair. No painting."""
from pathlib import Path
from PIL import Image
import hashlib,json
Z=Path(__file__).resolve().parent.parent
P='r06_c12_p22-p23-bridge'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=Z/'native/r06_c12_p22-v2.png';b=Z/'native/r06_c12_p23-v1.png'
images=[]
for p in (a,b):
 r=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
 if r['sha256']!=sha(p):raise ValueError('Input hash mismatch')
 im=Image.open(p);im.load()
 if im.size!=(1254,1254):raise ValueError('Wrong native dimensions')
 images.append(im.convert('RGB'))
out=Image.new('RGB',(1254,1254))
out.paste(images[0].crop((512,0,1139,1254)),(0,0))
out.paste(images[1].crop((115,0,742,1254)),(627,0))
target=Z/'guides'/f'{P}-edit-target.png'
if target.exists():raise ValueError('Refusing to overwrite target')
out.save(target)
sources=[{'path':str(p),'sha256':sha(p),'sourceBox':s,'targetBox':t,'generationRecord':str(p)+'.generation.json'}
 for p,s,t in [(a,[512,0,1139,1254],[0,0,627,1254]),(b,[115,0,742,1254],[627,0,1254,1254])]]
write(str(target)+'.derived.json',{'file':str(target),'sha256':sha(target),'pixels':[1254,1254],
 'nativeGlobalBox':[46477,21389,47731,22643],'joinLocalX':627,'derivedFrom':sources,
 'operation':'1:1 crop and opaque paste, no resize, drawing, blending or feathering',
 'purpose':'Native splice target for one image_gen repair; not accepted art'})
write(Z/'records'/f'{P}-config-snapshot.json',json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')))
print(str(target))

