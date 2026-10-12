from PIL import Image
import numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
a=Image.open(P/'south-crossedge.v1.target.png');b=Image.open(P/'south-crossedge.v1.native.png')
print('dimensions',b.size)
a.crop((440,840,740,1080)).save(P/'S2.before.png');b.crop((440,840,740,1080)).save(P/'S2.native.png')
for x in [500,550,600,627,650,680,700,750,800]:
 lo,hi=int(.835*x+445),int(.835*x+495)
 print(x,[int(np.array(im.convert('L'))[lo:hi,x].argmin())+lo for im in [a,b]])
v1=np.array(a.convert('L'));v2=np.array(b.convert('L'))
ok=[]
for x in range(670,940):
 lo,hi=int(.8*x+469),int(.8*x+507)
 ya=int(v1[lo:hi,x].argmin())+lo;yb=int(v2[lo:hi,x].argmin())+lo
 if ya==yb:ok.append([x,ya])
print('matching positions',ok[:70])
