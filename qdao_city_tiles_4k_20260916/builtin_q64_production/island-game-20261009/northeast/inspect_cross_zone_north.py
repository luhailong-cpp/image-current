from native_work import *
ext=ZONE.parent/'accelerated-northeast-coast/candidates';out=ZONE/'qa/cross-zone-20261011';out.mkdir(exist_ok=True);records=[]
for c in [13,14]:
 a=ext/f'r02_c{c}.4096-candidate.png';b=ZONE/'tiles'/f'r03_c{c}.png';d=read(a.with_suffix('.png.assembly.json'));print(json.dumps({'tile':a.stem,'assemblyKeys':list(d)}))
 ia=Image.open(a).convert('RGB');ib=Image.open(b).convert('RGB');assert ia.size==ib.size==(4096,4096)
 ah=sha(a);bh=sha(b)
 ev=[]
 for i in range(4):
  im=Image.new('RGB',(1024,512));im.paste(ia.crop((i*1024,3840,(i+1)*1024,4096)),(0,0));im.paste(ib.crop((i*1024,0,(i+1)*1024,256)),(0,256));p=out/f'r02_c{c}__r03_c{c}.segment-{i+1}.png';im.save(p);ev.append({'file':p.as_posix(),'sha256':sha(p),'segment':i+1,'status':'pending'})
 records.append({'pair':[f'r02_c{c}',f'r03_c{c}'],'upper':{'file':a.as_posix(),'sha256':ah,'assembly':a.with_suffix('.png.assembly.json').as_posix()},'lower':{'file':b.as_posix(),'sha256':bh},'evidence':ev,'status':'pending_visual_review','operation':'exact top-bottom core border strips;1:1; no resize/no feather; external source read only'})
write(out/'review.json',{'reviewedAtUtc':None,'records':records,'formalAccepted':False,'scope':'two whole4096shared boundaries only; no cross-zone source changes'})

