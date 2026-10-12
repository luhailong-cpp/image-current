from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json
D=Path(__file__).parent
a=np.asarray(Image.open(D/'merged-three-v1/column02-context.png').crop((0,1085,1254,2339)).convert('RGB')).astype(float)
b=np.asarray(Image.open(D/'bridge-shading-work/bridge-v1-native.png').convert('RGB')).astype(float)
for x0,x1 in [(350,550),(550,752),(350,752),(0,1254)]:
 d=np.mean(np.abs(a[:,:,:][...,][...,]-b),axis=2)[:,x0:x1].mean(axis=1)
 print(x0,x1,'candidates',[(lo,hi,int(np.argmin(d[lo:hi])+lo),round(float(np.min(d[lo:hi])),2)) for lo,hi in [(0,100),(100,300),(300,450),(800,950),(950,1150),(1150,1254)]])
 print('means',[(y,np.round((a[y:y+20,x0:x1]-b[y:y+20,x0:x1]).mean((0,1)),2).tolist()) for y in [0,50,100,200,300,400,850,950,1050,1150,1230]])
