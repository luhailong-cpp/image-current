from pathlib import Path
from PIL import Image
import json,hashlib
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r07_c06');out=r/'qa/s02_02_orphanfix02-proposal01';out.mkdir(exist_ok=False)
a=Image.open(r/'qa/s02_02_orphanfix01-proposal01/proposal-native-1254.png').convert('RGB')
d=Image.open(r/'native/s02_02_orphanfix02.png').convert('RGB')
box=(140,1000,253,1114);a.paste(d.crop(box),box[:2])
a.save(out/'proposal-native-1254.png');a.crop((115,975,278,1139)).save(out/'joint-and-all-four-perimeters.png')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(out/'proposal-proof.json').write_text(json.dumps(dict(sourceROI=list(box),nativeWorldBox=[21389,25485,22643,26739],sourceOriginal=str(r/'qa/s02_02_orphanfix01-proposal01/proposal-native-1254.png'),additionalNative=dict(file=str(r/'native/s02_02_orphanfix02.png'),sha256=sha(r/'native/s02_02_orphanfix02.png')),pixelOperation='same-world binary native ROI overwrite only',status='proposal-pending-local-perimeter-review',formalAccepted=False),indent=2),encoding='utf-8')
