from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast/seam-qa/independent-20261010/repair-candidates')
for f in ['r12c08-rail-input-100pct.png','r12c08-rail-joint-v1.png','r12c08-rail-joint-v2.png','r12c08-rail-joint-v3.png']:
 a=np.asarray(Image.open(D/f).convert('RGB')).astype(float)
 rec={}
 for x in [535,600,700,800,900,1000,1100,1200]:
  v=a[:,x]; m=(v[:,0]-v[:,1]>28)&(v[:,1]-v[:,2]>22)&(v[:,0]>105)&(np.arange(len(v))>50)&(np.arange(len(v))<950)
  edges=np.diff(np.r_[False,m,False].astype(int)); spans=list(zip(np.where(edges==1)[0].tolist(),np.where(edges==-1)[0].tolist())); rec[x]=[e for e in spans if e[1]-e[0]>15]
 print(f,rec)

