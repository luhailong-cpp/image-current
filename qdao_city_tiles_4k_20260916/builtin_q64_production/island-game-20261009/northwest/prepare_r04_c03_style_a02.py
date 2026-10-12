from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stem='r04_c03_s01_01_a02';old=json.loads((Z/'guides/r04_c03_s01_01_a01.input.json').read_text(encoding='utf-8'))
srcs=[Z/'native/r03_c03_s04_01_a01.png',Z/'native/r03_c03_repair_second_cylinder_a01.png']
contact=Z/'guides'/f'{stem}.native-style-contact.png';assert not contact.exists()
im=Image.new('RGB',(2508,1254))
for i,p in enumerate(srcs):im.paste(Image.open(p).convert('RGB'),(i*1254,0))
im.save(contact)
d=dict(operation='unresized horizontal native reference contact, not final artwork',output=dict(path=contact.as_posix(),sha256=sha(contact),nativeSize=[2508,1254]),sources=[dict(path=p.as_posix(),sha256=sha(p),nativeSize=[1254,1254],placement=[i*1254,0],role=('top coordinate neighbor' if i==0 else 'same-island accepted rounded painted firework cylinder material, NOT coordinate view')) for i,p in enumerate(srcs)],resizing=False,colorCorrection=False)
dp=contact.with_suffix('.derivation.json');dp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
target=Z/'native/r04_c03_s01_01_a01.png';style=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
inputs=[dict(path=target.as_posix(),sha256=sha(target),nativeSize=[1254,1254],role='edit target: preserve composition and native scale, replace overly photographic textures with approved rounded Q painting')]+style+[dict(path=contact.as_posix(),sha256=sha(contact),nativeSize=[2508,1254],role='unscaled native top neighbor LEFT, approved finished same-island painted firework material RIGHT; latter only style',derivationRecord=dict(path=dp.as_posix(),sha256=sha(dp)))]
rec=dict(old);rec.update(versionStem=stem,attempt='a02',inputs=inputs,imageGenReferencedImagePaths=[e['path'] for e in inputs],editTarget=dict(path=target.as_posix(),sha256=sha(target)),operation='builtin native style correction of a01, no layout movement',inputCount=5)
for suffix,v in [('input',rec),('references',dict(inputs=inputs))]:
 p=Z/'guides'/f'{stem}.{suffix}.json';assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([e['path'] for e in inputs]))
