from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent
orig=np.asarray(Image.open(D/'bench-G3-left-conditioned-v6-before-guide-native1254.png').convert('RGB'))
out=[]
for x in range(460,750,10):
 rec={'x':x}
 for name,file in [('orig',None),('v4','bench-G3-left-conditioned-v4-raw.png'),('v6','bench-G3-left-conditioned-v6-raw.png'),('v7','bench-G3-left-conditioned-v7-raw.png'),('v8','bench-G3-left-conditioned-v8-raw.png')]:
  a=orig if file is None else np.asarray(Image.open(D/file).convert('RGB'))
  ys=np.arange(320,480);gold=(a[ys,x,0]>240)&(a[ys,x,1]>160)&(a[ys,x,2]<220)
  y=ys[gold];rec[name]=int(y[0]) if len(y) else None
 out.append(rec)
print(json.dumps(out))

