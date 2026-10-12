from pathlib import Path
from PIL import Image
import json,hashlib
d=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach/r05_c11/repairs/ground-halo-v6');d.mkdir(parents=True,exist_ok=True)
src=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach/r05_c11/repairs/ground-halo-v3/native-result.png')
im=Image.open(src).convert('RGBA');im.paste((0,0,0,0),(582,574,721,727));im.save(d/'target-inpaint-native.png')
(d/'inpaint-target-derivation.json').write_text(json.dumps({'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'dimensions':[1254,1254],'operation':'Native alpha knockout only, no resampling or new painted pixels','transparentHoleNativeBox':[582,574,721,727]},indent=2)+'\n',encoding='utf-8')

