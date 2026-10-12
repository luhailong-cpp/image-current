from workflow import *
from PIL import Image
import numpy as np
base=ROOT/'tiles/r09_c12.candidate-v04.png';src=ROOT/'native/r09_c12_roof_surface_d_v01.png';crop=[200,470,490,745];dest=[1851,1212,2141,1487];im=Image.open(base).convert('RGB');patchim=Image.open(src).convert('RGB').crop(crop);assert patchim.size==(dest[2]-dest[0],dest[3]-dest[1]);im.paste(patchim,dest[:2]);parts=[]
def subtract(a,b):
 x0,y0,x1,y1=a;u0,v0,u1,v1=b;ix0,iy0,ix1,iy1=max(x0,u0),max(y0,v0),min(x1,u1),min(y1,v1)
 if ix0>=ix1 or iy0>=iy1:return [a]
 return [q for q in [[x0,y0,x1,iy0],[x0,iy1,x1,y1],[x0,iy0,ix0,iy1],[ix1,iy0,x1,iy1]] if q[0]<q[2] and q[1]<q[3]]
for r in read(Path(str(base)+'.generation.json'))['contributions']:
 for box in subtract(r['destinationBox'],dest):
  p=dict(r);x,y,_,_=r['destinationBox'];sx,sy,_,_=r['sourceCrop'];p.update({'sourceCrop':[sx+box[0]-x,sy+box[1]-y,sx+box[2]-x,sy+box[3]-y],'destination':box[:2],'destinationBox':box});parts.append(p)
parts.append({'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':dest[:2],'destinationBox':dest,'record':str(src)+'.generation.json'})
out=ROOT/'tiles/r09_c12.candidate-v05.png';assert not out.exists();im.save(out);cover=np.zeros((4096,4096),dtype=np.uint8);replay=Image.new('RGB',(4096,4096))
for p in parts:
 a=Image.open(p['file']).convert('RGB').crop(p['sourceCrop']);x0,y0,x1,y1=p['destinationBox'];cover[y0:y1,x0:x1]+=1;replay.paste(a,(x0,y0))
assert np.all(cover==1) and replay.tobytes()==im.tobytes()
write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'width':4096,'height':4096,'generatedAt':now(),'operation':'Exact unscaled native rectangles; no painting or blend','contributions':parts,'base':str(base),'baseSha256':sha(base),'fullCoverage':True,'allContributionsPixelExact':True,'pixelCoverageMin':1,'pixelCoverageMax':1,'actualModel':None,'actualQuality':None,'status':'pending_eave_patch_perimeter_review'})
q=ROOT/'qa/roof-surface-v01/eave-insertion.png';im.crop([1791,1152,2201,1547]).save(q)
write(Path(str(q)+'.generation.json'),{'file':str(q),'sha256':sha(q),'source':str(out),'sourceSha256':sha(out),'sourceCrop':[1791,1152,2201,1547],'nativeSourceCrop':crop,'destinationBox':dest,'operation':'100 percent actual candidate crop; source insert at [60,60,350,335]'})
print(str(out));print(sha(out))

