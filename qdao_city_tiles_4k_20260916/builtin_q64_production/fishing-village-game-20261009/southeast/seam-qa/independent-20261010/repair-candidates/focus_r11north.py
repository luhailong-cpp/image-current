from pathlib import Path
from PIL import Image
P=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/seam-qa/independent-20261010/r11_c08-final-external')
Image.open(P/'north-segment-3-100pct.png').crop((285,0,525,400)).save(P/'north-segment-3-left-adoption-focus.png')

