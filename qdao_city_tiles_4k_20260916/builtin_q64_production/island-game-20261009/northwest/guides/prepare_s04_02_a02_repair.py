from pathlib import Path
from PIL import Image
import json, hashlib
Z=Path(__file__).resolve().parent.parent
S='r03_c03_s04_02_a02'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role):return dict(path=p.as_posix(),sha256=sha(p),nativeSize=list(Image.open(p).size),role=role)
old=json.loads((Z/'guides/r03_c03_s04_02_a01.input.json').read_text(encoding='utf-8'))
target=Z/'native/r03_c03_s04_02_a01.png';top=Z/'native/r03_c03_s03_02_a03.png'
left=Z/'native/r03_c03_s04_01_a01.png';right=Z/'native/r03_c03_s04_03_a01.png'
out=Z/'guides'/f'{S}.native-editguide.png';assert not out.exists()
im=Image.open(target).convert('RGB');up=Image.open(top).convert('RGB')
assert im.size==up.size==(1254,1254)
im.paste(up.crop((320,1024,850,1254)),(320,0));im.save(out)
sources=[ref(target,'original lower native full canvas'),dict(**ref(top,'upper native primary cylinder exact original-pixel overlap'),sourceCrop=[320,1024,850,1254],destination=[320,0])]
der=dict(file=out.as_posix(),sha256=sha(out),dimensions=[1254,1254],operation='mechanical exact same-coordinate native crop/paste only',resized=False,finalArt=False,sources=sources)
out.with_suffix('.png.derivation.json').write_text(json.dumps(der,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rec={k:old[k] for k in ('globalBox','coreBox','referenceBox')}
rec.update(stem=S,editIntent='Join primary cylinder upper body to fixed existing lower base, repairing only x310..860/y0..340; secondary right cylinder unchanged, pending adjoining ownership.',inputs=[dict(**ref(out,'PRIMARY native lower-patch edit guide, 1254 square; upper primary-cylinder strip is fixed real upper source'),derivedFrom=sources)]+old['inputs'][1:4]+[
ref(target,'panel1 original lower patch; preserve gold base, ground contact and paving'),ref(top,'panel2 real upper source; last230 rows align target first230, exact primary cylinder x350..808'),ref(left,'panel3 lower-left neighbor; last230 columns align target first230'),ref(right,'panel4 lower-right neighbor; first230 columns align target last230; preserve this joint')])
(Z/'guides'/f'{S}.input.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
