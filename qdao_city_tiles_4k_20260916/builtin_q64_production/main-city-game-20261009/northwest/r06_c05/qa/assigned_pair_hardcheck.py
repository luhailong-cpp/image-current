import json
from pathlib import Path
import numpy as np
from PIL import Image
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c05")
sel=json.loads((b/"selection.json").read_text())
for top,bottom in [("s01_01","s02_01"),("s03_02","s04_02")]:
 a=np.array(Image.open(sel[top]).convert("RGB"));c=np.array(Image.open(sel[bottom]).convert("RGB"))
 joined=np.concatenate([a[:1139],c[115:]],axis=0)
 Image.fromarray(joined[924:1354]).save(b/"qa"/f"pair-{top}-{bottom}-hard-native.png")

