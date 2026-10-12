import sys,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest")
sys.path.insert(0,str(z))
from assemble_native import append_with_minimum_seam,sha
b=z/"r06_c05"
sel=json.loads((b/"selection.json").read_text())
pairs=[("s01_01","s02_01"),("s03_02","s04_02"),("s03_01","s04_01"),("s02_02","s03_02")]
out=[]
for top,bottom in pairs:
 a=np.array(Image.open(sel[top]).convert("RGB"));c=np.array(Image.open(sel[bottom]).convert("RGB"))
 joined,seam=append_with_minimum_seam(a.transpose(1,0,2),c.transpose(1,0,2))
 joined=joined.transpose(1,0,2)
 p=b/"qa"/f"pair-{top}-{bottom}-native.png"
 Image.fromarray(joined[924:1354]).save(p)
 out.append({"top":top,"bottom":bottom,"topFile":sel[top],"bottomFile":sel[bottom],"topSha":sha(Path(sel[top])),"bottomSha":sha(Path(sel[bottom])),"qaFile":str(p),"method":"native binary minimum-error overlap; crop only, no blend/rescale/warp","overlapMeanAbsoluteDifference":float(np.abs(a[-230:].astype(float)-c[:230]).mean()),"cutRange":[int(seam.min()),int(seam.max())]})
(b/"qa"/"assigned-pairs-20261010.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

