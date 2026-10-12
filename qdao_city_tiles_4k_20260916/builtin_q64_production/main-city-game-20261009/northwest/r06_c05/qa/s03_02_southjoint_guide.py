import json,hashlib
from pathlib import Path
from PIL import Image
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c05")
base=b/"native/s03_02.png"; guide=b/"layout-only/s03_02.continuation-guide.png"
im=Image.open(base).convert("RGB")
anchor=Image.open(guide).convert("RGB")
im.paste(anchor.crop((0,1024,1254,1254)),(0,1024))
p=b/"layout-only/s03_02_southjoint02.native-anchor-guide.png";im.save(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
(p.with_suffix(p.suffix+".derivation.json")).write_text(json.dumps({"role":"reference guide only, not deliverable art","base":{"file":str(base),"sha256":sha(base)},"nativeSouthAnchor":{"file":str(guide),"sha256":sha(guide),"sourceCrop":[0,1024,1254,1254],"targetPaste":[0,1024]},"transforms":"exact native pixel crop/paste only, no scaling, coloring or blur","output":{"file":str(p),"sha256":sha(p),"size":[1254,1254]}},indent=2))
print(p)

