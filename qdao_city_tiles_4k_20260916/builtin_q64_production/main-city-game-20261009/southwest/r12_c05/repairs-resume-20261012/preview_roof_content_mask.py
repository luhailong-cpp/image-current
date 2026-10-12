from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012/roof-color-east-cap-v01')
orig=Image.open(T/'input.png').convert('RGB');nat=Image.open(T/'native.png').convert('RGB');oa=np.array(orig).astype(float);na=np.array(nat).astype(float);dif=np.abs(oa-na).mean(axis=2)
def route(xlo,xhi,ylo,yhi,center):
 # Mechanical copy boundary chosen where existing and generated paint already match best.
 # This only selects source pixels; no source image pixel is painted, recolored or resized.
 cost=dif[ylo:yhi,xlo:xhi].copy();xs=np.arange(xlo,xhi);cost+=.001*(xs-center)**2
 h,w=cost.shape;dp=cost[0].copy();back=np.zeros((h,w),dtype=np.int16)
 for y in range(1,h):
  new=np.full(w,np.inf)
  for step in range(-2,3):
   idx=np.clip(np.arange(w)+step,0,w-1);v=dp[idx]+.3*abs(step);better=v<new;new[better]=v[better];back[y,better]=idx[better]
  dp=new+cost[y]
 result=np.zeros(h,dtype=int);result[-1]=int(dp.argmin())
 for y in range(h-1,0,-1):result[y-1]=back[y,result[y]]
 return result+xlo
ylo,yhi=308,1254;left=route(635,731,ylo,yhi,682);right=route(755,846,ylo,yhi,801)
ma=np.zeros((1254,1254),dtype='uint8')
for y in range(ylo,yhi):ma[y,left[y-ylo]:right[y-ylo]+1]=255
roof=((oa[:,:,0]>oa[:,:,1]+7)|((oa[:,:,2]<135)&(oa[:,:,1]<140)))
ma[~roof]=0
mask=Image.fromarray(ma);e1=mask.filter(ImageFilter.MinFilter(3));e2=e1.filter(ImageFilter.MinFilter(3));alpha=np.where(np.array(e2)>0,255,np.where(np.array(e1)>0,170,np.where(ma>0,85,0))).astype('uint8')
app=Image.composite(nat,orig,Image.fromarray(alpha));app.save(T/'applied-content-test.png');mask.save(T/'copy-mask-content-test.png');Image.fromarray(alpha).save(T/'alpha-content-test.png');app.crop((595,295,880,1254)).save(T/'applied-content-ROI-native-QA.png')
(T/'content-mask-QA.json').write_text(json.dumps({'mechanicalMaskOnly':True,'sourcePixelsNotEdited':True,'maximumFeatherPixels':2,'leftSearchRange':[635,731],'rightSearchRange':[755,846],'rowRange':[308,1254],'nativeLeftBoundaryMeanAbsDifference':float(np.mean([dif[y,left[y-ylo]] for y in range(ylo,yhi)])),'nativeRightBoundaryMeanAbsDifference':float(np.mean([dif[y,right[y-ylo]] for y in range(ylo,yhi)])),'outsideMaskChangedPixels':int((np.any(np.array(app)!=np.array(orig),axis=2)&(ma==0)).sum()),'leftPath':left.tolist(),'rightPath':right.tolist()},ensure_ascii=False,indent=2),encoding='utf-8')
print(str(T/'applied-content-ROI-native-QA.png'))
