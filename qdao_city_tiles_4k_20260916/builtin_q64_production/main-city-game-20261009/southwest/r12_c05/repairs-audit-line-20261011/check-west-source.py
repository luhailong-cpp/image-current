from pathlib import Path
from PIL import Image
import json
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011/qa-macro-round-01"
src=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png")
im=Image.open(src);box=[309,898,353,929];im.crop(box).resize((880,620),Image.Resampling.NEAREST).save(D/"west-frame-source-nearest20x.png")
(D/"west-frame-source-nearest20x.json").write_text(json.dumps({"source":str(src),"sourceCrop":box,"resizedForReviewOnly":True,"scale":20}))

