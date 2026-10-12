from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(__file__).resolve().parent
a=np.asarray(Image.open(D/'bench-C2-right-conditioned-v4-bounded-preview-native1254.png').convert('RGB'));b=np.asarray(Image.open(D/'bench-C2-right-conditioned-v5-raw.png').convert('RGB'));out=[]
for x in [590,620,621,650,680,710]:
 t=round(754-(x-555)*.505)+4
 out.append({'x':x,'maskTop':t,'original':[[y,a[y,x].tolist()] for y in range(t-5,t+11)],'raw':[[y,b[y,x].tolist()] for y in range(t-5,t+11)]})
print(json.dumps(out))

