from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent
a=np.asarray(Image.open(D/'eastdeck-G2-conditioned-v1-guide-native1254.png').convert('RGB'))
out={}
for x in [439,850]:
 v=a[:,x,:].mean(1); ys=np.flatnonzero((v<120)&(np.arange(1254)>220)&(np.arange(1254)<1220))
 groups=np.split(ys,np.where(np.diff(ys)>1)[0]+1)
 out[x]=[{'first':int(g[0]),'last':int(g[-1]),'darkest':int(g[v[g].argmin()]),'mean':float(v[g].min())} for g in groups if len(g)>=2]
print(json.dumps(out))

