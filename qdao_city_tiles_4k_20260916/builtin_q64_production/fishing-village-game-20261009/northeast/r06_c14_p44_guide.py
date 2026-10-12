from pathlib import Path
from PIL import Image
import json,hashlib
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast');p='r06_c14_p44'
plan=json.loads((z/'records'/f'{p}.plan.json').read_text(encoding='utf-8'))
im=Image.open(z/'guides'/f'{p}.layout-only.png').convert('RGB')
for e in plan['nativeEdgeSources']:
 if 'top' in e['role']:e['path']=str(z/'native/r06_c14_p34-v3.png').replace(chr(92),'/')
 path=Path(e['path']);e['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();im.paste(Image.open(path).convert('RGB').crop(e['cropBox']),e['pasteAt'])
g=z/'guides'/f'{p}.native-edge-layout-v1.png';assert not g.exists();im.save(g)
plan['references'][3].update({'path':str(g).replace(chr(92),'/'),'sha256':hashlib.sha256(g.read_bytes()).hexdigest()})
(z/'records'/f'{p}-v1.plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
Path(str(g)+'.derived.json').write_text(json.dumps({'purpose':'guide only not final pixels','sources':plan['nativeEdgeSources'],'operation':'exact native left and top230 pasted1:1 onto layout-only'},indent=2),encoding='utf-8')
(z/'records/r06_c14.working-selection.json').write_text(json.dumps({'r06_c14_p34':'r06_c14_p34-v3.png'},indent=2),encoding='utf-8')
print(str(g))

