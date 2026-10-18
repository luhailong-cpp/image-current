from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
z=Path(__file__).resolve().parent
info=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
p=z/'qa/r06_c02_wave1_quick_review_20261013.json'
r=dict(reviewedAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='west_continuation',scope='quick layout and edge screen before continuing; not full internal seam acceptance',items=[
dict(stem='r06_c02_s01_01_a01',source=info(z/'native/r06_c02_s01_01_a01.png'),status='PROVISIONAL_layout_edge_compatible',note='Warm gray carved balustrade runs from real north edge; yellow-green flowering shrub at wall; macro and native quality appropriate.'),
dict(stem='r06_c02_s01_02_a01',source=info(z/'native/r06_c02_s01_02_a01.png'),status='REPAIR_inflight_a02',note='Stone coping, single ball post and pavement valid; lower-right pink blossoms have prohibited defocus. a02 local edit requested before propagating that edge.'),
dict(stem='r06_c02_s02_01_a01',source=info(z/'native/r06_c02_s02_01_a01.png'),status='PROVISIONAL_internal_leaf_join_pending',note='Layout and bottom advancing edge appropriate. Existing top strip ends visibly at local y230 in leaf/branch silhouettes; mark internal repair pending, do not count passed. No defect reaches its south advancing edge.')],formalAccepted=False)
with p.open('x',encoding='utf8') as f:json.dump(r,f,indent=2)
s=z/'west-current-selection-20261012.json';d=json.loads(s.read_text());part=next(t for t in d['partialTiles'] if t['tileId']=='r06_c02');part['quickReview']=info(p);part['inflightStems']=['r06_c02_s01_02_a02','r06_c02_s03_01_a01'];part['openIssues']=['s02c01 a01 foliage horizontal contour cut at native local y230; internal repair after assembly.'];s.write_text(json.dumps(d,indent=2));print(info(p))

