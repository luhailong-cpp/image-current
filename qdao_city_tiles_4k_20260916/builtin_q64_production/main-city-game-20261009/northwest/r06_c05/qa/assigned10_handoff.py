import sys,json
from pathlib import Path
import numpy as np
from PIL import Image
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c05");sys.path.insert(0,str(b.parent))
from assemble_native import append_with_minimum_seam,sha
sel=json.loads((b/"selection.json").read_text())
def source(id):return np.array(Image.open(sel[id]).convert("RGB"))
a,c=source("s03_01"),source("s03_02")
joined,seam=append_with_minimum_seam(a,c)
Image.fromarray(joined[:,924:1354]).save(b/"qa/s03_02-fulljoint03-west-native.png")
for row in [2,3]:
 up,_=append_with_minimum_seam(source(f"s{row:02d}_01"),source(f"s{row:02d}_02"))
 dn,_=append_with_minimum_seam(source(f"s{row+1:02d}_01"),source(f"s{row+1:02d}_02"))
 both,_=append_with_minimum_seam(up.transpose(1,0,2),dn.transpose(1,0,2));both=both.transpose(1,0,2)
 Image.fromarray(both[774:1504,774:1504]).save(b/"qa"/f"s03_02-fulljoint03-junction-r{row}-native.png")
out=[]
for row,col in [(r,c) for r in [1,2] for c in range(1,5)]+[(3,1),(3,2)]:
 id=f"s{row:02d}_{col:02d}";p=Path(sel[id]);meta=json.loads(p.with_suffix(".png.generation.json").read_text())
 out.append({"patch":id,"selected":str(p),"sha256":sha(p),"nativeSize":[meta.get("width"),meta.get("height")],"actualModel":meta.get("actualModel"),"actualQuality":meta.get("actualQuality"),"record":str(p.with_suffix(".png.generation.json"))})
(b/"qa"/"assigned10-source-handoff.json").write_text(json.dumps({"scope":"top two rows plus s03_01 and s03_02","sources":out,"wholeTileAcceptance":"pending root full assembly QA","progressUpdated":False,"s02_01":"delegated to south worker for suspended diagonal upper-floor repair"} ,indent=2))

