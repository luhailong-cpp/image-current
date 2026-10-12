import sys,json,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
import assemble_tile as a
p=Z/'tiles/r05_c03_candidate-v8_4096.png';old=Image.open(Z/'tiles/r05_c03_candidate-v1_4096.png').convert('RGB');im=Image.open(p).convert('RGB')
out=Z/'qa/r05_c03_v8_internal_closure';out.mkdir(exist_ok=False)
qa=a.save_qa(out,im);(out/'qa_index.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
changed=[];unchanged=[]
for e in qa['seamAndJunctionCrops']:
 box=e['tileCropBoxHalfOpen'];name=Path(e['path']).name
 (unchanged if np.array_equal(np.asarray(old.crop(box)),np.asarray(im.crop(box))) else changed).append(name)
ar=np.array(im);o=np.array(old)
edge={k:bool(np.array_equal(x,y)) for k,x,y in [('north',ar[:115],o[:115]),('south',ar[-115:],o[-115:]),('west',ar[:,:115],o[:,:115]),('east',ar[:,-115:],o[:,-115:])]}
extra={
 'stair_mid_baseline_100pct.png':[1260,2840,1790,3370],
 'stair_left_rightcrop_boundary_100pct.png':[1620,2860,2110,3340],
 'door_repair_boundary_100pct.png':[850,920,1480,1540],
 'window_repair_boundary_100pct.png':[2830,100,3300,520],
 'paving_final_tip_100pct.png':[2770,3080,3270,3530]}
for n,b in extra.items(): im.crop(b).save(out/n)
review={'tileId':'r05_c03','candidate':{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},'priorVersionAll33Reviewed':True,'changedStandardCrops':changed,'unchangedStandardCrops':unchanged,'outer115PixelBandsUnchanged':edge,'extraReviewCrops':extra,'status':'pending_changed_and_repair_boundary_visual_review','formalAccepted':False}
(out/'review_pending.json').write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
print(json.dumps(review))
