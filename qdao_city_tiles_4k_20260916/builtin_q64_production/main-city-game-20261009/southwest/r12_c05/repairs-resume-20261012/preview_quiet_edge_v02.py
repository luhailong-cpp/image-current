from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012/V1-row1-quiet-edge-v02');orig=Image.open(T/'input.png').convert('RGB');nat=Image.open(T/'native.png').convert('RGB');oa=np.array(orig).astype(float);na=np.array(nat).astype(float);dif=np.abs(oa-na).mean(axis=2)
poly=[(645,325),(705,325),(710,425),(980,470),(1140,575),(1140,655),(950,555),(650,490)]
mask=Image.new('L',orig.size,0);ImageDraw.Draw(mask).polygon(poly,fill=255);ma=np.array(mask);e1=mask.filter(ImageFilter.MinFilter(3));e2=e1.filter(ImageFilter.MinFilter(3));alpha=np.where(np.array(e2)>0,255,np.where(np.array(e1)>0,170,np.where(ma>0,85,0))).astype('uint8');app=Image.composite(nat,orig,Image.fromarray(alpha));app.save(T/'applied-test-crop.png');mask.save(T/'copy-mask-test.png');Image.fromarray(alpha).save(T/'alpha-test.png')
for n,im in [('original',orig),('native',nat),('applied-test',app)]:im.crop((610,285,1170,715)).save(T/(n+'-ROI-native-QA.png'))
change=np.any(np.array(app)!=np.array(orig),axis=2);print(json.dumps({'outsideMask':int((change&(ma==0)).sum()),'changedPixels':int(change.sum()),'meanOriginalNativeAbsDiffInside':float(dif[ma>0].mean())}))
