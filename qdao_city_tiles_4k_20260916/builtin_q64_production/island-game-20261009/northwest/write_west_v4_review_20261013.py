import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
z=Path(__file__).resolve().parent
info=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
q=z/'qa/r05_c02_v4_internal_review/qa_index.json';d=json.loads(q.read_text())
prior=z/'qa/r05_c02_v1_owner_native33_review_20261013.json';old={Path(i['path']).name:i for i in json.loads(prior.read_text())['items']}
out=[]
for i in d['seamAndJunctionCrops']:
 n=Path(i['path']).name;p=old[n];same=i['sha256']==p['sha256']
 if same: status=p['status'];note=p['note']
 elif n=='top-bottom_r03-r04_x1024-2048_100pct.png':status='REPAIR';note='Small central foot cloud-moulding edge step at local x455,y355; southwest ground join repair submitted.'
 else:status='PASS';note='Viewed complete native crop: medallion rims, cauldron underside, foot and paving joins continuous; no structural seam remains in this crop.'
 out.append({**i,'status':status,'note':note,'method':'exact-hash previous review reuse' if same else 'view_image original full crop','viewedNative100Percent':not same,'reuseFrom':info(prior) if same else None})
result=dict(schemaVersion=1,reviewedAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='west_continuation',tileId='r05_c02',candidate=info(z/'tiles/r05_c02_candidate-v4_4096.png'),record=info(z/'tiles/r05_c02_candidate-v4_4096.native-repair.json'),qaIndex=info(q),status='native33_reviewed_three_crops_pending_one_local_repair',passed=sum(i['status']=='PASS' for i in out),repair=sum(i['status']=='REPAIR' for i in out),internalClosurePassed=False,formalAccepted=False,items=out)
p=z/'qa/r05_c02_v4_owner_native33_review_20261013.json'
with p.open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps({'review':info(p),'pass':result['passed'],'repair':result['repair']}))

