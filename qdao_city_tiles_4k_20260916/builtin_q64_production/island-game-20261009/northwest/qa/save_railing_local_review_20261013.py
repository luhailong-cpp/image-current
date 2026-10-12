from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
info=lambda p:dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
items=[]
for stem,mask,status,notes in [
 ('r06_c04_rail_east_foot_a01','v2','local_geometry_pass_independent_review_pending','Triangular paving intrusion under wall closed; coping line continuous; carved post and north115 preserved by mask. Not whole-tile or connected acceptance.'),
 ('r06_c04_rail_middle_body_a01','v1','wall_geometry_pass_paving_boundary_repair_required','Top coping step and both detached front stone beams removed. Main wall/post maintained. Mask lower perimeter contains coarse paving blind ends near native crop (430,1200), (560,1240), (790,1120), and right boundary requires reinspection. Do not accept this combined crop or project as a passed repair.')]:
 raw=Z/'native'/f'{stem}.png';md=Z/'qa'/f'{stem}_mask_{mask}'
 gp=Z/'native'/(f'{stem}.png.generation-evidence-v2.json' if 'east' in stem else f'{stem}.png.generation.json')
 items.append(dict(stem=stem,raw=info(raw),generation=info(gp),mask=info(md/'source_selection_mask.png'),combined=info(md/'combined_native_crop.png'),status=status,notes=notes,review=dict(reviewer='/root/connected_resume',method='Direct complete1254 view_image detail=original',nativeScale100Percent=True)))
p=Z/'qa/railing_local_review_20261013_v1.json'
with p.open('x',encoding='utf-8') as f:json.dump(dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),scope='r06 c03/c04 whole shared railing',status='in_progress',items=items,formalAccepted=False),f,indent=2)
print(json.dumps(info(p)))
