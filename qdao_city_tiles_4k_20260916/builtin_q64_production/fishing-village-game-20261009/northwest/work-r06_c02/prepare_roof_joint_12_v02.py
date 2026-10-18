from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');W=B/'work-r06_c02'
src=W/'base-v2/extended.png';p=W/'guides/r06_c02_roof_joint_12_v02.authoritative.png'
assert not p.exists()
Image.open(src).crop((1536,0,2790,1254)).save(p)
Path(str(p)+'.derivation.json').write_text(json.dumps({'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'crop':[1536,0,2790,1254],'resample':False,'globalNativeBox':[5517,20365,6771,21619]}),encoding='utf-8')
