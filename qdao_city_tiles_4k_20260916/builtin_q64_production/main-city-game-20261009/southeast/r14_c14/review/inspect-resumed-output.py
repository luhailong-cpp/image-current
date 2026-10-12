from pathlib import Path
from PIL import Image
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r14_c14/repairs")
for v in ["upper-left-20261011T060818-6e7f4444","lower-right-fullgeometry-20261011T061451-0923b3cc"]:
 d=t/v
 boxes=[(490,150,740,360),(480,925,735,1140)] if v.startswith("upper") else [(0,410,270,710),(700,1050,1050,1254)]
 for n,box in enumerate(boxes):
  for f in ["source-1254.png","native.png","review-composed-1254.png"]:
   Image.open(d/f).crop(box).save(d/(f"inspect{n}-"+f))
print("ready")

