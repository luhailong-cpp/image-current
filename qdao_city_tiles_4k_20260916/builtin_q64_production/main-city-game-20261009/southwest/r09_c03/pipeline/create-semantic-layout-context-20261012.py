from pathlib import Path
import json, hashlib
from PIL import Image
T = Path(__file__).resolve().parents[1]
ref = Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png')
out = T / 'pipeline/guides/r09c03-smith-ground-semantic-layout-context.png'
assert not out.exists()
with Image.open(ref) as im:
    im.crop((145,600,275,750)).resize((780,900), Image.Resampling.NEAREST).save(out)
Path(str(out)+'.derivation.json').write_text(json.dumps({'source':str(ref),'sourceSha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'sourceCrop':[145,600,275,750],'operation':'mechanical nearest-neighbor enlarged geometry-only semantic context; never native final art','gameArt':False},indent=2)+'\n', encoding='utf-8')
print(out)
