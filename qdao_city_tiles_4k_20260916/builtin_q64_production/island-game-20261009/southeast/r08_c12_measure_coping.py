from PIL import Image
from pathlib import Path
import numpy as np,os
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
R=Path(__file__).resolve().parent
for f in ['guides/r08_c12_repair_coping_v04.native-context.png','native/r08_c12_repair_coping_v04.png','native/r08_c12_repair_coping_long_left_v01.png']:
 v=np.asarray(Image.open(R/f).convert('RGB')).astype(int); out=[]
 for x in [0,200,627,1000,1139,1253]:
  for y in range(150,900):
   p=v[y:y+50,x]
   if np.all((p[:,0]>180)&(p[:,2]>150)&((p[:,0]-p[:,2])<70)):
    out.append([x,y]);break
 print(f,out)

