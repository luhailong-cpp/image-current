import sys,json
from pathlib import Path
import numpy as np
from PIL import Image
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c05");sys.path.insert(0,str(b.parent))
from assemble_native import append_with_minimum_seam
a=np.array(Image.open(b/"native/s03_02_fulljoint03.png").convert("RGB"));c=np.array(Image.open(b/"native/s04_02.png").convert("RGB"))
joined,seam=append_with_minimum_seam(a.transpose(1,0,2),c.transpose(1,0,2));joined=joined.transpose(1,0,2)
Image.fromarray(joined[924:1354]).save(b/"qa/s03_02_fulljoint03-south-mincut.png")
hard=np.concatenate([a[:1139],c[115:]],axis=0);Image.fromarray(hard[924:1354]).save(b/"qa/s03_02_fulljoint03-south-hard.png")
print(float(np.abs(a[-230:].astype(float)-c[:230]).mean()))

