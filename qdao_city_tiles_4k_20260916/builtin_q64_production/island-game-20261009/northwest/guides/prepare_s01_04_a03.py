from pathlib import Path
from PIL import Image
import json,hashlib
z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest'); stem='r03_c03_s01_04_a03'
left=z/'native/r03_c03_s01_03_a03.png'; prev=z/'native/r03_c03_s01_04_a02.png'; out=z/'guides'/f'{stem}.native-editguide.png'
assert not out.exists()
im=Image.open(prev).convert('RGB'); im.paste(Image.open(left).convert('RGB').crop((1024,0,1254,1254)),(0,0)); im.save(out)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources=[dict(path=prev.as_posix(),sha256=sha(prev),sourceCrop=[0,0,1254,1254],destination=[0,0],role='prior target native retaining unchanged material outside seam'),dict(path=left.as_posix(),sha256=sha(left),sourceCrop=[1024,0,1254,1254],destination=[0,0],role='new corrected left-neighbor overlap replacing first 230 columns')]
d=dict(file=out.as_posix(),sha256=sha(out),operation='mechanical native copy and exact 230px overlap paste; edit guide only',nativeSize=[1254,1254],sources=sources,finalArt=False)
out.with_suffix('.png.derivation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=z/'guides'/f'{stem}.input.json'; r=json.loads(p.read_text(encoding='utf-8-sig'))
r['layoutOnlyGuide']=r['inputs'][0]
r['inputs'][0]=dict(path=out.as_posix(),sha256=sha(out),role='native edit target guide: corrected left native 230px plus unchanged prior target',nativeSize=[1254,1254],derivedFrom=sources)
r['inputs'].append(dict(path=prev.as_posix(),sha256=sha(prev),role='prior native edit target; preserve door and roof away from seam',nativeSize=[1254,1254]))
p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
