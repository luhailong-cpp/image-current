from pathlib import Path
from PIL import Image
import json,hashlib
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast')
p='r06_c14_p34'
g=z/'guides'/f'{p}.native-edge-layout.png'
im=Image.open(g).convert('RGB')
pure=Image.open(z/'guides'/f'{p}.layout-only.png').convert('RGB')
box=(230,116,720,230)
im.paste(pure.crop(box),box[:2])
out=z/'guides'/f'{p}.native-edge-layout-v1.png'
assert not out.exists()
im.save(out)
rec={'purpose':'guide only, not final pixels','operation':'replace top non-core halo mistaken tiny cap with exact layout-only pixels; true y115 seam kept','base':str(g),'layout':str(z/'guides'/f'{p}.layout-only.png'),'replaceBox':list(box),'coreBoundaryPreserved':115}
Path(str(out)+'.derived.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
plan=json.loads((z/'records'/f'{p}.plan.json').read_text(encoding='utf-8'))
plan['references'][3].update({'path':str(out).replace(chr(92),'/'),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
plan['nativeHaloAdjustment']=rec
(z/'records'/f'{p}-v1.plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(out))

