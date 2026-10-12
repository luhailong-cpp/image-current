from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent
arr={k:np.asarray(Image.open(D/f).convert('RGB')).astype(int) for k,f in [('orig','bench-G3-left-conditioned-v9b-bounded-preview-native1254.png'),('raw','bench-G3-left-conditioned-v10-raw.png')]}
out=[]
for x in range(690,770,4):
 e=round(545+(x-710)*.45);rec={'x':x}
 for k,a in arr.items():
  yy=np.arange(e-10,e+11);score=a[yy,x,1]+a[yy,x,2];rec[k]=int(yy[score.argmax()])
 out.append(rec)
print(json.dumps(out))

