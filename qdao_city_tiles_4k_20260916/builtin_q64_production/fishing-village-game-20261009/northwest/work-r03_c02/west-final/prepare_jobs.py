from pathlib import Path
import json,hashlib
from PIL import Image
from datetime import datetime,timezone
R=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");D=R/"work-r03_c02/west-final"
jobs=json.loads((D/"jobs.json").read_text())
Image.open(D/"joint0-pair.png").crop((5880-4096,9475-8192,7134-4096,10729-8192)).save(D/"M2-target.png")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for j in jobs:
 refs=j["refs"];roles=["exact-native-scale-object-edit-target"]+(["complete-object-context-only"] if j["extra"] else [])+["approved-map-layout","approved-material-closeup","approved-daoist-Q-style"]
 req={"id":j["id"],"tool":"image_gen.imagegen","prompt":j["prompt"],"referenced_image_paths":refs,"references":[{"file":p,"sha256":sha(p),"role":role} for p,role in zip(refs,roles)],"transparent_background":False,"submittedAt":datetime.now(timezone.utc).isoformat(),"submittedParameters":{"model":None,"quality":None},"globalNativeBox":j["box"],"actualModel":None,"actualQuality":None}
 (D/(j["id"]+".prompt.txt")).write_text(j["prompt"],encoding="utf8")
 (D/(j["id"]+".request.json")).write_text(json.dumps(req,indent=2),encoding="utf8")
print("prepared 3 exact-native object edits")

