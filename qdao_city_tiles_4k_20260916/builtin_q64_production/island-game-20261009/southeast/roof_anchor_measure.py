from workflow import *
from PIL import Image
import numpy as np
e=np.asarray(Image.open(ROOT/'native/r09_c12_roof_surface_e_v01.png').convert('RGB')).astype(np.int16)
f=np.asarray(Image.open(ROOT/'native/r09_c12_roof_surface_f_v02.png').convert('RGB')).astype(np.int16)
d=np.asarray(Image.open(ROOT/'native/r09_c12_roof_surface_d_v01.png').convert('RGB')).astype(np.int16)
out={}
for name,a,b in [('ef',e[:,1024:],f[:,:230]),('fd',f[:,1024:],d[:,:230])]:
 diff=np.abs(a-b).mean(axis=2);sm=np.convolve(diff.mean(axis=0),np.ones(7)/7,'same');ids=np.argsort(sm[8:-8])[:15]+8
 out[name]={'bestColumns':ids.tolist(),'meanDifference':[round(float(sm[i]),3) for i in ids],'at115':float(sm[115]),'minimumMean':float(sm[ids[0]])}
print(out);write(ROOT/'qa/roof-f02-full-trial/anchor-measurements.json',out)
