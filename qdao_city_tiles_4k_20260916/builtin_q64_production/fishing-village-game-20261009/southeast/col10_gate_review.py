from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;T=Z/'r11_c10';Q=T/'qa'/'existing-2x2'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
m=read(Q/'manifest.json')
observations={
'r10_c09-p34--r10_c10-p31':'Bench silhouette and rails continuous. Blue cloth weave density changes slightly across join; material observation, not confirmed geometry blocker.',
'r11_c09-p24--r11_c10-p21':'Heavy rail/post silhouette continuous; local wood face tone variation near join. No confirmed structural break.',
}
for s in m['seams']:
 s['visualStatus']='reviewed_no_confirmed_major_geometry_break'
 s['reviewNotes']=observations.get(s['id'],'Native 100% crop inspected: crossing contours continuous; minor wood/cloth texture differences may remain.')
m['crossing']['visualStatus']='reviewed_no_confirmed_major_geometry_break'
m['crossing']['reviewNotes']='Four-tile corner is continuous diagonal wooden floor; no cross-shaped contour break seen.'
m.update(reviewedAt=now,reviewer='next_tile_setup primary visual review',formalAccepted=False,capacityValidated=False)
write(Q/'review.json',m)
im=read(T/'qa'/'internal'/'manifest.json')
for s in im['seams']+im['crossings']:s.update(visualStatus='reviewed_no_confirmed_major_geometry_break',reviewedAt=now,reviewNotes='Continuous wooden floor contours and rail boundary at100%; minor grain differences remain.')
im.update(reviewedAt=now,visualStatus='available_six_positions_reviewed_only',formalAccepted=False,missingNativePositions=10)
write(T/'qa'/'partial-internal-review.json',im)
ack=read(T/'capacity-gate-ack.json')
r10sel=read(Z/'r10_c10'/'selected-patches.json');p10=read(Z/'r10_c10'/'coordinate-plan.json')
coords=[]
for p in p10['patches']:
 if p['id'] in r10sel['patches']:
  f=Z/'r10_c10'/r10sel['patches'][p['id']]
  coords.append({'patch':p['id'],'file':str(f),'sha256':sha(f),'coreGlobalBox':p['coreBox'],'nativeGlobalBox':p['globalBox']})
ack.update(r10c10ExistingSelectedCoordinates=coords,qaReviewedAt=now,existingSharedEdgeSegmentsReviewed=14,existingSharedCrossingsReviewed=1,availableInternalSegmentsReviewed=6,availableInternalCrossingsReviewed=1,confirmedMajorGeometryBlockers=0,formalAccepted=False,capacityValidated=False,styleSourceReplayIssue={'missingPath':'D:/work/image/designs/mail-ui-v1/01-mail-event.png','recordedSha256':'3cf0b7d7b3bae337d51e947719588419a01ae21bdce9bccedd6258ce1feef0a2','affectedReferences':6,'referenceChecksPassed':18,'referenceChecksTotal':24,'differentHashAlternativeFound':'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/user-references-20261009/mail-daoist-style.jpg','alternativeSha256':'c1ab2e50b271e5c5590a92fe68bd6cf7d2c64cbd0d369b25b4ff5c6619033b63','substituted':False})
write(T/'capacity-gate-ack.json',ack)
p=read(T/'progress.json');p.update(updatedAt=now,status='capacity_layout_gate_hold_existing_QA_saved',newGenerationHeld=True,inFlightImageGeneration=False,gate=ack['gate'],nativeCount=6,complete4kCount=0,internalReady=False,formalAcceptedCount=0,nextPatchAfterGateRelease='p23',referenceReplayStatus='18of24_currently_verified_style_source_missing',qaReview=str(Q/'review.json'));write(T/'progress.json',p)
print(json.dumps({'held':True,'r10coordinates':len(coords),'r11coordinates':6,'sharedEdgesReviewed':14,'internalEdgesReviewed':6}))

