from PIL import Image
from pathlib import Path
import json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast")
src=Z/"tiles/r05_c14.candidate-v1.png";out=Z/"guides/r05_c14-bridge01-v1.native-context.png"
Image.open(src).crop((2560,2330,3814,3584)).save(out)
d={"purpose":"native1:1 repair bridge context ONLY, never final pixels by itself","source":{"path":str(src).replace("\\","/"),"sha256":hashlib.sha256(src.read_bytes()).hexdigest()},"sourceCropBox":[2560,2330,3814,3584],"worldBox":[55808,18714,57062,19968],"size":[1254,1254],"operation":"exact integer crop; no resizing/paint/feather","resized":False,"artifactWorld":[56435,19341],"artifactBridgeNative":[627,627]}
Path(str(out)+".derived.json").write_text(json.dumps(d,indent=2),encoding="utf-8")
print(hashlib.sha256(out.read_bytes()).hexdigest())

