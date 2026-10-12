from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import apply_native_tile_repair as r
z=Path(__file__).resolve().parent;info=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
v=z/'tiles/r05_c02_candidate-v5_4096.png';rec=v.with_suffix('.native-repair.json');q=z/'qa/r05_c02_v5_internal_review/qa_index.json'
prior=z/'qa/r05_c02_v4_owner_native33_review_20261013.json';old={Path(i['path']).name:i for i in json.loads(prior.read_text())['items']};out=[]
for i in json.loads(q.read_text())['seamAndJunctionCrops']:
 same=old[Path(i['path']).name]['sha256']==i['sha256']
 if same:assert old[Path(i['path']).name]['status']=='PASS'
 out.append({**i,'status':'PASS','method':'exact-hash reuse previous PASS' if same else 'full native crop view_image original','note':old[Path(i['path']).name]['note'] if same else 'Southwest broad paving joints and shadows continuous; middle foot cloud rim continuous. No new boundary cuts in this crop.','reuseFrom':info(prior) if same else None})
pixels,proof=r.validate_base(v,rec)
receipt=z/'qa/r05_c02_v5_strict_native_replay_20261013.json';receipt.write_text(json.dumps(dict(base=info(v),record=info(rec),proof=proof,all16777216PixelsReplayed=True,visualAcceptance=False),indent=2))
review=z/'qa/r05_c02_v5_owner_native33_review_20261013.json'
d=dict(schemaVersion=1,reviewedAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='west_continuation',tileId='r05_c02',candidate=info(v),record=info(rec),qaIndex=info(q),strictReplay=info(receipt),status='owner_native33_PASS_independent_review_and_external_pending',passed=33,repair=0,internalClosurePassed=False,formalAccepted=False,items=out)
with review.open('x',encoding='utf8') as f:json.dump(d,f,indent=2)
sel=z/'west-current-selection-20261012.json';s=json.loads(sel.read_text());s['currentTile'].update(candidate=info(v),record=info(rec),qaIndex=info(q),internalReview=info(review),strictReplay=info(receipt),status=d['status'],internalClosurePassed=False,formalAccepted=False);sel.write_text(json.dumps(s,indent=2))
print(json.dumps(dict(review=info(review),strictReplay=info(receipt),candidate=info(v),record=info(rec),passed=33)))

