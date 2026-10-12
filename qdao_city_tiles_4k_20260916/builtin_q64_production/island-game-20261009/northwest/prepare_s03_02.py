from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parent
stem='r03_c03_s03_02_a01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
box=[9101,10125,10355,11379]; rb=[v*1254/57344 for v in box]
guide=Image.open(refs[0]['path']).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,rb,Image.Resampling.BICUBIC)
names=[('left','r03_c03_s03_01_a01',[1024,0,1254,1254],[0,0]),('top','r03_c03_s02_02_a02',[0,1024,1254,1254],[0,0]),('bottom','r03_c03_s04_02_a01',[0,0,1254,230],[0,1024])]
contact=Image.new('RGB',(1254*3,1254)); neighbors=[]
for i,(edge,name,crop,dest) in enumerate(names):
 p=Z/'native'/f'{name}.png'; im=Image.open(p).convert('RGB');assert im.size==(1254,1254)
 guide.paste(im.crop(crop),tuple(dest));contact.paste(im,(i*1254,0))
 neighbors.append(dict(path=p.as_posix(),sha256=sha(p),nativeSize=[1254,1254],role=edge+' adjacent native',sourceCrop=crop,guideDestination=dest,contactBox=[i*1254,0,(i+1)*1254,1254]))
gp=Z/'guides'/f'{stem}.layout-with-native.png'; cp=Z/'guides'/f'{stem}.native-reference-contact.png'
assert not gp.exists() and not cp.exists()
guide.save(gp);contact.save(cp)
inputs=[dict(path=gp.as_posix(),sha256=sha(gp),nativeSize=[1254,1254],role='layout-only plus left/top/bottom exact 230px native strips')]+refs+[dict(path=cp.as_posix(),sha256=sha(cp),nativeSize=[3762,1254],role='unresized contact left-to-right: left neighbor, top neighbor, bottom neighbor',derivedFrom=neighbors)]
write(Z/'guides'/f'{stem}.input.json',dict(stem=stem,globalBox=box,coreBox=[9216,10240,10240,11264],referenceBox=rb,inputs=inputs,neighbor=neighbors,layoutPixelsForbiddenInFinal=True,operation='layout guide with unresampled adjacent native strips'))
write(Z/'guides'/f'{stem}.native-reference-contact.derivation.json',dict(output=cp.as_posix(),sha256=sha(cp),operation='unresized horizontal native contact for reference only',sources=neighbors,allowedAsFinalArt=False))
print(gp.as_posix())

