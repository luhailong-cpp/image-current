from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012')
src=D/'integrated-local-v10/r12_c05.candidate.context.png';im=Image.open(src).convert('RGB');a=np.asarray(im).astype(float)
out=[]
for x in [2500,2560,2700,3000,3187,3234,3500,3813,4000,4210,4325]:
 ys=np.arange(1600,4050);v=a[ys,x];ok=np.where((v[:,2]-v[:,0]>5)&(v[:,2]>v[:,1]))[0];y=int(ys[ok[0]]) if len(ok) else None
 out.append({'contextX':x,'firstBlueY':y,'pixel':a[y,x].astype(int).tolist() if y else None})
im.crop((4070,1750,4326,2280)).save(D/'blue-east-anchor-native-QA.png')
(D/'blue-edge-anchors-QA.json').write_text(json.dumps({'sourceFile':str(src),'colorEdgeProfiles':out,'note':'Color profile hints only, must visually inspect actual edge.'},indent=2),encoding='utf-8')
print(json.dumps(out))
