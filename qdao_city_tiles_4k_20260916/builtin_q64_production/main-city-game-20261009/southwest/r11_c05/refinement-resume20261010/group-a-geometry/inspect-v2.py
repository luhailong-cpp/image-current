from PIL import Image
from pathlib import Path
import numpy as np
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r11_c05/refinement-resume20261010/group-a-geometry")
A=np.array(Image.open(D/'input/group-a-target.native1254.png'));B=np.array(Image.open(D/'native/group-a-v2.png'))
for x in [540,560,600,650,700,750,800,835,880,920,950]:
 y=int(.95*x+302);l=max(0,y-35);h=min(1254,y+36)
 print(x,int(l+np.argmin(A[l:h,x].mean(1))),int(l+np.argmin(B[l:h,x].mean(1))))
for x in [300,350,400,420,450,480,495,515,535,555,575,595]:
 y=int(730-.675*x);l=max(0,y-25);h=min(1254,y+26)
 print('upper',x,int(l+np.argmin(A[l:h,x].mean(1))),int(l+np.argmin(B[l:h,x].mean(1))))
Image.fromarray(B[1040:1220,680:930]).save(D/'qa/v2-lower-junction.png')
Image.fromarray(B[760:885,490:610]).save(D/'qa/v2-extension-old-joint.png')

