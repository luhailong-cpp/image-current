from pathlib import Path
from PIL import Image
import json,hashlib
import assemble_tile
Z=Path(__file__).resolve().parent
q=Z/'qa/r03_c02_v5_internal_closure';q.mkdir(exist_ok=True)
p=Z/'tiles/r03_c02_candidate-v5_4096.png'
im=Image.open(p).convert('RGB')
rec=assemble_tile.save_qa(q,im)
for stem,box in [('guard_repair',[1450,550,2704,1804]),('blade_repair',[1450,1450,2704,2704]),('paving_final',[400,2080,1654,3334]),('paving_boundary_final',[640,2300,1894,3554])]:
 im.crop(box).save(q/(stem+'_100pct.png'))
(q/'qa_index.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf8')
print(json.dumps({'cropCount':len(rec['seamAndJunctionCrops']),'qaDir':str(q)}))
