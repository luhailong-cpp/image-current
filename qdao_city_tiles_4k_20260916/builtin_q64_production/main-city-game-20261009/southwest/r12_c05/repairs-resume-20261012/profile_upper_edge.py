from pathlib import Path
from PIL import Image
import json,numpy as np
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012/upper-cream-step-local-v02')
out=[]
for fn in ['input.png','native.png']:
 im=Image.open(D/fn).convert('RGB');a=np.asarray(im).astype(float);lum=a.mean(2);hits=[]
 for x in [0,200,400,500,552,600,640,660,680,700,740,780,808,850,900,940,980,1000,1020,1040]:
  yc=744-0.73*x;lo=max(0,int(yc-45));hi=min(1254,int(yc+45));v=lum[lo:hi,x];y=int(v.argmin())+lo
  hits.append({'x':x,'minimumLumY':y,'minimumLum':round(float(lum[y,x]),2),'pixel':a[y,x].astype(int).tolist()})
 im.crop((500,0,1100,450)).save(D/(fn.split('.')[0]+'-edge-native-QA.png'))
 out.append({'file':fn,'profile':hits})
(D/'edge-profile-QA.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))
