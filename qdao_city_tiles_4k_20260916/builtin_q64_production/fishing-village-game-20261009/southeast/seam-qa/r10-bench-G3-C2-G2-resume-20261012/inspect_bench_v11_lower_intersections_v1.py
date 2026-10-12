from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent
arr={k:np.asarray(Image.open(D/f).convert('RGB')).astype(int) for k,f in [('base','bench-G3-left-conditioned-v10b-bounded-preview-native1254.png'),('raw','bench-G3-left-conditioned-v11-raw.png')]}
out=[]
for x in range(530,766,4):
 e=round(582+(x-449)*.45);rec={'x':x}
 for k,a in arr.items():
  yy=np.arange(e-20,e+21);score=a[yy,x].mean(1);rec[k]=int(yy[score.argmin()])
 out.append(rec)
print(json.dumps(out))

