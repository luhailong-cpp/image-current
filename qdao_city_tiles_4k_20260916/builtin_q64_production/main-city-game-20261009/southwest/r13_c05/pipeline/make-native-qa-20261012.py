import sys,json,hashlib
from pathlib import Path
from PIL import Image
a=Path(sys.argv[1]); d=json.loads(a.read_text(encoding='utf-8-sig'))
p=Path(d['output']['file']); im=Image.open(p).convert('RGB'); w,h=im.size; nr=h//1024; nc=w//1024
out=a.parent/'native-qa'; out.mkdir(exist_ok=True); records=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,box,kind):
    target=out/(name+'.png'); assert not target.exists()
    crop=im.crop(box); crop.save(target)
    records.append({'name':name,'kind':kind,'file':str(target),'sha256':sha(target),'pixels':list(crop.size),'cropBoxInCore':box,'resampled':False,'visualQa':'pending'})
for r in range(nr):
    for c in range(1,nc): save(f'V{c}-{r+1}',[1024*c-119,1024*r,1024*c+119,1024*(r+1)],'vertical')
for r in range(1,nr):
    for c in range(nc): save(f'H{r}-{c+1}',[1024*c,1024*r-119,1024*(c+1),1024*r+119],'horizontal')
for r in range(1,nr):
    for c in range(1,nc): save(f'X{r}-{c}',[1024*c-256,1024*r-256,1024*c+256,1024*r+256],'intersection')
manifest=out/'manifest.json'; manifest.write_text(json.dumps({'assembly':str(a),'assemblySha256':sha(a),'source':str(p),'sourceSha256':sha(p),'records':records,'nativeCropOnly':True,'formalAccepted':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qa':str(manifest),'newNativeCrops':[q['file'] for q in records]},indent=2))
