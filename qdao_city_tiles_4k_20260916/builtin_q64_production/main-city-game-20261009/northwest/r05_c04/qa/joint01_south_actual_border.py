from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c04")
sys.path.insert(0,str(B.parent)); import assemble_native as asm
neighbor=B.parent/"r06_c04"
arrays,sources,missing=asm.load_sources(neighbor,[12288,20480,16384,24576])
strip=arrays[0,0]; paths=[]
for c in range(1,4):
 strip,seam=asm.append_with_minimum_seam(strip,arrays[0,c])
 paths.append(seam.tolist())
south=strip[115:275,115:4211]
north=np.array(Image.open(B/"candidate/r05_c04-candidate-minimum-error-6b0f7ef07937.png"))[-160:]
actual=np.concatenate([north,south],axis=0)
files=[]
for c in range(4):
 p=B/"qa"/f"s04_02_joint01-south-actual-border-segment{c+1:02d}.png"
 Image.fromarray(actual[:,c*1024:(c+1)*1024]).save(p); files.append(str(p))
report={"method":"north formal candidate final160rows directly abutted to southern first-row native horizontal-minimum-error assembly core-first160rows; no vertical seam blending, pixel changes, resize or color adjustment","borderWorldY":20480,"northTileCandidate":r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r05_c04/candidate/r05_c04-candidate-minimum-error-6b0f7ef07937.png","southNativeSources":[x for x in sources if x["row"]==1],"southHorizontalPaths":paths,"files":files,"scope":"full south edge only. Other outer edges pending."}
(B/"qa/s04_02_joint01-south-actual-border.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({"files":files},indent=2))

