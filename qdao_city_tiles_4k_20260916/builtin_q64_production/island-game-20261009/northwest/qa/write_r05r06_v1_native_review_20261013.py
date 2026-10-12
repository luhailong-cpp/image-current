from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
B=Z/'tiles/connected-r05-r06-cross-v1'
info=lambda p:dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
c=json.loads((B/'connected-cluster.json').read_text(encoding='utf8'))
faults={
 'shared_vertical_y4096-5120_100pct.png':'Railing top cap changes elevation near local x160,y910; left cap segment is blurred. Native boundary repair required.',
 'shared_vertical_y5120-6144_100pct.png':'Railing panel and duplicated detached lower beams stair-step across c03/c04; consolidate with the already fixed solid wall to the east.',
 'shared_horizontal_x5120-6144_100pct.png':'Diagonal paving grout is cut at local y240, with endpoints near x160 and x304; join continuity requires native repair.'
}
items=[]
for q in c['qa']['nativeScaleCrops']:
 p=Path(q['output']['path']);bad=faults.get(p.name)
 items.append(dict(image=info(p),box=q['box'],axis=q['axis'],nativeVisualReviewed=True,geometry='repair_required' if bad else 'pass',note=bad or 'Viewed full native crop; visible coarse contours and object boundaries continuous.'))
checks=[]
for tid,old in [('r06_c03',Z/'tiles/r06_c03_candidate-v7_4096.png'),('r06_c04',Z/'tiles/r06_c04_rail-east-mid-v1_4096.png')]:
 new=B/f'{tid}_connected_4096.png'
 a=np.array(Image.open(old).convert('RGB'));b=np.array(Image.open(new).convert('RGB'))
 checks.append(dict(tileId=tid,base=info(old),current=info(new),south115Unchanged=bool(np.array_equal(a[-115:],b[-115:])),changedPixelsInSouth115=int(np.any(a[-115:]!=b[-115:],axis=2).sum())))
out=Z/'qa/r05r06_v1_native17_connected_continuation_review_20261013.json'
with out.open('x',encoding='utf8') as f:json.dump(dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='connected_continuation',cluster=info(B/'connected-cluster.json'),status='14_of_17_geometry_pass_3_repair_required_material_pending',nativeViewed=17,geometryPassed=14,geometryRepairRequired=3,materialPending='Small regular cells / checker texture remain inside several large paving slabs. Local geometry passes do not resolve this material issue.',items=items,anchorChecks=checks,formalAccepted=False),f,indent=2)
print(json.dumps(dict(review=info(out),anchorChecks=checks)))
