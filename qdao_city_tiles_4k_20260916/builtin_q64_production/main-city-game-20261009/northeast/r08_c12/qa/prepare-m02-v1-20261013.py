from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c12');q=p/'qa'/'repair-resume-20261013';q.mkdir(exist_ok=True)
src=p/'qa/core-baseline/f7529838f3e52b886085/r08_c12-core-baseline.candidate.png'
box=[1250,0,2504,1254]
out=q/'m02-extra-band-north-target-v1.png'
assert not out.exists()
Image.open(src).crop(box).save(out)
(q/'m02-extra-band-north-target-v1.json').write_text(json.dumps({'source':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sourceBox':box,'output':str(out),'operation':'native integer crop; no resampling; target only'},indent=2),encoding='utf-8')
