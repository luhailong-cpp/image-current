import tile_native_workflow as w
from pathlib import Path
T=w.ZONE/'r12_c10';M=w.read(T/'processed/weststairs-v2-preview/manifest.json');p=T/'selected-patches.json';sel=w.read(p);backup=T/'selected-before-weststairs-v2.json'
assert not backup.exists();w.write(backup,sel)
for r in M['outputs']:
 assert w.sha(T/sel['patches'][r['patch']])==r['baseSha256']
 sel['patches'][r['patch']]=Path(r['file']).relative_to(T).as_posix()
sel['updatedAt']=w.now();sel['status']='native_production_and_internal_QA';w.write(p,sel)
w.write(T/'qa/weststairs-v2-preview/owner-review.json',{'createdAt':w.now(),'status':'owner_geometry_review_pass_candidate_adopted_independent_pending','evidence':w.read(T/'qa/weststairs-v2-preview/manifest.json'),'checks':['left adoption through full pillar/stair ends','top landing/tread line','right adoption through all3 risers','bottom-left wood planks after c09 p34 core115 adoption','actual core shared edge through all3 stairs'],'findings':'No remaining geometric discontinuity seen in native strips; minor material color difference reserved for bounded RGB field; p31 not generated, full south interface pending.','beforeSelection':str(backup),'afterSelectionSha256':w.sha(p),'formalAccepted':False})
print('Adopted owned provisional geometry, 6 selected; formal false')
