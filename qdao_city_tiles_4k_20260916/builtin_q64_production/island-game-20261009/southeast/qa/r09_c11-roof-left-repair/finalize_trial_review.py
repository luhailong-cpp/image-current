from pathlib import Path
from datetime import datetime,timezone
import os,json,hashlib
R=Path(__file__).resolve().parents[2];Q=Path(__file__).resolve().parent
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c12.json'
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wr(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def ev(n):
 p=Q/n
 return {'file':str(p),'sha256':sh(p),'nativeScale':True}
replay=json.loads((Q/'trial-source-replay.json').read_text())
review={
 'timestamp':datetime.now(timezone.utc).isoformat(),
 'status':'rejected_do_not_promote',
 'scope':'r09_c11 v05 / r09_c12 v09 proposals only; no main tiles or progress changed',
 'decision':'Original x3814 blue material bar is removed within both new sources, but replacement sources drift in left gutter/terminal-medallion geometry. Both prepared exact-pixel ownership trials introduce unacceptable new discontinuities. Neither is an acceptable candidate.',
 'coordinateSystem':'All x/y below are two-tile canvas coordinates, with r09_c11 at [0,0] and r09_c12 at [4096,0]. World offset is [40960,32768].',
 'findings':[
  {'severity':'reject','area':'rectangular left ownership boundary x3368','rangeForInspection':[3200,750,3600,1550],'detail':'The bright curved tile lip and black trough change phase at the straight cut. The white lip has a visible vertical step and a partial displaced terminal medallion. This is new geometry damage, not acceptable paint texture.', 'evidence':[ev('left-lower-rect-v01.png'),ev('fixed-v14-rect-v01.png')]},
  {'severity':'reject','area':'roof bottom object ownership','rangeForInspection':[3300,1150,4554,1854],'detail':'Blue-only bottom ownership cuts into old/new gold terminal discs. The first two terminals differ materially in location; the mask exposes double outlines and gold crescents. A lowest-blue-pixel silhouette is not a complete roof-plus-medallion object mask. Source geometry drift remains even if the discs are included.', 'evidence':[ev('bottom-left-rect-v01.png'),ev('bottom-right-rect-v01.png'),ev('shared-lower-rect-v01.png')]},
  {'severity':'reject','area':'minimum-cost coordinate-path ownership trial','detail':'The trial called natural follows per-row image differences but does not establish a valid shared gutter. It produces a diagonal clipped/doubled trough and a hard tonal corner on the upper tile. It also duplicates the left terminal geometry. Low pixel error cannot override this visual failure.', 'evidence':[ev('left-upper-natural-v01.png'),ev('left-lower-natural-v01.png'),ev('complete-top-natural-v01.png')]},
  {'severity':'minor_new_transition','area':'rectangular right boundary x4530','detail':'Upper geometry is close. A visible narrow vertical material transition remains through lower blue tile texture; no principal gutter severing was seen there. This is secondary to the left and bottom rejection.', 'evidence':[ev('right-upper-rect-v01.png'),ev('right-lower-rect-v01.png')]},
  {'severity':'localized_continuity_observed','area':'upper/lower native join y737','detail':'Away from the separate left-edge defect, the true world-aligned 654-pixel overlap supports a continuous internal join at y737. No broad horizontal rectangular material step was observed in this crop.', 'evidence':[ev('upper-lower-rect-v01.png')]},
  {'severity':'localized_continuity_observed','area':'r09c11/r09c12 shared edge x4096','detail':'The shared vertical boundary inherits the same native sources on both sides and no seam at x4096 was observed. The lower evidence still contains the nearby invalid medallion ownership described above. This observation does not make either tile acceptable.', 'evidence':[ev('shared-upper-rect-v01.png'),ev('shared-lower-rect-v01.png')]},
  {'severity':'not_reaccepted','area':'r09c12 north against r08c12v15','detail':'The rectangular trial changes 110714 pixels in r09c12 north256; path trial changes 91802. The earlier exact-unchanged v08/v06 north proof does not apply to these trials. The 458-pixel affected cross-boundary crop has no obvious principal contour gap, but both full candidates are rejected and no new external acceptance is issued.', 'evidence':[ev('north-r08-rect-v01.png')]}
 ],
 'visualCoverage':{
  'rectTrialAffectedPerimeterComplete':True,
  'directlyViewed':['left-upper-rect-v01.png','left-lower-rect-v01.png','right-upper-rect-v01.png','right-lower-rect-v01.png','bottom-left-rect-v01.png','bottom-right-rect-v01.png','upper-lower-rect-v01.png','shared-upper-rect-v01.png','shared-lower-rect-v01.png','fixed-v14-rect-v01.png','complete-top-rect-v01.png','north-r08-rect-v01.png','left-upper-natural-v01.png','left-lower-natural-v01.png','complete-top-natural-v01.png'],
  'naturalTrialFullPerimeterAccepted':False,
  'naturalTrialEarlyRejection':'Independent left/top inspections already establish unacceptable geometry.',
  'unaffectedOuterBoundaryProof':'See edgeBandsExactVsBase in trial-source-replay.json: old outer west of r09c11, outer east of r09c12, and both south bands stay exact.'
 },
 'sourceReplay':{'file':str(Q/'trial-source-replay.json'),'sha256':sh(Q/'trial-source-replay.json'),'allFourTileOutputsZeroMismatchedPixels':True,'RGBModified':False,'resampled':False,'feathered':False},
 'newNative':replay['nativeAudit'],
 'roundLimit':{'successfulNativeCount':2,'maximum':2,'pendingRequest':False,'furtherImageGenerationIssued':False,'networkBlockObserved':False},
 'nextRecommendation':'Keep existing main candidates. Before any further generation, agree a geometry-preserving complete-object repair whose source support includes the entire left affected tile gutter and its terminal disc. Neither hard-cut optimization nor RGB blending can recover coincident geometry that these two sources did not preserve. Further original generation requires the parent to authorize a new round; this authorized two-image round is exhausted.',
 'recordClarification':'The lower request/reference role described upper as accepted. That described an available saved source, not visual acceptance; both upper and lower are source-valid and trial-rejected pending geometry repair.',
 'formalAccepted':False,
 'usableExternalAccepted':False,
 'r08c11GuidesRemainPaused':True
}
wr(Q/'independent-trial-review.json',review)
proposal={'timestamp':review['timestamp'],'status':'rejected_do_not_promote','proposedVersionNamesOnly':['r09_c11.candidate-v05','r09_c12.candidate-v09'],'proposals':replay['trials'],'review':str(Q/'independent-trial-review.json'),'reviewSha256':sh(Q/'independent-trial-review.json'),'sourceReplay':str(Q/'trial-source-replay.json'),'sourceReplaySha256':sh(Q/'trial-source-replay.json'),'sourceRGBExact':True,'visualPass':False,'formalAccepted':False,'noMainTileWrites':True}
wr(Q/'trial-proposal-final.json',proposal)
p=json.loads((Q/'repair-plan.json').read_text());p.update(status='two_native_saved_trials_rejected',updatedAt=review['timestamp'],successfulNewNativeCount=2,pendingRequest=False,maximumNativeCallsThisRound=2,furtherGenerationIssued=False,proposal=str(Q/'trial-proposal-final.json'),review=str(Q/'independent-trial-review.json'),formalAccepted=False);wr(Q/'repair-plan.json',p)
for kind in ['rect','natural']:
 p=Q/f'{kind}-trial-v01.json';m=json.loads(p.read_text());m.update(status='rejected_do_not_promote',visualReview=str(Q/'independent-trial-review.json'),formalAccepted=False);wr(p,m)
print(json.dumps({'proposal':str(Q/'trial-proposal-final.json'),'proposalSha256':sh(Q/'trial-proposal-final.json'),'review':str(Q/'independent-trial-review.json'),'mainTileWrites':False,'decision':'rejected_do_not_promote'},indent=2))
