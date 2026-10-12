from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012/H3-3-blue-edge-gap-v01')
data=[]
for n in ['input','native']:
 im=Image.open(T/(n+'.png')).convert('RGB');a=np.array(im);rows=[]
 im.crop((570,575,710,700)).save(T/(n+'-gap-native-QA.png'))
 for x in [575,590,605,615,625,635,645,655,665,680,700]:
  c=a[575:720,x];ys=np.mean(c,axis=1);y=int(np.argmin(ys))+575
  rows.append({'x':x,'minLuminanceY':y,'rgb':list(map(int,a[y,x]))})
 data.append({'image':n,'file':str(T/(n+'.png')),'sha256':hashlib.sha256((T/(n+'.png')).read_bytes()).hexdigest(),'profile':rows})
(T/'gap-edge-profile-QA.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(data))
