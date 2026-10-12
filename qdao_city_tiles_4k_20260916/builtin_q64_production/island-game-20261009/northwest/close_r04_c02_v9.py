from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;Q=Z/'qa/r04_c02_v9_internal_review'
def info(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
root=Z/'qa/r04_c02_v9_independent_root_21_review_20261012.json'
peer=Z/'qa/r04_c02_v9_independent_connected_12_review_20261012.json'
assert info(root)['sha256']=='ecd7dcbd80294e39cbda846b0bc3d913b7f62e670a1b567c1e1b95ce5c259ec3'
assert info(peer)['sha256']=='a3d8eab56929661945e78f29ddbb486cd39b4df22a97f4b0cf0cc7295ee70831'
owner=read(Q/'owner-review.json');items=read(root)['items']+read(peer)['items']
assert len(items)==33 and {x['sha256'] for x in items}=={x['sha256'] for x in owner['standardCrops']}
for x in items:assert info(Path(x['path']))['sha256']==x['sha256']
owner.update({'closedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'internal_native_closure_PASS_external_seams_pending','independentReview':[info(root),info(peer)],'independentReviewedCropCount':33,'internalClosurePassed':True,'ownerReviewRecord':info(Q/'owner-review.json'),'externalSeamsReviewed':False,'formalAccepted':False,'formalAcceptedCount':0})
p=Q/'review.json';assert not p.exists();p.write_text(json.dumps(owner,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
s=Z/'west-current-selection-20261012.json';d=read(s)
current=d['currentTile'];current.update({'internalClosurePassed':True,'internalReview':info(p),'status':'internal_33_independent_and_owner_PASS_strict_replay_PASS_external_pending','formalAccepted':False})
if not any(x['tileId']=='r04_c02' for x in d['completedTiles']):d['completedTiles'].append(dict(current))
d['partialTiles'][0].update({'selectedNativeStems':['r05_c02_s01_01_a02','r05_c02_s01_02_a02','r05_c02_s02_01_a02'],'inflightStems':['r05_c02_s01_03_a01','r05_c02_s02_02_a01','r05_c02_s03_01_a01'],'status':'3of16_native_cauldron_region_continuing','openIssues':['r04c02/r05c02 north external flower cutoff near west end in minerror pair; final cross-tile QA/repair pending']})
d['partialTiles'][0].pop('inflightStem',None)
s.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
print(json.dumps({'review':info(p),'selection':info(s)}))

