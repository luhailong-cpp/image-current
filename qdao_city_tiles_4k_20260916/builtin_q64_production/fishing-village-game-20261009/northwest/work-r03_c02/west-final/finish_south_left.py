from pathlib import Path
from PIL import Image
import numpy as np,json,sys

def finish(a,ids,m,D):
 sys.path.insert(0,str(D.parent.parent/'work-r03_c04'))
 from apply_r03_c04_repairs import minimum_path
 x0,x1,y0,y1=8077,8192,12173,12288
 prev=a[y0-8192:y1-8192,x0-4096:x1-4096].copy()
 srcs={k:np.asarray(Image.open(m['sources'][str(k)]['file'])) for k in [513,520]}
 b=m['sources']['513']['globalNativeBox'];new=srcs[513][y0-b[1]:y1-b[1],x0-b[0]:x1-b[0]].copy();ni=np.full(new.shape[:2],513,dtype=np.uint16)
 yb=12173;ba=m['sources']['520']['globalNativeBox'];lower=srcs[520][yb-ba[1]:y1-ba[1],x0-ba[0]:x1-ba[0]]
 c=np.sum((new[yb-y0:].astype(np.int32)-lower.astype(np.int32))**2,axis=2,dtype=np.int64)+1
 # The final path endpoint is the already accepted right-side join at global y=12249.
 c[:, -1]+=10**12;c[12249-yb,-1]-=10**12
 path,_=minimum_path(c.T,1,114)
 yy=np.arange(y1-yb)[:,None];choose=yy>=path[None,:]
 new[yb-y0:][choose]=lower[choose];ni[yb-y0:][choose]=520
 c=np.sum((prev.astype(np.int32)-new.astype(np.int32))**2,axis=2,dtype=np.int64)+1
 left,_=minimum_path(c,5,90)
 tc=c.copy();tc[:,-1]+=10**12;tc[0,-1]-=10**12
 top,_=minimum_path(tc.T,0,100)
 yy,xx=np.indices(c.shape);mask=(xx>=left[:,None])&(yy>=top[None,:])
 a[y0-8192:y1-8192,x0-4096:x1-4096][mask]=new[mask]
 ids[y0-8192:y1-8192,x0-4096:x1-4096][mask]=ni[mask]
 p=D/'south-left-object-mask.png';Image.fromarray(mask.astype(np.uint8)*255).save(p)
 return {'globalBox':[x0,y0,x1,y1],'maskFile':str(p),'selectedPixels':int(mask.sum()),'sourceIds':[513,520],'leftXByY':left.tolist(),'topYByX':top.tolist(),'southSourceTransitionYByX':(path+yb).tolist(),'rightSouthBandUnchanged':True}
