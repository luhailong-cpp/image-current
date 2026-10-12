from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05");D=B/"repairs-audit-line-20261011"
def rows(file,x):
 a=np.asarray(Image.open(file).convert("RGB")).mean(2);v=a[:,max(0,x-1):min(1254,x+2)].mean(1);xs=np.flatnonzero(v<190);runs=[]
 for z in xs:
  if not runs or z>runs[-1][-1]+1:runs.append([int(z)])
  else:runs[-1].append(int(z))
 return [[min(q),max(q),round(float(v[q].min()),1)] for q in runs]
out={}
for f in ["p01_03-macro-rebuild-v01","p01_03-quiet-material-v02","p03_03-coordination-v02","p02_02-macro-rebuild-v01","p02_02-macro-rebuild-v02"]:
 out[f]={str(x):rows(D/f/"native.png",x) for x in [0,115,230,417,627,1024,1139,1253]}
out["p0302-neighbor"]={str(x):rows(B/"native/p03_02.png",x) for x in [1024,1139,1253]}
(D/"native-line-profile-evidence.json").write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

