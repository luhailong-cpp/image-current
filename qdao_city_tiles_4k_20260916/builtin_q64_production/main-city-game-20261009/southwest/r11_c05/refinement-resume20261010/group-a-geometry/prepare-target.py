from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r11_c05/refinement-resume20261010/group-a-geometry");D.mkdir(parents=True,exist_ok=True)
for sub in ['prompts','native','receipts','input','qa','output']: (D/sub).mkdir(exist_ok=True)
base=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r11_c05/refinement-resume20261010/full-tile-review")/'output/r11_c05.repaired.candidate.context.png'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='09e3107e74361a9c2cc3a1b2911554ad3dbb470843a833d6e648e47b86804686'
im=Image.open(base);box=[512,2100,1766,3354];out=D/'input/group-a-target.native1254.png';im.crop(box).save(out)
record={'sourceContext':str(base),'sourceContextSha256':hashlib.sha256(base.read_bytes()).hexdigest(),'cropContextBox':box,'cropCoreBox':[397,1985,1651,3239],'target':str(out),'targetSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'resampled':False,'pixels':[1254,1254]}
(D/'input/crop-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record,indent=2))

