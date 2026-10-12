from pathlib import Path
from PIL import Image
import json, hashlib

ZONE = Path(__file__).resolve().parent.parent
STEM = 'r03_c03_s02_02_a03'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(path, role):
    return dict(path=Path(path).as_posix(), sha256=sha(path), nativeSize=list(Image.open(path).size), role=role)
old = json.loads((ZONE/'guides/r03_c03_s02_02_a02.input.json').read_text(encoding='utf-8-sig'))
target = ZONE/'native/r03_c03_s02_02_a02.png'
right = ZONE/'native/r03_c03_s02_03_a01.png'
left = ZONE/'native/r03_c03_s02_01_a04.png'
top = ZONE/'native/r03_c03_s01_02_a03.png'
out = ZONE/'guides'/f'{STEM}.native-editguide.png'
assert not out.exists()
base = Image.open(target).convert('RGB')
imright = Image.open(right).convert('RGB')
assert base.size == imright.size == (1254,1254)
base.paste(imright.crop((0,230,230,1254)),(1024,230))
base.save(out)
derivation = dict(file=out.as_posix(), sha256=sha(out), dimensions=[1254,1254], operation='exact native pixels; base plus right-neighbor overlap below preserved top halo; no drawing, scaling or color correction', finalArt=False,
    sources=[ref(target,'prior native target; full canvas'),dict(**ref(right,'right adjacent native; exact crop'),sourceCrop=[0,230,230,1254],destination=[1024,230])], repairContextBox=[950,480,1254,740])
out.with_suffix('.png.derivation.json').write_text(json.dumps(derivation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data = {k: old[k] for k in ('globalBox','coreBox','referenceBox')}
data.update(stem=STEM, editIntent='repair only lantern lower exterior curve into right native; preserve window, column, beams, top and left. Bottom joint pending new row-three native.', inputs=[dict(**ref(out,'PRIMARY 1254x1254 native edit guide; preserve this crop and framing; only repair lantern lower contour at old/right-strip transition'),derivedFrom=derivation['sources'])]+old['inputs'][1:4]+[
    ref(target,'panel 1: original target a02, unchanged context outside local lantern edge'),
    ref(right,'panel 2: right neighbor 02_03a01; its left 230 native pixels map to target x1024..1253; preserve lower lantern trajectory toward its gold collar'),
    ref(left,'panel 3: left neighbor 02_01a04; last 230 native columns overlap target first 230'),
    ref(top,'panel 4: top neighbor 01_02a03; last 230 native rows overlap target first 230')])
dest=ZONE/'guides'/f'{STEM}.input.json'
dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(dest.as_posix())
