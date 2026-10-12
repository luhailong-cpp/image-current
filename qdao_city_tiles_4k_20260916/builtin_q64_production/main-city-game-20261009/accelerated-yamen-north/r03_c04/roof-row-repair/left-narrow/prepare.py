from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;P=O.parent;T=P.parent
BFILE=T/'candidate/r03_c04-pipeline-minimum-error-5a45bea8726a-ccd4a3.png'
B=np.array(Image.open(BFILE).convert('RGB'));C=B[493:1747,453:1707].copy()
R=np.array(Image.open(P/'right/derived-context.png').convert('RGB'));S=np.array(Image.open(P/'right/support-positive-mask.png'))>0
C[:,980:1254]=np.where(S[:,:274,None],R[:,:274],C[:,980:1254])
Image.fromarray(C).save(O/'stage0-native.png')
rois=[{'id':1,'roiBox':[130,515,490,725]}, {'id':2,'roiBox':[450,515,825,725]}, {'id':3,'roiBox':[785,515,1095,725]}]
for item in rois:
 item['contextTileBox']=[453,493,1707,1747];item['contextWorldBox']=[12741,8685,13995,9939]
 item['roiTileBox']=[item['roiBox'][0]+453,item['roiBox'][1]+493,item['roiBox'][2]+453,item['roiBox'][3]+493]
 item['roiWorldBox']=[item['roiTileBox'][0]+12288,item['roiTileBox'][1]+8192,item['roiTileBox'][2]+12288,item['roiTileBox'][3]+8192]
data={'baseFile':str(BFILE),'baseSha256':hashlib.sha256(BFILE.read_bytes()).hexdigest(),
 'contextTileBox':[453,493,1707,1747],'contextWorldBox':[12741,8685,13995,9939],
 'stage0RightPatch':str(P/'right/manifest.json'),'mergeOrder':'root right accepted repair first, then accepted narrow repairs in id order',
 'rois':rois}
(O/'preparation.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
A=np.concatenate([C,np.full((1254,1254,1),255,dtype=np.uint8)],axis=2);x0,y0,x1,y1=rois[0]['roiBox'];A[y0:y1,x0:x1]=0
Image.fromarray(A).save(O/'roi1-mask-guide.png')
print(json.dumps(data))
