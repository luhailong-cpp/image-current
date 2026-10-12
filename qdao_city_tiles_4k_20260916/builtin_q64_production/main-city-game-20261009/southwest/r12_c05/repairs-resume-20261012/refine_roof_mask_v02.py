from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012/roof-color-east-cap-v01')
orig=Image.open(T/'input.png').convert('RGB');nat=Image.open(T/'native.png').convert('RGB');oa=np.array(orig).astype('int16');ma=np.array(Image.open(T/'copy-mask.png')).copy()
# Below the teal molding only the red roof remains; original warm floor/shadow is excluded.
# This narrows a mechanical copy mask, without altering any source/native pixel colors.
floor=np.zeros((1254,1254),bool);floor[900:,:]=(oa[900:,:,0]-oa[900:,:,1])<60
removed=int(((ma>0)&floor).sum());ma[floor]=0
mask=Image.fromarray(ma);e1=mask.filter(ImageFilter.MinFilter(3));e2=e1.filter(ImageFilter.MinFilter(3));alpha=np.where(np.array(e2)>0,255,np.where(np.array(e1)>0,170,np.where(ma>0,85,0))).astype('uint8')
app=Image.composite(nat,orig,Image.fromarray(alpha));app.save(T/'applied-crop-v02.png');mask.save(T/'copy-mask-v02.png');Image.fromarray(alpha).save(T/'alpha-v02.png')
app.crop((595,295,880,1254)).save(T/'applied-content-ROI-native-v02-QA.png')
change=np.any(np.array(app)!=np.array(orig),axis=2);assert int((change&(ma==0)).sum())==0;assert int((change&floor).sum())==0
(T/'mask-refinement-v02-QA.json').write_text(json.dumps({'sourceCopyMask':{'file':str(T/'copy-mask.png'),'sha256':hashlib.sha256((T/'copy-mask.png').read_bytes()).hexdigest()},'originalFloorExcluded':True,'excludedFloorPixels':removed,'floorChangedPixels':int((change&floor).sum()),'outsideMaskChangedPixels':int((change&(ma==0)).sum()),'maximumFeatherPixels':2,'sourceResampling':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'excludedFloorPixels':removed,'changedPixels':int(change.sum()),'floorChangedPixels':int((change&floor).sum())}))
