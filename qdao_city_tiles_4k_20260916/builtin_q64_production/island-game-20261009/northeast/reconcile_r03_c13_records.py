"""Reconcile only r03_c13 evidence and QA state after finished generation; no image edits."""
from native_work import *
for p in (ZONE/'native').glob('r03_c13*.png.generation.json'):
 r=read(p)
 for ref in r['references']:
  rp=Path(ref['file']);gp=rp.with_suffix('.png.generation.json');dp=rp.with_suffix('.png.derivation.json')
  if gp.exists(): ref['generationRecord']=gp.as_posix()
  if dp.exists(): ref['derivationRecord']=dp.as_posix()
  ref['currentlyAvailableAtAudit']=rp.exists()
  if rp.exists(): assert sha(rp)==ref['sha256'],f'Reference changed {rp}'
 receipt=Path(r['evidence']['receipt']);rr=read(receipt);rr['prompt']=r['prompt'];rr['promptSha256']=sha(r['prompt']);write(receipt,rr)
 for old,new in [('r03_c13_p02_02','r03_c13_p02_02_v2'),('r03_c13_p03_02','r03_c13_p03_02_v2'),('r03_c13_p04_02','r03_c13_p04_02_v3'),('r03_c13_p04_02_v2','r03_c13_p04_02_v3'),('r03_c13_p04_03','r03_c13_p04_03_v2')]:
  if r['id']==old:r.update(status='rejected_superseded_by_repair',supersededBy=new)
 if r['id']=='r03_c13_p04_03_v2':r.update(status='candidate_requires_joint_repair',internalSeams='top/right pass, left stone terrace edge height discontinuity; cannot accept until full joint redraw')
 write(p,r)
 inp=ZONE/'prompts'/f"{r['id']}.inputs.json"
 if inp.exists():write(inp,r['references'])
bad='r03_c13_p04_02_v3__r03_c13_p04_03_v2'
p=ZONE/'qa'/f'{bad}.json';r=read(p);r.update(status='failed_geometry',reviewedAtUtc=now(),geometryChecks={'terraceFrontEdge':'fails; upper/front edge shifts up approx150 pixels at core boundary'},nextAction='After capacity gate release, native redraw spanning entire interrupted terrace edge with all attachment borders; no further same small one-sided patch repair');write(p,r)
p=ZONE/'tiles'/'r03_c13.png.derivation.json';r=read(p);r.update(status='complete_native_coverage_geometry_repair_required',internalReview='failed lower terrace edge discontinuity',formalAccepted=False,unresolvedGeometry=[{'id':'terrace-front-edge','tilePixelBox':[1850,3450,2550,4096],'evidence':(ZONE/'qa'/f'{bad}.join-100pct.png').as_posix(),'severity':'requires native joint redraw'}]);write(p,r)
write(ZONE/'qa'/'r03_c13-root-review.json',{'tileId':'r03_c13','sha256':r['sha256'],'status':'internal_geometry_not_passed','knownIssues':r['unresolvedGeometry'],'formalAccepted':False,'capacity5000Validated':False,'lastGeneratedNative':'r03_c13_p04_03_v2','newImageRequestsHeld':True,'reviewedAtUtc':now()})
print('r03_c13 records reconciled; unresolved terrace geometry retained as failure.')

