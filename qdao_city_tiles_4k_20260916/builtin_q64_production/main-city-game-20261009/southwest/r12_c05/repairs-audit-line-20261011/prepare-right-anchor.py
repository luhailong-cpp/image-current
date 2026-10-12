from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011";sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
guide=B/"guides/p01_02.layout-only.png";neighbor=D/"p01_03-quiet-material-v02/native.png";out=D/"p01_02.right-anchor.seed.png"
im=Image.open(guide).convert("RGB");ref=Image.open(neighbor).convert("RGB");im.paste(ref.crop((0,0,230,1254)),(1024,0));im.save(out)
record={"file":str(out),"sha256":sha(out),"seedNotNative":True,"guide":{"file":str(guide),"sha256":sha(guide)},"exactCopy":{"file":str(neighbor),"sha256":sha(neighbor),"sourceCrop":[0,0,230,1254],"targetBox":[1024,0,1254,1254],"sameWorldBox":[18317,44941,18547,46195],"resized":False},"meaning":"approved macro guide with correct newly repaired right neighbor native overlap"}
(out.with_suffix(".provenance.json")).write_text(json.dumps(record,indent=2),encoding="utf-8")
print(json.dumps(record))

