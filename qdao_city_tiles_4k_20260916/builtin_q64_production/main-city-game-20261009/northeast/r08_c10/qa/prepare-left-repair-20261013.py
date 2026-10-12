from pathlib import Path
from PIL import Image
import json,hashlib
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c10")
d=t/"qa/local-repair-20261013";d.mkdir(exist_ok=True)
src=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c10/qa/core-baseline/aa79b145eff57b69aabf/r08_c10-core-baseline.candidate.png")
target=d/"cloud-upper-target-v1.png"
assert not target.exists()
im=Image.open(src).convert("RGB");im.crop((1421,397,2675,1651)).save(target)
meta={"source":str(src),"sourceSha256":hashlib.sha256(src.read_bytes()).hexdigest(),"cropBox":[1421,397,2675,1651],"pasteOutputBox":[1480,850,2560,1150],"kind":"integer source crop; native local repair target"}
(d/"cloud-upper-target-v1.json").write_text(json.dumps(meta,indent=2)+"\n")
print(str(target))

