from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r11_c05/refinement-resume20261010/p04_02-local-joint")
A=np.array(Image.open(Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")/'r11_c05/native/p04_02.png').convert('RGB'))
B=np.array(Image.open(D/'native/p04_02-joint-v1.png').convert('RGB'))
print('dimensions',A.shape,B.shape)
for x in [230,240,250,260,280,300,320,340,360,400,500,600,700,760,800]:
 y=int(1175-.83*x);lo=max(0,y-30);hi=min(1254,y+31)
 print(x,lo+np.argmin(A[lo:hi,x].mean(axis=1)),lo+np.argmin(B[lo:hi,x].mean(axis=1)))
Image.fromarray(A[820:1040,220:460]).save(D/'qa/incoming-before.png')
Image.fromarray(B[820:1040,220:460]).save(D/'qa/incoming-generated.png')
Image.fromarray(A[450:640,680:900]).save(D/'qa/junction-before.png')
Image.fromarray(B[450:640,680:900]).save(D/'qa/junction-generated.png')

