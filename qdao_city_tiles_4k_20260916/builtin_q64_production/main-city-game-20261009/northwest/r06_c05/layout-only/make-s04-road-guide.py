from PIL import Image, ImageDraw
from pathlib import Path
import json, hashlib
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c05")
out=b/"layout-only/s04_03.straight-band-coordinate-guide.png"
guide=Image.new("RGB",(1254,1254),(223,219,212))
guide.paste(Image.open(b/"native/s04_03_roadalign01.png").crop((0,0,230,1254)),(0,0))
d=ImageDraw.Draw(guide)
d.rectangle((515,0,584,1253),fill=(239,235,224))
d.rectangle((585,0,934,1253),fill=(151,168,181))
d.rectangle((935,0,1004,1253),fill=(239,235,224))
guide.save(out)
out.with_suffix(".png.derivation.json").write_text(json.dumps({"gameArt":False,"role":"explicit geometry reference only; native generation required","size":[1254,1254],"worldBox":[18317,23437,19571,24691],"blueBodyNativeX":[585,935],"paleBorderOuterNativeX":[515,1005],"y":[0,1254],"authorization":"Parent via joint_repair_continue: straight alignment to accepted s02_03 actual L; replaces earlier wider blurred-layout body","sourceWestAnchor":"native/s04_03_roadalign01.png","sourceWestCrop":[0,0,230,1254],"operation":"flat colored guide rectangles plus exact230px west; no generated final art"},indent=2),encoding="utf-8")
print(out)

