from PIL import Image
from pathlib import Path
import json,hashlib
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast")
src=z/"native/r05_c14_p14-v1.png"; left=z/"native/r05_c14_p13-v4.png"; bottom=z/"native/r05_c14_p24-v1.png"
im=Image.open(src).convert("RGB")
im.paste(Image.open(bottom).crop((0,0,1254,230)),(0,1024))
im.paste(Image.open(left).crop((1024,0,1139,1254)),(0,0))
gp=z/"guides/r05_c14_p14-v2.native-left-core-repair-guide.png"; im.save(gp)
def rec(p,role):return {"path":str(p).replace("\\","/"),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"role":role}
(gp.with_name(gp.name+".derived.json")).write_text(json.dumps({"purpose":"native geometry guide only; never final art","operation":"1:1 integer opaque crop/paste; no resize/paint/feather","sources":[rec(src,"edit target base"),rec(left,"native last115 core columns source"),rec(bottom,"native bottom strip")],"leftCrop":[1024,0,1139,1254],"leftPaste":[0,0],"bottomCrop":[0,0,1254,230],"bottomPaste":[0,1024],"trueCoreCut":115,"rationale":"Source left east halo fitted bow inaccurately; source actual core pixels used through world cut only."},indent=2),encoding="utf-8")
print(gp)

