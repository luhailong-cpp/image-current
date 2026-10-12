from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent;a=np.asarray(Image.open(D/'bench-C2-right-conditioned-v1-guide-native1254.png').convert('RGB'));out=[]
for x in [572,600,621,650,700,750,800,850,880]:
 t=round(382+(x-572)*199/308);b=round(780-(x-572)*199/308);v=a[:,x].mean(1)
 out.append({'x':x,'upperExpected':t,'upperDarkest':int(v[t-20:t+15].argmin()+t-20),'lowerExpected':b,'lowerRowsGold':[int(y) for y in range(b-20,b+16) if int(a[y,x,0])>235 and int(a[y,x,1])>160]})
print(json.dumps(out))

