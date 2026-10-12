from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]; now=datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sel=read(Z/'selection-r04_c13.json');der=read(Z/'tiles/r04_c13.png.derivation.json'); audit=read(Z/'qa/r04_c13-final-audit.json')
assert sha(der['file'])==der['sha256']==audit['sha256'] and audit['rebuiltPixelExact'] and audit['allOverlaySourcesPass']
inspected=[]
for direction in ['vertical','horizontal']:
 for i in range(1,4):
  for j in range(1,5):
   p=Z/'qa/r04_c13-final'/f'{direction}-{i}-segment-{j}-100pct.png';inspected.append({'file':p.as_posix(),'sha256':sha(p),'status':'passed_visual_100pct','checks':'continuous contours, geometry, materials and lighting; no unresolved hard cut'})
for i in range(1,4):
 for j in range(1,4):
  p=Z/'qa/r04_c13-final'/f'cross-{i}-{j}-100pct.png';inspected.append({'file':p.as_posix(),'sha256':sha(p),'status':'passed_visual_100pct'})
for b in audit['externalBorders']:b['status']='passed_visual_100pct_four_segments_and_three_crossings'
audit['externalTopLeftFourTileCross']='passed_visual_100pct'
audit['adjacentOverlayJoin']='passed_visual_100pct'
audit['reviewedAtUtc']=now
write(Z/'qa/r04_c13-final-audit.json',audit)
review={'tileId':'r04_c13','file':der['file'],'sha256':der['sha256'],'reviewedAtUtc':now,'reviewer':'southeast_tile','overview':'viewed1536preview; all native sources individually reviewed during production','nativeCoreCount':16,'nativeOverlayCount':2,'internalSeamSegmentCount':24,'internalCrossCount':9,'inspectionScale':1,'inspectedFinalCrops':inspected,'overlayEdges':'both native repair cores reviewed at all four exact join boundaries; their mutual boundary reviewed separately','externalBorders':audit['externalBorders'],'externalCrossings':'six internal boundary crossings and one top-left four-tile crossing viewed512square at1:1; pass','resolvedDefects':[{'id':'r04_c13_cross_03_01_repair','description':'removed erroneous paving wedge and rectangular roof discontinuity; blue tiles and fascia form coherent corner'},{'id':'r04_c13_cross_02_01_repair','description':'removed rectangular horizontal highlight band on upper golden curl'}],'unresolvedInternalDefects':[],'pending':['right external4K border and right boundary corners pending r04_c14 completion','bottom external4K border and bottom boundary corners pending r05_c13 completion','formal user acceptance'],'formalAccepted':False,'actualModel':None,'actualQuality':None}
write(Z/'qa/r04_c13-visual-review.json',review)
der.update(status='complete_native_coverage_internal_QA_passed_external_partial',internalReview='passed_final24seam_segments9crossings_and2overlays',externalSeams={'left':'passed_final4K_border_with_r04_c12','top':'passed_final4K_border_with_r03_c13','right':'pending_r04_c14','bottom':'pending_r05_c13'},reviewRecord=(Z/'qa/r04_c13-visual-review.json').as_posix(),finalAudit=(Z/'qa/r04_c13-final-audit.json').as_posix(),formalAccepted=False,reviewedAtUtc=now)
write(Z/'tiles/r04_c13.png.derivation.json',der)
for line in sel['cores']:
 for pid in line:
  p=Z/'native'/f'{pid}.png.generation.json';m=read(p)
  m['status']='selected_native_core_in_internally_reviewed_tile'
  m['finalTileReview']=review['sha256'];m['finalTileReviewRecord']=(Z/'qa/r04_c13-visual-review.json').as_posix()
  if pid in ['r04_c13_p03_01_v2','r04_c13_p03_02','r04_c13_p04_01','r04_c13_p04_02']:m['requiredFinalOverlays']=sel['overlays']
  write(p,m)
for oid in sel['overlays']:
 p=Z/'native'/f'{oid}.png.generation.json';m=read(p);m.update(status='selected_native_repair_core',internalSeams='four repair boundaries visually passed100pct',formalAccepted=False);write(p,m)
print(json.dumps({'tileId':'r04_c13','sha256':der['sha256'],'internalQA':'passed','externalTopAndLeft':'passed','formalAccepted':False}))

