from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-audit-line-20261011");out={}
for a in ["roof-vertical-join-v01","blue-border-south-join-v01"]:
 old=np.array(Image.open(D/a/"input.png")).astype(float);new=np.array(Image.open(D/a/"native.png")).astype(float);diff=np.abs(old-new)
 o={}
 for name,b in {"left":[0,0,8,1254],"right":[1246,0,1254,1254],"top":[0,0,1254,8],"bottom":[0,1246,1254,1254],"leftBlue":[0,300,50,500],"rightBlue":[1200,200,1254,350],"leftRoof":[0,700,10,960],"rightRoof":[1244,300,1254,850]}.items():
  x0,y0,x1,y1=b;o[name]={"oldMean":old[y0:y1,x0:x1].mean((0,1)).round(1).tolist(),"newMean":new[y0:y1,x0:x1].mean((0,1)).round(1).tolist(),"absoluteMean":round(float(diff[y0:y1,x0:x1].mean()),2),"p95":round(float(np.percentile(diff[y0:y1,x0:x1],95)),2)}
 out[a]=o
print(json.dumps(out,indent=2))
(D/"cross-second-boundary-color-evidence.json").write_text(json.dumps(out,indent=2))

