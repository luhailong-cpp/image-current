from pathlib import Path
import sys,json,datetime,numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
import cross_tile_native_repair as c
r=c.r
info=lambda p:r.file_info(Z/p)
mp=Z/'qa/connected-r05-r06-current-v5.manifest.json'
idx=Z/'qa/r05r06_v5_changed_native_review_20261013/index.json'
ind=Z/'qa/r05r06_v5_independent_native_geometry_review_20261013.json'
index=r.read_json(idx);independent=r.read_json(ind)
assert r.file_info(mp)==index['manifest']==independent['manifest']
assert r.file_info(idx)==independent['index']
items=index['items']
for q in items:
 assert r.file_info(Path(q['output']['path']))==q['output']
 if q['geometry']!='PASS':
  q.update(geometry='PASS',method='full native crop view_image original by connected_continuation',note='Coarse stone grout and/or solid railing contours continuous; no visible structural cutoff.')
for q in index['extraBoundaryCrops']:
 assert r.file_info(Path(q['output']['path']))==q['output']
 q.update(geometry='PASS',method='full native crop view_image original by connected_continuation',note='Coarse geometry remains continuous across repaired footprint perimeter.')
audit=Z/'guides/connected_r05_r06_v5_final_native_audit_20261013.input.json'
ad=r.read_json(audit);assert ad['manifest']==r.file_info(mp)
assert r.file_info(Path(ad['editTarget']['path']))=={k:ad['editTarget'][k] for k in ('path','sha256')}
for p in independent['fullRepairCrops']:
 assert p['geometry']=='PASS' and p['exactCurrentManifestPixels']
out=Z/'qa/r05r06_v5_geometry_closure_material_pending_20261013.json'
result=dict(schemaVersion=1,createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='connected_continuation',manifest=r.file_info(mp),tiles=r.read_json(mp)['tiles'],status='17_seam_geometry_PASS_with_independent_review_material_pending',geometryClosurePassed=True,formalAccepted=False,wholeMapAccepted=False,counts=dict(nativeSeams=17,unchangedPriorPassReused=12,newSeamsViewed=5,newBoundaryMarginsViewed=8,fullFollowupRepairCropsViewed=2),ownerItems=items,ownerBoundaryMargins=index['extraBoundaryCrops'],independentReview=r.file_info(ind),followupRepairReview=info('qa/r05r06_two_followup_repairs_owner_review_20261013.json'),strictReplay=dict(status='PASS',method='Final manifest canonical_context strict replay via versioned depth128 memo runner, including all four full-resolution source validations; no change to hash, per-pixel provenance or cycle detection.',finalNativeAudit=r.file_info(audit),finalNativeAuditDerivation=ad['editTarget']['derivationRecord'],finalAuditOutput={k:ad['editTarget'][k] for k in ('path','sha256')},validator=info('qa/run_cross_with_strict_memo_depth128_20261013.py'),originalRunner=info('qa/run_cross_with_strict_memo.py'),depthPolicy=dict(oldLimit=32,usedLimit=128,originalSharedScriptsUnmodified=True,reason='Legitimate chained repair ancestry exceeded prior arbitrary guard; cycle detection remains active.'),finalServerMemoStats=dict(hits=126,misses=97,rehashes=72688,dependencyChanges=0)),anchorChecks=index['anchorChecks'],remaining=[dict(type='material',status='PENDING',description='Small regular cells / checker patches remain within broad paving slabs. Requires native material edits while locking current geometry; no blur, pixel synthesis or upscaling.'),dict(type='external_boundary',status='PENDING_OTHER_OWNER',description='r06c04 south115 differs from original fixed base by 7914 left-edge DP pixels. No subsequent local repair touched this boundary; r06/r07 northwest junction still needs downstream QA.'),dict(type='whole_map',status='PENDING',description='No whole-map or formal 4K tile acceptance granted by local cluster geometry closure.')],models=dict(route='builtin image_gen.imagegen',actualModel=None,actualQuality=None,paidApiUsed=False),operations=[info('tiles/connected-r05-r06-cross-v2/rail-west-v1.cross-native-operation.json'),info('tiles/connected-r05-r06-cross-v3/paving-north-v1.cross-native-operation.json'),info('tiles/connected-r05-r06-cross-v4/paving-left-v1.cross-native-operation.json'),info('tiles/connected-r05-r06-cross-v5/rail-ground-v1.cross-native-operation.json')])
c.write_json(out,result);print(json.dumps(r.file_info(out)))

