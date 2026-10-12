from pathlib import Path
from PIL import Image
import numpy as np,json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012/H1-4-grout-gap-v01');out=[]
for n in ['input','native']:
 im=Image.open(T/(n+'.png')).convert('RGB');a=np.array(im);im.crop((590,575,695,680)).save(T/(n+'-ROI-native-QA.png'));rows=[]
 for x in [600,610,615,620,624,627,630,633,636,640,645,650]:
  y=int(168+x*.723);lo=y-10;hi=y+11;c=a[lo:hi,x];t=lo+int(np.argmin(c.mean(axis=1)));rows.append({'x':x,'y':t,'rgb':list(map(int,a[t,x]))})
 out.append({'image':n,'profile':rows})
(T/'gap-edge-profile-QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out))
