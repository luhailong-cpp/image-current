from pathlib import Path
from PIL import Image
import json,numpy as np,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012')
R=D/'blue-coherent-left-v04';out=[]
for fn in ['input.png','native.png']:
 a=np.asarray(Image.open(R/fn).convert('RGB')).astype(float);p=[]
 for x in [0,200,400,600,800,1000,1253]:
  ys=np.arange(0,1254);v=a[ys,x];ok=np.where((v[:,2]-v[:,0]>5)&(v[:,2]>v[:,1]))[0]
  p.append({'x':x,'firstBlueY':int(ok[0]) if len(ok) else None,'desiredThinEdgeY':1080-1250/1765*x})
 out.append({'file':fn,'hints':p})
(R/'blue-edge-profile-QA.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))
T=D/'blue-direct-control-left-v05';T.mkdir(exist_ok=True)
Image.open(R/'QA-common-line-overlay-not-final.png').save(T/'input.png');Image.open(R/'input.png').save(T/'clean-original-support.png')
(T/'input-derivation.json').write_text(json.dumps({'controlTargetFile':str(R/'QA-common-line-overlay-not-final.png'),'cleanOriginalFile':str(R/'input.png'),'sourceCropContextBox':[2560,2160,3814,3414],'lineContextAnchors':[[2560,3240],[4325,1990]],'guidePixelsNeverCopiedToFinal':True,'noFinalPixelsPaintedByCode':True},indent=2),encoding='utf-8')
