from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach/r03_c10')
q=R/'qa'/'full-audit'/'tint-v2'
a=np.array(Image.open(R/'candidate'/'r03_c10-4096-candidate-v1.png').convert('RGB')).astype(np.float32)
b=np.array(Image.open(R/'candidate'/'r03_c10-4096-candidate-v2.png').convert('RGB')).astype(np.float32)
d={}
for name,x1,x2 in [('inside_repaired_center',1950,2146),('right_outside_roi',2286,2675),('right_rest_of_p13',2675,3072),('left_outside_roi',1600,1811)]:
 d[name]={}
 for label,arr in [('before',a),('after',b)]:
  v=arr[1024,x1:x2]-arr[1023,x1:x2]
  n=np.abs(np.diff(arr[1008:1041,x1:x2],axis=0))
  neighbor=np.concatenate([n[:15],n[16:]],axis=0)
  d[name][label]={'xRangeHalfOpen':[x1,x2],'meanAbsRGBJump':float(np.abs(v).mean()),'meanDownMinusUpRGB':v.mean(axis=0).tolist(),'neighborMeanAbsRGBJump':float(neighbor.mean())}
Image.open(R/'candidate'/'r03_c10-4096-candidate-v2.png').crop([2240,832,2784,1216]).save(q/'remaining-horizontal-tint-native.png')
(q/'horizontal-residual-metrics.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d,indent=2))

