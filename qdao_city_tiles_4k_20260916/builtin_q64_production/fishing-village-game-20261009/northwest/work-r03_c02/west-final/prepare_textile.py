from pathlib import Path
from PIL import Image
import json
R=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest");D=R/"work-r03_c02/west-final";im=Image.open(D/"internal1-pair.png")
for name,b in [("E2-roll-target",[7510,10850,8764,12104]),("E2-fold-target",[7700,11034,8954,12288]),("E2-whole-context",[7500,11050,9000,12288])]:
 im.crop((b[0]-4096,b[1]-8192,b[2]-4096,b[3]-8192)).save(D/(name+".png"))

