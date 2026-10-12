from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent
arr={k:np.asarray(Image.open(D/f).convert('RGB')).astype(int) for k,f in [('orig','bench-G3-left-conditioned-v6-before-guide-native1254.png'),('raw','bench-G3-left-conditioned-v9-raw.png')]}
out=[]
for x in range(630,746,4):
 rec={'x':x};e=round(380+(x-567)*.49)
 for k,a in arr.items():
  vals=[]
  for y in range(e-15,e+16):
   q=a[y:y+16,x];t=(q[:,0]>230)&(q[:,1]>175)&(q[:,2]<220)
   if t.sum()>=14:vals.append(y);break
  rec[k]=vals[0] if vals else None
 out.append(rec)
print(json.dumps(out))

