from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;BASE=D.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,a):
 p=Path(p);assert not p.exists(),p;p.write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
stem='eastdeck-G2-v6-color-finish-v1';report=read(D/(stem+'.report.json'));npz=np.load(report['replay']);rr=np.clip(np.rint(npz['raw'].astype(np.float32)+npz['offsetField']),0,255).astype(np.uint8);rebuilt=npz['before'].copy();rebuilt[npz['mask']]=rr[npz['mask']]
assert np.array_equal(rebuilt,npz['final']);assert float(abs(npz['offsetField']).max())<=24
assert np.array_equal(rebuilt[~npz['mask']],npz['before'][~npz['mask']])
base=read(D/'eastdeck-G2-final-v5.adoption-instructions.json');oldz=np.load(base['replayNpz'])
assert np.array_equal(oldz['original'][~npz['mask']],rebuilt[~npz['mask']])
spec=importlib.util.spec_from_file_location('sources',BASE/'review_external_seams.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);sources=mod.Sources()
for r in report['patches']:
 cur,err=sources.source(r['tile'],r['patch']);assert not err;assert cur['file']==r['source'] and cur['sha256']==r['sourceSha256'];assert sha(r['file'])==r['sha256']
 sources.tile(r['tile'])['selection']['patches'][r['patch']]=r['file']
im,_,missing=sources.extract([32141,37925,33395,39179]);assert not missing;assert np.array_equal(np.asarray(im),rebuilt)
review={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'improved_material_candidate_remaining_boundary_pending','allSixNativeEvidenceViewed':True,'evidence':report['evidence'],'endpointEvidence':str(D/'G2-v5-v6-color-endpoint-check-20261013.json'),'observations':['Native v6 improves the central wood surface continuity across former internal rectangles.','Additive RGB field further reduces right-side dark tone bands; actual offset magnitude is11.73774 (pixel rounding maximum12), cap24. Artwork itself is never interpolated or blurred.','Five left boundary groove darkest-row deltas are[-1,0,-1,0,-2], compared with previous[-1,-1,-1,-1,-3]; right boundary deltas[0,0,0,-1,0]. Darkest-row evidence supports no new larger endpoint displacement, but is not alone a visual acceptance.','Rectangular wood-grain transitions remain visible at original union edges, particularly x850/x915 and the upper post-shadow cut x627; this is not a final material pass. Stone pixels outside the mask are byte-exact original.'],'geometryReadyForIndependentReview':True,'materialPending':True,'internalReady':False,'formalAccepted':False,'canonicalSelectionsModified':False}
save(D/(stem+'.native-review.json'),review)
save(D/(stem+'.adoption-instructions.json'),{'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'improved_candidate_material_pending','frameWorld':[32141,37925,33395,39179],'overallAdoptionBoundingWorld':[32581,38135,33056,39025],'nativeCore':[115,115,1139,1139],'patches':report['patches'],'raw':report['raw'],'rawSha256':report['rawSha256'],'rawReceipt':str(D/'eastdeck-G2-conditioned-v6.generation-receipt.json'),'adoptMask':report['mask'],'adoptMaskSha256':report['maskSha256'],'colorOperation':report['fieldOperation'],'maxAbsField':report['maxAbsField'],'colorCap':24,'colorReplayNpz':report['replay'],'colorReplayNpzSha256':report['replaySha256'],'nativeSourceReplayExact':True,'nativeCoreReplayExact':True,'outsideOriginalUnionChangedPixels':0,'canonicalSourceHashesVerifiedCurrent':True,'materialPending':True,'internalReady':False,'formalAccepted':False,'actualModel':None,'actualQuality':None,'paidApiUsed':False,'resampling':False,'pixelShift':False,'blur':False,'pixelBlending':False,'syntheticGeometry':False,'canonicalSelectionsModified':False,'review':str(D/(stem+'.native-review.json')),'adoptionInstructions':'Root independent inspection only. Do not mark final acceptance. If provisionally using this improved geometry/material candidate, verify all four current canonical source hashes then coordinate all four native replacements together. The current candidate is raw v6 plus saved bounded additive RGB field inside the exact prior v3/v4/v5 union; all outside pixels equal original canonical frame.'})
# Read-only current-source confirmation and missing native QA completion.
sources=mod.Sources();wall=BASE/'seam-qa/repair-resume-20261012';g3=BASE/'seam-qa/G3-shared-stairs-resume-20261012'
wallInstr=read(wall/'r12c08-wall-rock-rail-color-finish-v1.adoption-instructions.json');g3Instr=read(g3/'G3-bottom-conditioned-v3.adoption-instructions.json')
currentChecks={}
for name,ins in [('wall',wallInstr),('sharedG3',g3Instr)]:
 rows=[]
 for r in ins['patches']:
  cur,err=sources.source(r['tile'],r['patch']);assert not err
  expected=r['sha256'];assert cur['sha256']==expected
  rows.append({'tile':r['tile'],'patch':r['patch'],'currentFile':cur['file'],'sha256':cur['sha256'],'sameAsPreviouslyReviewedNativeCandidate':True})
 currentChecks[name]=rows
wallQA=[]
for n in ['p13--p14','p14--p24','cross-r1-c3']:
 f=BASE/'r12_c08/qa/wall-joint-resume-20261012-v1'/(n+'.png');d=read(str(f)+'.derivation.json');assert sha(f)==d['sha256']
 img,pcs,missing=sources.extract(d['globalBox']);assert not missing;assert np.array_equal(np.asarray(img),np.asarray(Image.open(f).convert('RGB')))
 for p in d['sources']:assert sha(p['file'])==p['sha256']
 wallQA.append({'file':str(f),'sha256':sha(f),'globalBox':d['globalBox'],'currentSelectedCoreReplayExact':True,'viewedOriginalSize':True,'geometryPassed':True,'localMaterialPassed':True,'observation':'Continuous rounded rock silhouettes, ground/foliage gaps and stone grain at the actual internal seam; no new cut line within this evidence.'})
frame=[36060,46592,37314,47846];im,_,missing=sources.extract(frame);assert not missing
oldg=g3/'G3-bottom-conditioned-v3-bounded-preview-native1254.png';assert np.array_equal(np.asarray(im),np.asarray(Image.open(oldg).convert('RGB')))
summary={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'local_joint_QA_completed_remaining_material_open','canonicalSelectionsModified':False,'currentSourceChecks':currentChecks,'completedWallInternalEvidence':wallQA,'sharedG3ReviewReuse':{'priorRootReview':str(g3/'root-v3-independent-geometry-review.json'),'priorRootReviewSha256':sha(g3/'root-v3-independent-geometry-review.json'),'nativeFrameWorld':frame,'currentFrameMatchesPreviouslyReviewedCandidateExactly':True,'previousCandidate':str(oldg),'previousCandidateSha256':sha(oldg),'fullNativeContextViewedAgainForMaterialAssessment':True,'geometryPassedAsPreviouslyReviewed':True,'materialPending':True,'materialObservation':'Thin linear-grain/density boundaries remain around the wood mask and small80px square infill; no geometry regression. No new AI call here.'},'wallMaterialStatus':{'geometryPassedAsPreviouslyReviewed':True,'materialPending':True,'observation':'Dense small stone flecks versus larger adjacent painted facets remain visibly different at original wall/rock repair boundaries. Existing bounded color correction already reduced tone without resolving density; another color-only pass cannot supply native texture.','priorReview':str(wall/'r12c08-wall-rock-rail-color-finish-v1.native-review-v1.json')},'currentCandidates':{'benchG3':str(D/'bench-G3-best-v12-20261013.adoption-instructions.json'),'benchC2':str(D/'bench-C2-best-v7-20261013.adoption-instructions.json'),'eastdeckG2':str(D/(stem+'.adoption-instructions.json'))},'formalAccepted':False,'internalReady':False,'materialPending':True,'inFlight':False,'allReturnedImagesSaved':True,'remainingWork':'Grouped native material finishing remains for G2/C2/benchG3/sharedG3/wall. This record completes only current local evidence and candidate packaging; it does not claim all points exhausted two unsuccessful attempts.'}
save(D/'joint-independent-status-20261013-v3.json',summary)
print(json.dumps({'G2Instructions':str(D/(stem+'.adoption-instructions.json')),'status':str(D/'joint-independent-status-20261013-v3.json'),'wallNewLocalQACount':len(wallQA),'G3PriorReviewExactReuse':True,'G2MaxField':report['maxAbsField']}))

