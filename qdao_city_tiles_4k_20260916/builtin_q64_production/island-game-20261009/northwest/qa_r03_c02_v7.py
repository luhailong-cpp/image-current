from pathlib import Path
from PIL import Image
import numpy as np,json
import assemble_tile
Z=Path(__file__).resolve().parent
q=Z/'qa/r03_c02_v7_internal_closure';q.mkdir(exist_ok=False)
im=Image.open(Z/'tiles/r03_c02_candidate-v7_4096.png').convert('RGB')
rec=assemble_tile.save_qa(q,im)
for name,box in [('upper_and_mid_paving',[450,1540,1704,2794]),('paving_boundary',[640,2300,1894,3554])]:im.crop(box).save(q/(name+'_100pct.png'))
v5=Z/'qa/r03_c02_v5_internal_closure'
changed=[];unchanged=[]
for e in rec['seamAndJunctionCrops']:
 p=Path(e['path']);a=np.array(Image.open(p));b=np.array(Image.open(v5/p.name))
 (unchanged if np.array_equal(a,b) else changed).append(p.name)
(q/'qa_index.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf8')
(q/'delta_from_v5.json').write_text(json.dumps({'changed':changed,'unchanged':unchanged},indent=2)+'\n',encoding='utf8')
print(json.dumps({'changed':changed,'unchangedCount':len(unchanged)}))
