from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent;a=np.asarray(Image.open(D/'bench-C2-right-conditioned-v1-guide-native1254.png').convert('RGB'));out=[]
for x in [572,600,621,650,700,750,800,850,880]:
 t=round(382+(x-572)*199/308)
 out.append({'x':x,'samples':[[y,a[y,x].tolist()] for y in range(t-20,t+13,4)]})
print(json.dumps(out))

