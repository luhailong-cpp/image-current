from pathlib import Path
import json
from PIL import Image
T=Path(__file__).resolve().parents[1]
ref=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png')
out=T/'pipeline/guides/r09c02-smith-semantic-layout-context.png'
assert not out.exists()
with Image.open(ref) as im:
    im.crop((70,550,230,750)).resize((800,1000),Image.Resampling.NEAREST).save(out)
Path(str(out)+'.derivation.json').write_text(json.dumps({'source':str(ref),'sourceCrop':[70,550,230,750],'operation':'nearest-neighbor enlarged layout-only semantic context; never final art','gameArt':False},indent=2)+'\n')
print(out)
