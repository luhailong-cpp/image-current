from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent
files={'orig':'bench-G3-left-conditioned-v6-before-guide-native1254.png','v4':'bench-G3-left-conditioned-v4-raw.png','v6':'bench-G3-left-conditioned-v6-raw.png','v7':'bench-G3-left-conditioned-v7-raw.png','v8':'bench-G3-left-conditioned-v8-raw.png'}
arrays={k:np.asarray(Image.open(D/f).convert('RGB')).astype(int) for k,f in files.items()}
out=[]
for x in range(500,749,5):
 rec={'x':x}
 for name,a in arrays.items():
  expect=round(344+(x-449)*.43) if x<567 else round(380+(x-567)*.49)
  candidates=[]
  for y in range(expect-25,expect+26):
   q=a[y:y+16,x];t=(q[:,0]>230)&(q[:,1]>175)&(q[:,2]<220)
   if t.sum()>=14:candidates.append(y);break
  rec[name]=candidates[0] if candidates else None
 out.append(rec)
print(json.dumps(out))

