"""Complete deferred closure using pinned, already passed native evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parents[1];Q=Z/'qa/connected-r04-r05-final-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=str(Path(p).resolve()),sha256=sha(p))
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pinned(item):
 assert Path(item['path']).is_file() and sha(item['path'])==item['sha256'],item
 return Path(item['path'])
resume=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
authorization=read(resume)
assert authorization['newArtworkGenerationAllowed'] is True and authorization['historicalFreezeEvidenceMustRemainUnmodified'] is True
freeze=Z/'qa/connected-migration-freeze-20261011.json';f=read(freeze);freeze_before=sha(freeze)
assert freeze_before=='29c5614f18c2887314d594c1fe3da3fe06b8f3f6df027994891bc7b83122ecbf'
manifest=pinned(f['currentLastAppliedManifest']);m=read(manifest)
assert m['tiles']==f['currentLastAppliedTiles']
for tile in m['tiles']:
 pinned(tile['image']);pinned(tile['record'])
passed=f['completedBeforeFreeze'];assert passed['sharedBoundaryNativeQaPassed']==17 and passed['wholeLanternNativeCropsPassed']==2 and passed['repairCombinedIndependentReviewsPassed']==4
replay=pinned(passed['fullOrderedPixelReplay']);pixel=read(replay)
assert pixel['manifest']==f['currentLastAppliedManifest'] and pixel['verifiedPixelCount']==67108864
assert len(pixel['nativeScaleCrops'])==17 and len(pixel['wholeObjectNativeCrops'])==2
repairs=[]
for item in f['successfulSavedNativeOutputs']:
 review_path=pinned(item['completedVisualReview']);review=read(review_path)
 for k in ('raw','generation','receipt','prompt','mask','combined'):pinned(item[k])
 assert review['authorVisualPassed'] is True and review['independentVisualPassed'] is True
 repairs.append(dict(stem=item['stem'],raw=item['raw'],generation=item['generation'],receipt=item['receipt'],prompt=item['prompt'],mask=item['mask'],combinedNativeImage=item['combined'],selectedPixels=review['selectedPixels'],nativeVisualPassed=True,independentReviewer=review['independentReviewer'],independentVisualPassed=True,savedReview=item['completedVisualReview']))
checks=[]
for item in pixel['nativeScaleCrops']:
 pinned(item['output'])
 checks.append(dict(**item,visualPassed=True,reviewMethod='Prior native visual PASS; exact pixel equality to original passed crop' if item['matchesInitialViewedNativeCrop'] else 'Changed final native crop reopened and visually passed before freeze',reviewEvidence=info(freeze)))
for item in pixel['wholeObjectNativeCrops']:pinned(item['output'])
audit=pinned(passed['strictFinalRecursiveAuditInput']);pinned(f['southBoundaryHandoff']['edgeDifferenceEvidence'])
report=dict(schemaVersion=1,completedAtUtc=datetime.now(timezone.utc).isoformat(),scope='r04/r05 x c03/c04 connected cluster internal shared boundaries',status='shared_boundary_visual_closure_passed_perimeter_pending',resumeAuthorization=info(resume),historicalFreezeEvidence=info(freeze),completionMethod='Deferred closure documentation from unchanged hash-pinned native visual and strict replay evidence; no artwork change or repeated visual review',finalManifest=info(manifest),candidateTileCount=4,sharedBoundaryPairCount=4,nativeQaCount=17,nativeQaPassed=17,repairNativeGenerationCount=4,repairs=repairs,checks=checks,wholeObjectNativeCrops=[dict(**item,visualPassed=True,reviewEvidence=info(freeze)) for item in pixel['wholeObjectNativeCrops']],wholeLanternVisualPassed=True,fullFinalPixelReplay=info(replay),verifiedPixelCount=67108864,orderedRepairOverlapPixels=passed['orderedRepairOverlapPixels'],strictFinalRecursiveProvenanceAudit=info(audit),strictMemo=passed['strictInvocationMemo'],clusterOuterEdgesIdenticalToInitialConnected=True,sourceInputEdgeDifferences=f['southBoundaryHandoff'],formalAcceptedCount=0,remaining=['Outer neighbors require separate shared-boundary and zone closure.','Use final r05_c03 south x4089..4095 for r05/r06 junction; final r05_c04 south remains the internal v4 edge.'],reviewNotes=['Complete lantern cap, body, mount, bead and single tassel passed in two overlapping native crops before freeze.','Four native repairs independently passed root review before freeze.','Historical freeze record retained byte-for-byte; root progress is not modified.'])
out=Q/'closure.json'
with out.open('x',encoding='utf8') as handle:json.dump(report,handle,ensure_ascii=False,indent=2)
assert sha(freeze)==freeze_before
print(json.dumps(dict(closure=info(out),finalManifest=info(manifest),nativeQaPassed=17,wholeLanternVisualPassed=True,artworkChanged=False),indent=2))
