from pathlib import Path
from PIL import Image
import hashlib,json
root=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest"); out=root/"work-r03_c04/paving-fresh"
p=root/"work-r03_c04/tiles/r03_c04.candidate.png"; dst=out/"junction-shape-target.png"
Image.open(p).crop((350,420,1604,1674)).save(dst)
d={"source":str(p),"sourceSha256":hashlib.sha256(p.read_bytes()).hexdigest(),"cropBox":[350,420,1604,1674],"globalNativeBox":[12638,8612,13892,9866],"noResample":True,"operation":"exact crop for image-generation edit input"}
(out/"junction-shape-target.derivation.json").write_text(json.dumps(d,indent=2))

