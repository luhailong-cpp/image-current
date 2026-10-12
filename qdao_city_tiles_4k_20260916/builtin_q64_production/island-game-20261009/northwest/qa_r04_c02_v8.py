from pathlib import Path
from PIL import Image
import json,hashlib
import assemble_tile
Z=Path(__file__).resolve().parent
q=Z/'qa/r04_c02_v8_internal_review';q.mkdir(exist_ok=False)
im=Image.open(Z/'tiles/r04_c02_candidate-v8_4096.png').convert('RGB')
rec=assemble_tile.save_qa(q,im)
for name,box in [('eastupper_lower_boundary',[3700,1050,4096,1500]),('eastroof_lower_boundary',[3700,3150,4096,3530]),('wallscroll_upper_boundary',[2900,680,3530,1100]),('full_east_mid',[3700,1200,4096,2400]),('north_paving_tip',[2850,0,3350,520])]:
 im.crop(box).save(q/(name+'_100pct.png'))
(q/'qa_index.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf8')
def f(p):return dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
sel=dict(schemaVersion=1,owner='west_closure',currentTile=dict(tileId='r04_c02',candidate=f(Z/'tiles/r04_c02_candidate-v8_4096.png'),record=f(Z/'tiles/r04_c02_candidate-v8_4096.native-repair.json'),internalClosurePassed=False,qaIndex=f(q/'qa_index.json'),status='all16_native_and7_repairs_merged_pending_full33_and_boundary_review'),completedTiles=[dict(tileId='r03_c02',candidate=f(Z/'tiles/r03_c02_candidate-v7_4096.png'),record=f(Z/'tiles/r03_c02_candidate-v7_4096.native-repair.json'),internalClosurePassed=True,formalAccepted=False)],partialTiles=[dict(tileId='r05_c02',selectedNativeStems=[],status='not_started_waiting_final_r04c02_south'),dict(tileId='r06_c02',selectedNativeStems=[],status='not_started')],historicalFreezeUnchanged=True,progressModified=False,formalAcceptedCount=0)
(Z/'west-current-selection-20261012.json').write_text(json.dumps(sel,indent=2)+'\n',encoding='utf8')
print(json.dumps(sel))

