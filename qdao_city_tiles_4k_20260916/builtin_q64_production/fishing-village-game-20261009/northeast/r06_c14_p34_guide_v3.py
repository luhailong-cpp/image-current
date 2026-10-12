from pathlib import Path
from PIL import Image
import json,hashlib
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast');p='r06_c14_p34'
v1=z/'native'/f'{p}-v1.png';v2=z/'native'/f'{p}-v2.png'
im=Image.open(v2).convert('RGB');im.paste(Image.open(v1).convert('RGB').crop((0,0,1254,420)),(0,0))
g=z/'guides'/f'{p}.native-geometry-v3.png';assert not g.exists();im.save(g)
rec={'purpose':'AI guide only, not final image','operation':'native1:1 upper420 of v1 with correct intact cap below top seam, lower834 of v2 with correct long trunk; AI must redraw full patch','sources':[{'path':str(x),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in [v1,v2]],'compositeSplitY':420}
Path(str(g)+'.derived.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
plan=json.loads((z/'records'/f'{p}-v2.plan.json').read_text(encoding='utf-8'));plan['references'][3].update({'path':str(g).replace(chr(92),'/'),'sha256':hashlib.sha256(g.read_bytes()).hexdigest(),'role':'native geometry correction guide only'});plan['guideCorrection']=rec
(z/'records'/f'{p}-v3.plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(g))

