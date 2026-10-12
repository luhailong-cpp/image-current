from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012/V1-row1-quiet-edge-v02');orig=Image.open(T/'input.png').convert('RGB');nat=Image.open(T/'native.png').convert('RGB');oa=np.array(orig).astype(float);na=np.array(nat).astype(float);dif=np.abs(oa-na).mean(axis=2)
def route(cost,coords,center):
 h,w=cost.shape;cost=cost+.0004*(coords-center)**2;dp=cost[0].copy();back=np.zeros((h,w),dtype='int16')
 for i in range(1,h):
  best=np.full(w,np.inf)
  for step in [-2,-1,0,1,2]:
   idx=np.clip(np.arange(w)+step,0,w-1);v=dp[idx]+.25*abs(step);ok=v<best;best[ok]=v[ok];back[i,ok]=idx[ok]
  dp=best+cost[i]
 out=np.zeros(h,dtype=int);out[-1]=int(dp.argmin())
 for i in range(h-1,0,-1):out[i-1]=back[i,out[i]]
 return out+coords[0]
left=route(dif[325:676,635:681],np.arange(635,681),653);right=route(dif[325:676,1095:1141],np.arange(1095,1141),1120)
top=route(dif[325:396,635:1141].T,np.arange(325,396),350);bottom=route(dif[595:676,635:1141].T,np.arange(595,676),647)
ma=np.zeros((1254,1254),dtype='uint8')
for y in range(325,676):
 for x in range(635,1141):
  if left[y-325]<=x<=right[y-325] and top[x-635]<=y<=bottom[x-635]:ma[y,x]=255
mask=Image.fromarray(ma);e1=mask.filter(ImageFilter.MinFilter(3));e2=e1.filter(ImageFilter.MinFilter(3));alpha=np.where(np.array(e2)>0,255,np.where(np.array(e1)>0,170,np.where(ma>0,85,0))).astype('uint8');app=Image.composite(nat,orig,Image.fromarray(alpha));app.save(T/'applied-content-test-crop.png');mask.save(T/'copy-mask-content-test.png');Image.fromarray(alpha).save(T/'alpha-content-test.png');app.crop((610,285,1170,715)).save(T/'applied-content-test-ROI-native-QA.png')
ch=np.any(np.array(app)!=np.array(orig),axis=2);audit={'scopeBoundedToPromptROI':[635,325,1140,675],'mechanicalCopySelectionOnly':True,'maximumFeatherPixels':2,'sourceResampling':False,'outsideMaskChangedPixels':int((ch&(ma==0)).sum()),'changedPixels':int(ch.sum()),'pathRanges':{'left':[635,680],'right':[1095,1140],'top':[325,395],'bottom':[595,675]},'paths':{'left':left.tolist(),'right':right.tolist(),'top':top.tolist(),'bottom':bottom.tolist()}}
(T/'content-mask-test-QA.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in audit.items() if k!='paths'}))
