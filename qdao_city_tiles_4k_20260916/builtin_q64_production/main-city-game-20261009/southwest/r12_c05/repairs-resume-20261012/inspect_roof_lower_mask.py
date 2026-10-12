from pathlib import Path
from PIL import Image
import numpy as np,json
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest/r12_c05/repairs-resume-20261012/roof-color-east-cap-v01');a=np.array(Image.open(T/'input.png'));m=np.array(Image.open(T/'copy-mask.png'));rows=[]
for x in [640,680,710,742,780,820,840]:
 rows.append({'x':x,'floorTransitionY':next((y for y in range(900,1254) if int(a[y,x,0])-int(a[y,x,1])<35 and a[y,x,1]>140),None),'pixels':[{'y':y,'rgb':list(map(int,a[y,x])),'mask':int(m[y,x])} for y in [1000,1050,1100,1150,1200,1250]]})
print(json.dumps(rows));Image.open(T/'applied-content-test.png').crop((595,970,880,1254)).save(T/'lower-mask-native-QA.png')
