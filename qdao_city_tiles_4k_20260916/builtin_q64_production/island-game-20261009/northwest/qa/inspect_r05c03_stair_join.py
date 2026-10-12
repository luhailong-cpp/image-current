from pathlib import Path
from PIL import Image
import json,hashlib
Z=Path(__file__).resolve().parents[1]
p=Z/'tiles/r05_c03_candidate-v5_4096.png'
out=Z/'qa/r05_c03_stair_join_v5_100pct.png'
Image.open(p).crop((1260,2840,1790,3370)).save(out)
print(out)
