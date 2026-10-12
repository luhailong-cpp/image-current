from PIL import Image
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
D.mkdir(exist_ok=True)
b=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")/"integrated-20261011/v2/r11_c06.candidate.png"
im=Image.open(b);im.crop([0,1050,1254,2304]).save(D/"baseline-crop.png")
for name,p in [("06",Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r11_c06")/"repairs-resume20261011/06-bottom-step-focused/rejected-native.png"),("07",Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r11_c06")/"repairs-resume20261011/07-bottom-step-width/rejected-native.png")]:
 n=Image.open(p);n.crop([150,240,800,540]).save(D/f"{name}-step-native-crop.png")
im.crop([150,1290,800,1590]).save(D/"baseline-step-crop.png")

