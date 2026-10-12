from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
R=T/'qa/local-repair-resume2-20261013'
base=T/'qa/core-baseline/31b09711d96a1bf993b7/r06_c15-core-baseline.candidate.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(base).convert('RGB')
items=[
('panel',[140,2350],[50,470,1010,1220]),
('ledge',[540,2842],[100,650,1180,1120]),
('roof',[2580,2480],[370,440,1254,760]),
('trunk',[2240,1340],[390,180,660,780]),
('wallrail',[840,1180],[185,150,1040,1020]),
('fascia',[1720,400],[0,410,710,760]),
('upperroof',[680,400],[180,480,1254,770]),
]
layers=[]
for name,origin,crop in items:
 src=T/'native/repairs'/f'{name}-local-resume2-v20261013.png'
 p=Image.open(src).convert('RGB')
 pos=[origin[0]+crop[0],origin[1]+crop[1]]
 im.paste(p.crop(crop),tuple(pos))
 layers.append({'id':name,'file':str(src),'sha256':sha(src),'targetOrigin':origin,'sourceCrop':crop,'destination':pos,'nativeSize':list(p.size)})
dest=T/'candidates/r06_c15.local-repairs-resume2-v1.png'
dest.parent.mkdir(exist_ok=True)
assert not dest.exists()
im.save(dest)
for name,origin,crop in items:
 out=R/(name+'-composited-v1.png')
 assert not out.exists()
 im.crop([origin[0],origin[1],origin[0]+1254,origin[1]+1254]).save(out)
report={'tile':'r06_c15','base':str(base),'baseSha256':sha(base),'candidate':str(dest),'candidateSha256':sha(dest),'layers':layers,'operation':'integer crop/paste only; no resampling, feathering or pixel painting','status':'repair-boundaries-awaiting-visual-review','internalPassed4kCount':0}
(R/'composition-v1.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate':str(dest),'sha256':sha(dest),'layers':len(layers)}))
