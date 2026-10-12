from pathlib import Path
from PIL import Image
import numpy as np
import hashlib,json
from datetime import datetime,timezone

Q=Path(__file__).resolve().parent
R=Q.parent.parent
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
proof=rd(Q/'whole-object-v05-source-replay.json')
assert proof['mismatchPixels']==0 and proof['totalPixelsReplayed']==33554432
manifest=rd(Q/'whole-object-trial-v05.json')
for o in proof['outputs']:
 assert sh(o['file'])==o['sha256'] and sh(o['base'])==o['baseSha256'] and sh(o['sourceID'])==o['sourceIDSha256']
assert sh(proof['mask'])==proof['maskSha256']

north=R/'tiles/r08_c12.candidate-v15.png'
assert sh(north)=='ce6c1019f1df0bb3c327905fc696d7f266a812b295e3e3469786d58315ff5298'
old=np.asarray(Image.open(R/'tiles/r09_c12.candidate-v08.png').convert('RGB'))
new=np.asarray(Image.open(Q/'r09_c12-trial-whole-object-v05.png').convert('RGB'))
segments=[]
for i in range(4):
 x=i*1024
 segments.append({'xRange':[x,x+1024],'north256ExactPriorV08':bool(np.array_equal(old[:256,x:x+1024],new[:256,x:x+1024]))})
assert all(s['north256ExactPriorV08'] for s in segments[1:])
assert np.array_equal(old[:256,389:],new[:256,389:])
junctions=[]
for x in [1024,2048,3072]:
 exact=bool(np.array_equal(old[:256,x-256:x+256],new[:256,x-256:x+256]));assert exact
 junctions.append({'tileX':x,'trialSouthHalfExactPriorAcceptedJunction':exact})

crop_notes={
 'original-bar':'Original long x3814 pale/dark rectangular material division is removed. Curved roof surfaces remain readable across it; the old strong defect is not reclassified minor.',
 'left-top':'New complete curved collars are retained. Two localized source-boundary gutter notches and a small dark-blue wedge remain, listed individually below.',
 'left-foot':'Single continuous physical dark gutter, complete first gold terminal and cast shadow. No leftover old crescent, severed rim or double end. Gutter width varies locally.',
 'complete-foot':'All selected new medallions and their own complete roof ends remain intact. Roof-to-wood silhouette and wood beam remain connected. No new full-width rectangular wood band.',
 'right-top':'Continuous blue barrel and collar outlines through the right source boundary; no strong vertical material bar.',
 'right-foot':'Directly viewed v05 itself because it is not pixel-identical to v03. Gold disc, full blue mouth and neighboring dark gutter remain intact; wood silhouette continuous.',
 'shared-1':'Actual c11/c12 boundary at crop x256 is continuous over y0..1024. No split tile phase or straight material boundary.',
 'shared-2':'Actual c11/c12 boundary at crop x256 is continuous over y1024..2048. Complete roof ends and beam are connected.',
 'r08north-1':'New actual r08c12v15/r09c12trial boundary at crop y256 directly viewed. Roof grooves and collar edges connect. Some paint-grain transition remains but no long strong band or disconnected geometry.',
 'minor-upper-left':'Approximately canvas[3635,495]: dark gutter has a small 5-8px corner/kink. No open gap or separate duplicate contour.',
 'minor-upper-mid':'Approximately canvas[3778,511]: localized triangular blue tone mismatch and 5-8px gutter kink. Clearly visible in the small 100% crop, but does not extend as a long material bar.',
 'minor-left-foot':'Approximately canvas[3310,1085]: local narrowing/corner in the old/new dark gutter. The connected single contour and whole adjacent collar remain intact.'
}
evidence=[]
for n,note in crop_notes.items():
 f=Q/f'whole-object-{n}-v05.png';assert f.exists()
 evidence.append({'file':str(f),'sha256':sh(f),'directNativeScaleVisualReview':n not in ['left-foot','complete-foot'],'reviewMethod':'Verified pixel-identical to directly reviewed v03 crop' if n in ['left-foot','complete-foot'] else 'Directly viewed this v05 crop at native scale','finding':note})
review={
 'timestamp':now,'reviewer':'coordinate_audit','status':'internal_candidate_with_documented_minor_boundary_defects','trialVersion':'whole-object-v05',
 'decision':'Recommend this complete-object 0/1 proposal for root review. It removes the strong original vertical material bar without severed gold terminals, doubled roof ends or broken beams. Two small U-to-whole-source gutter notches and localized blue wedges remain; this is not a claim of a flawless seam.',
 'gateApplied':'Judge actual final cross-source outer contours and strong material jumps. Internal position changes within a wholly selected replacement object are recorded but are not independently grounds for rejection.',
 'internalCompositionChange':{'severity':'minor','detail':'The first complete new roof terminal and its own gold disc move approximately 20px left / 10-17px up relative to old geometry. They are selected together with their entire tile mouth and cast shadow; old disc/rim pixels are not restored inside the new object.'},
 'remainingCrossSourceDefects':[
  {'severity':'minor_local_boundary','centerApproxTwoTileCanvas':[3635,495],'boxApproxTwoTileCanvas':[3615,480,3655,525],'detail':'5-8px corner/kink of the dark groove at the curved upper-to-whole ownership transition. No open roof gap or separate double rim.','evidence':str(Q/'whole-object-minor-upper-left-v05.png')},
  {'severity':'minor_local_boundary','centerApproxTwoTileCanvas':[3778,511],'boxApproxTwoTileCanvas':[3735,505,3795,555],'detail':'Small triangular dark-blue tone patch and 5-8px groove kink. Visible at 100%; not the former 500+px straight material bar.','evidence':str(Q/'whole-object-minor-upper-mid-v05.png')},
  {'severity':'minor_shadow_width_variation','centerApproxTwoTileCanvas':[3310,1085],'detail':'Left physical gutter becomes locally narrow near a collar junction; its single dark outline remains connected.','evidence':str(Q/'whole-object-minor-left-foot-v05.png')}
 ],
 'coordinateSystem':{'twoTileCanvas':'r09c11 at [0,0], r09c12 at [4096,0]','worldOffset':[40960,32768],'pixelGridUnchanged':True},
 'changedObjectBoundaryReview':{'fullTop':True,'fullBottom':True,'fullLeft':True,'fullRight':True,'c11c12SharedEdge':True},
 'northReview':{'northSource':str(north),'northSha256':sh(north),'modifiedPartDirectlyViewed':str(Q/'whole-object-r08north-1-v05.png'),'firstSegmentGeometryContinuous':True,'remainingSegmentsExactPriorEvidence':segments,'threePriorJunctionsExact':junctions,'priorReport':str(R/'qa/roof-final-north-independent.json'),'r09c12Top256UnchangedClaim':False,'detail':'Trial changes r09c12 top256 within x0..388, so old whole-band unchanged status is explicitly NOT reused. Changed first segment directly inspected; x389 onward and all other three segments/junctions remain exact prior accepted RGB. r09c11 north neighbor r08c11 is still ungenerated/unreviewed.'},
 'proof':str(Q/'whole-object-v05-source-replay.json'),'replayedPixels':33554432,'sourceRGBMismatchPixels':0,
 'evidence':evidence,'outputs':proof['outputs'],
 'actualModel':None,'actualQuality':None,'newGenerationDuringMaskRound':False,'pendingRequest':False,
 'mainTilesChanged':False,'progressChanged':False,'formalAccepted':False,'usableExternalAccepted':False,
 'scopeLimit':'Internal candidate and scoped visible-boundary review only. Parent/root owns promotion and final external QA. No r08c11 expansion or further native request issued.'
}
wr(Q/'whole-object-v05-review.json',review)
proposal={'timestamp':now,'status':'internal_candidate_ready_for_root_review','review':str(Q/'whole-object-v05-review.json'),'reviewSha256':sh(Q/'whole-object-v05-review.json'),'sourceReplay':str(Q/'whole-object-v05-source-replay.json'),'sourceReplaySha256':sh(Q/'whole-object-v05-source-replay.json'),'outputs':proof['outputs'],'sources':proof['sources'],'source0':'Prior exact candidate RGB at same coordinate; see its previous source-audit lineage.','sourceIDs':[0,1,3],'mask':proof['mask'],'maskSha256':proof['maskSha256'],'assemblyManifest':str(Q/'whole-object-trial-v05.json'),'sourceCoordinateRule':{'1':'source(x-3300,y)','3':'source(x-3230,y-370)','0':'prior candidate(x,y) in its own tile'},'selection':'Whole native roof objects and their complete gold discs/cast shadows; physical dark gutters and curved collar ownership. Binary source choice only.','noResize':True,'noWarp':True,'noColorAdjustment':True,'noBlending':True,'mainTilesChanged':False,'suggestedNamesIfParentPromotes':['r09_c11.candidate-v05.png','r09_c12.candidate-v09.png'],'minorDefects':review['remainingCrossSourceDefects'],'formalAccepted':False,'usableExternalAccepted':False}
wr(Q/'whole-object-v05-proposal.json',proposal)
manifest['upperWholeCutY']=None
manifest['status']='internal_candidate_with_documented_minor_boundary_defects'
manifest['finalReview']=str(Q/'whole-object-v05-review.json')
manifest['exactSourceReplay']=str(Q/'whole-object-v05-source-replay.json')
wr(Q/'whole-object-trial-v05.json',manifest)
# Correct descriptive metadata only; do not rerun assembly or change PNGs.
p=Q/'assemble_whole_joint_objects.py';s=p.read_text(encoding='utf-8');s=s.replace("'upperWholeCutY':None if V=='v04' else 400","'upperWholeCutY':None if V in ['v04','v05'] else 400");p.write_text(s,encoding='utf-8')

oldreport=rd(Q/'whole-joint-v01-review.json')
oldreport['policyReassessment']={'timestamp':now,'supersedesRejectionForWholeObjectTrial':True,'historicalMeasuredPositionsRetained':True,'reason':'Parent clarified that complete-object internal displacement is allowed if actual cross-source boundaries avoid breakage/double edges or strong material discontinuity. Original anchor-only rejection is historical and not the final verdict.','currentReview':str(Q/'whole-object-v05-review.json'),'currentStatus':review['status']}
wr(Q/'whole-joint-v01-review.json',oldreport)
plan=rd(Q/'repair-plan.json');plan['previousStatus']=plan['status'];plan.update({'status':'whole_object_v05_internal_candidate_pending_root_review','updatedAt':now,'lastReview':str(Q/'whole-object-v05-review.json'),'proposal':str(Q/'whole-object-v05-proposal.json'),'pendingRequest':False,'furtherGenerationIssued':False,'formalAccepted':False});wr(Q/'repair-plan.json',plan)
print(json.dumps({'status':review['status'],'review':str(Q/'whole-object-v05-review.json'),'reviewSha256':sh(Q/'whole-object-v05-review.json'),'proposal':str(Q/'whole-object-v05-proposal.json'),'proposalSha256':sh(Q/'whole-object-v05-proposal.json'),'mainTilesChanged':False},indent=2))
