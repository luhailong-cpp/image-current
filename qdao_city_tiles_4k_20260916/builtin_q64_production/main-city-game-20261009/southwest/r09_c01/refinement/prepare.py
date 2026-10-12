from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
T=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r09_c01");d=T/"refinement";d.mkdir(exist_ok=True)
base=json.loads((T/"pipeline/prompts/p01_01.v01.request.json").read_text(encoding="utf8"))
prompt=(d/"p01_01.v02.prompt.txt").read_text(encoding="utf8")
refs=json.loads((d/"p01_01.v02.refs.json").read_text(encoding="utf8"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base.update(prompt=prompt,promptFile=str(d/"p01_01.v02.prompt.txt"),promptSha256=sha(d/"p01_01.v02.prompt.txt"),referenced_image_paths=refs,preparedAtUtc=datetime.now(timezone.utc).isoformat(),references=[{"file":p,"sha256":sha(p),"role":r,"pixels":list(Image.open(p).size)} for p,r in zip(refs,["exact coarse layout edit target","approved full layout","approved material","approved primary chibi style","native overview crop semantic context only"])])
(d/"p01_01.v02.request.json").write_text(json.dumps(base,ensure_ascii=False,indent=2),encoding="utf8")
print(d/"p01_01.v02.request.json")

