from pathlib import Path
from PIL import Image
import json
B=Path(__file__).resolve().parents[1]
ref=B.parent.parent/'parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png'
p=B/'r09_c06/pipeline/qa/approved-post-context-qa.png';p.parent.mkdir(exist_ok=True,parents=True)
i=Image.open(ref);i.crop((380,600,450,670)).resize((840,840),Image.Resampling.NEAREST).save(p)
print(p)

