from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012');T=D/'roof-color-east-cap-v01';orig=Image.open(T/'input.png').convert('RGB');native=Image.open(T/'native.png').convert('RGB');assert orig.size==native.size==(1254,1254)
mask=Image.new('L',orig.size,0);ImageDraw.Draw(mask).rectangle((660,345,822,1018),fill=255)
e1=mask.filter(ImageFilter.MinFilter(3));e2=e1.filter(ImageFilter.MinFilter(3));ma=np.array(mask);alpha=np.where(np.array(e2)>0,255,np.where(np.array(e1)>0,170,np.where(ma>0,85,0))).astype('uint8')
app=Image.composite(native,orig,Image.fromarray(alpha));app.save(T/'applied-test-crop.png');mask.save(T/'copy-mask-test.png');Image.fromarray(alpha).save(T/'alpha-test.png')
for n,im in [('original',orig),('native',native),('applied-test',app)]:im.crop((600,315,875,1070)).save(T/(n+'-ROI-native-QA.png'))
oa=np.array(orig).astype(float);na=np.array(native).astype(float);profiles=[]
for y in [400,450,500,575,650,700,800,900,1000]:
 row=[]
 for x in [659,660,665,700,738,741,742,743,747,780,815,822,823]:
  row.append({'x':x,'originalRGB':list(map(int,oa[y,x])),'nativeRGB':list(map(int,na[y,x]))})
 profiles.append({'y':y,'pixels':row})
(T/'tone-profile-QA.json').write_text(json.dumps(profiles,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'maskOutsideChangedPixels':int((np.any(np.array(app)!=np.array(orig),axis=2)&(ma==0)).sum()),'nativeOriginalMeanAbsDifferenceLeft':float(np.abs(na[345:1019,660]-oa[345:1019,660]).mean()),'nativeOriginalMeanAbsDifferenceRight':float(np.abs(na[345:1019,822]-oa[345:1019,822]).mean())}))
