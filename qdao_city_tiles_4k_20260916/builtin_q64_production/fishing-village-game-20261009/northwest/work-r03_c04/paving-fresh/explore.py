from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
root=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest")
out=root/"work-r03_c04/paving-fresh";out.mkdir(exist_ok=True)
sys.path.insert(0,str(root/"work-r03_c04"))
from apply_r03_c04_repairs import minimum_path
base=np.asarray(Image.open(root/"work-r03_c04/guides/r03_c04_repair_paving_junction_v01.target.png")).copy()
for ver in [1,2,3,4]:
 src=np.asarray(Image.open(root/f"native/r03_c04_repair_paving_junction_v{ver:02d}.png"))
 diff=base.astype(np.int32)-src.astype(np.int32)
 cost=np.sum(diff*diff,axis=2,dtype=np.int64)+10
 left,_=minimum_path(cost,300,600)
 right,_=minimum_path(cost,1060,1190)
 top,_=minimum_path(cost.T,230,410)
 bot,_=minimum_path(cost.T,970,1130)
 yy,xx=np.indices(cost.shape)
 mask=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bot[None,:])
 dst=base.copy();dst[mask]=src[mask]
 Image.fromarray(dst).save(out/f"test{ver:02d}.png")
 Image.fromarray(mask.astype(np.uint8)*255).save(out/f"test{ver:02d}.mask.png")
 print(ver,int(mask.sum()))

