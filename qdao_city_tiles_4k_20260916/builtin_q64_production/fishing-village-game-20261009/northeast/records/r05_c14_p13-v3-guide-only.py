from PIL import Image
from pathlib import Path
import json,hashlib
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast")
src=z/"native/r05_c14_p13-v2.png"
left=z/"native/r05_c14_p12-v1.png"
bottom=z/"native/r05_c14_p23-v1.png"
im=Image.open(src).convert("RGB")
im.paste(Image.open(bottom).crop((0,0,1254,230)),(0,1024))
im.paste(Image.open(left).crop((1024,0,1254,1254)),(0,0))
gp=z/"guides/r05_c14_p13-v3.native-repair-guide.png"
im.save(gp)
def rec(p,role):return {"path":str(p).replace("\\","/"),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"role":role}
(gp.with_name(gp.name+".derived.json")).write_text(json.dumps({"purpose":"native geometry repair guide only; never final pixels","operation":"1:1 opaque integer crop/paste of real left/bottom neighbor onto v2 target; no resizing/paint/feather","sources":[rec(src,"edit target base"),rec(left,"exact left strip source"),rec(bottom,"exact bottom strip source")],"leftCrop":[1024,0,1254,1254],"leftPaste":[0,0],"bottomCrop":[0,0,1254,230],"bottomPaste":[0,1024],"core":[115,115,1139,1139]},indent=2),encoding="utf-8")
print(gp)

