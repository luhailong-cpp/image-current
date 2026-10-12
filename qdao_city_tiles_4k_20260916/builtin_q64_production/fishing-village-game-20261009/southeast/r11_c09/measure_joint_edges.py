from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
for name in ['layout-only/joint-p32-p33-native-crop.png','native/joint-p32-p33-v1.png','native/joint-p32-p33-v2.png']:
 a=np.array(Image.open(R/name)).astype(float)
 print(name)
 for x in [0,16,32,48,64,80,96,112,128,440,480,520,580,626,628,680,720]:
  c=np.median(a[:,max(0,x-2):x+3],axis=1);ground=(c[:,0]-c[:,1]<42)&(c[:,1]>75)&(np.arange(1254)>350)
  ys=np.flatnonzero(ground)
  print(x,int(ys[0]) if len(ys) else -1,end='; ')
 print()
b=np.array(Image.open(R/'layout-only/joint-p32-p33-native-crop.png')).astype(float)
j=np.array(Image.open(R/'native/joint-p32-p33-v1.png')).astype(float)
d=np.abs(j-b)
for box in [(0,300,128,520),(0,900,1000,1020),(840,300,1020,1020),(0,270,1000,360)]:
 x,y,x2,y2=box;v=d[y:y2,x:x2];print(box,'mean',v.mean(),'p90',np.percentile(v,90),'median',np.median(v))

