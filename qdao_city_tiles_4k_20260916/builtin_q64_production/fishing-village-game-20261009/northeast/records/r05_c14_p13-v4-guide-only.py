from PIL import Image
from pathlib import Path
import json,hashlib
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast")
src=z/"native/r05_c14_p13-v1.png"; left=z/"native/r05_c14_p12-v1.png"; bottom=z/"native/r05_c14_p23-v1.png"
im=Image.open(src).convert("RGB")
im.paste(Image.open(bottom).crop((0,0,1254,230)),(0,1024))
im.paste(Image.open(left).crop((1024,650,1254,1254)),(0,650))
gp=z/"guides/r05_c14_p13-v4.native-rock-only-repair-guide.png"; im.save(gp)
def rec(p,role):return {"path":str(p).replace("\\","/"),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"role":role}
(gp.with_name(gp.name+".derived.json")).write_text(json.dumps({"purpose":"native rock geometry repair guide only; not final pixels","operation":"1:1 integer opaque crop/paste; no resize/paint/feather","sources":[rec(src,"v1 boat and native target base"),rec(left,"real left rock region y650..1254"),rec(bottom,"real bottom strip")],"leftCrop":[1024,650,1254,1254],"leftPaste":[0,650],"bottomCrop":[0,0,1254,230],"bottomPaste":[0,1024]},indent=2),encoding="utf-8")
print(gp)

