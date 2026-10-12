from PIL import Image,ImageChops
from pathlib import Path
import json,hashlib
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast");Q=Z/"qa/r05_c14-v4"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
baseline=Z/"tiles/r05_c14.candidate-v1.png";candidate=Z/"tiles/r05_c14.candidate-v4.png";bridge=Z/"native/r05_c14_bridge01-v1.png"
a=Image.open(baseline).convert("RGB");c=Image.open(candidate).convert("RGB");b=Image.open(bridge).convert("RGB")
expected=a.copy();expected.paste(b.crop((371,371,883,883)),(2931,2701));assert ImageChops.difference(expected,c).getbbox() is None
bbox=ImageChops.difference(a,c).getbbox();assert bbox[0]>=2931 and bbox[1]>=2701 and bbox[2]<=3443 and bbox[3]<=3213
d={"status":"exact_native_contribution_verified","candidate":{"path":str(candidate).replace("\\","/"),"sha256":sha(candidate)},"candidateSize":list(c.size),"baseline":{"path":str(baseline).replace("\\","/"),"sha256":sha(baseline)},"bridge":{"path":str(bridge).replace("\\","/"),"sha256":sha(bridge),"nativeSize":list(b.size)},"bridgeSourceCropBox":[371,371,883,883],"candidateDestinationBox":[2931,2701,3443,3213],"worldContributionBox":[56179,19085,56691,19597],"actualDifferenceBoundingBox":list(bbox),"candidateEqualsBaselinePlusOnlyExactBridgeCrop":True,"outsideContributionPixelsUnchanged":True,"noResizePaintFeather":True,"notNative4KGeneration":True}
(Q/"exact-contribution-validation.json").write_text(json.dumps(d,indent=2),encoding="utf-8")
print(json.dumps(d))

