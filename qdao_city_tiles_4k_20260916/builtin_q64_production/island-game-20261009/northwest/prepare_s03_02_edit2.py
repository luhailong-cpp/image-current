from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stem='r03_c03_s03_02_a04'
p=Z/'native/r03_c03_s03_02_a03.png'; bottom=Z/'native/r03_c03_s04_02_a01.png'
im=Image.open(p).convert('RGB'); im.paste(Image.open(bottom).convert('RGB').crop((0,0,1254,230)),(0,1024))
g=Z/'guides'/f'{stem}.edit-target.png'; assert not g.exists();im.save(g)
refs=json.loads((Z/'references.json').read_text(encoding='utf-8-sig'))
inputs=[dict(path=g.as_posix(),role='edit target from prior native, exact lower230 restored; repair upper cylinder to match lower edge and cloud ornament',sha256=sha(g),derivedFrom=[dict(path=p.as_posix(),sha256=sha(p),operation='full native unresized'),dict(path=bottom.as_posix(),sha256=sha(bottom),sourceCrop=[0,0,1254,230],destination=[0,1024],operation='exact native edge paste')])]+refs+[dict(path=bottom.as_posix(),sha256=sha(bottom),role='authoritative lower native original')]
for suffix,rec in [('references',dict(inputs=inputs)),('input',dict(stem=stem,globalBox=[9101,10125,10355,11379],coreBox=[9216,10240,10240,11264],inputs=inputs,layoutPixelsForbiddenInFinal=True,operation='exact native lower edge paste in edit input only'))]:
 (Z/'guides'/f'{stem}.{suffix}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(g.as_posix())
