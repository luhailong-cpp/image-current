"""Refresh complete tile candidate metadata and verify every native provenance chain."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
stamp=datetime.now(timezone.utc).isoformat()
sel=read(T/'selected-patches.json')
entries=[];refchecks=[];failures=[]
for rp in sorted(T.rglob('*.png.generation.json')):
 d=read(rp);p=Path(d['file']);assert Image.open(p).size==(1254,1254);assert d['sha256']==sha(p)
 assert d['actualModel'] is None and d['actualQuality'] is None
 assert d['submittedParameters']=={'model':None,'quality':None}
 prompt=Path(d['prompt']);request=prompt.with_name(prompt.name.replace('.prompt.txt','.request.json'));receipt=Path(d['evidence']['receipt'])
 assert prompt.exists() and request.exists() and receipt.exists()
 d['promptSha256']=sha(prompt);d['evidence'].update(request=str(request),requestSha256=sha(request),receiptSha256=sha(receipt))
 assert len(d['references'])==5
 for ref in d['references']:
  source=Path(ref.get('verifiedSnapshotPath',ref['path']));assert source.exists() and sha(source)==ref['sha256'],str(source)
  refchecks.append({'generationRecord':str(rp),'submittedReference':ref['path'],'verifiedFile':str(source),'sha256':ref['sha256']})
 write(rp,d)
 entries.append({'file':str(p),'sha256':sha(p),'record':str(rp),'recordSha256':sha(rp),'nativeDimensions':[1254,1254],'directlySelected':p.relative_to(T).as_posix() in sel['patches'].values(),'configTarget':{'model':d['configSnapshot']['model'],'quality':d['configSnapshot']['quality']},'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'builtinOnly':True})
for p in T.rglob('*.receipt.json'):
 d=read(p)
 if d.get('status')=='failed' or d.get('error'):failures.append({'receipt':str(p),'sha256':sha(p),'detail':d})
assert len(sel['patches'])==16
candidate=T/'r10_c10-candidate-4096.png';im=np.asarray(Image.open(candidate).convert('RGB'));assert im.shape==(4096,4096,3)
selected=[]
for pid,rel in sorted(sel['patches'].items()):
 p=T/rel;native=np.asarray(Image.open(p).convert('RGB'));assert native.shape==(1254,1254,3)
 r,c=int(pid[1])-1,int(pid[2])-1;assert np.array_equal(im[r*1024:(r+1)*1024,c*1024:(c+1)*1024],native[115:1139,115:1139])
 selected.append({'patch':pid,'file':str(p),'sha256':sha(p),'dimensions':[1254,1254],'coreCrop':[115,115,1139,1139],'assembledPixelsExact':True})
qa=read(T/'qa/internal/manifest.json');assert len(qa['seams'])==24 and len(qa['crossings'])==9
review={'tile':'r10_c10','reviewedAt':stamp,'reviewer':'next_tile_setup','candidate':{'path':str(candidate),'sha256':sha(candidate),'dimensions':[4096,4096]},'selectedSources':selected,'reviewedSeams':24,'reviewedCrossings':9,'method':'native 100% seam/crossing crops plus all native generation results and explicit adoption boundaries; previous independent 20-seam/7-crossing review incorporated and repaired regions rechecked','status':'internal_candidate_ready_external_review_pending','formalAccepted':False,'blockingGeometryFindings':[],'resolved':['first-row roof/eave, golden binding and canopy-hem joins repaired with native cross-seam edits','p24 y230 net break repaired by builtin imagegen; connected-net silhouette adopted, unrelated bench/floor pixels restored exactly','p33-p34 foreground rim/wave border repaired jointly, then p34 adoption-edge notch corrected using builtin edit; adoption endpoints checked at matching native contours','bounded RGB color fields close local adoption color differences without image blur, spatial resampling or coordinate shift'],'nonblockingObservations':['Minor cloth weave and local wood-grain/illumination variation remain visible at native scale; no major broken contour remains in inspected cores.'],'independentReview':{'priorReport':str(T/'qa/internal-review/review.json'),'priorCoverage':[20,7],'finalChangedSourceReview':'pending separate reviewer availability'},'externalSeams':'pending final neighboring tile sources; west refreshed to r10_c09 local selection for p41; earlier raw-derived west content requires final external QA','imageResamplingAppliedToDelivery':False,'layoutImagesAreInputOnly':True}
write(T/'qa/internal-primary-review.json',review)
for seam in qa['seams']:
 seam.update(visualStatus='reviewed_internal_candidate_no_major_geometry_blocker',reviewer='next_tile_setup',reviewedAt=stamp,formalAccepted=False)
for cross in qa['crossings']:
 cross.update(visualStatus='reviewed_internal_candidate_no_major_geometry_blocker',reviewer='next_tile_setup',reviewedAt=stamp,formalAccepted=False)
qa.update(visualStatus='internal_candidate_ready_external_review_pending',primaryReview=str(T/'qa/internal-primary-review.json'),independentFinalReviewPending=True)
write(T/'qa/internal/manifest.json',qa)
sel.update(status='internal_candidate_ready_external_review_pending',formalAccepted=False,updatedAt=stamp,independentFinalReviewPending=True);write(T/'selected-patches.json',sel)
write(T/'generation-index.json',{'tile':'r10_c10','updatedAt':stamp,'route':'builtin','count':len(entries),'images':entries,'actualModelQualityConfirmed':False,'successfulNative1254Count':len(entries),'failedToolCalls':failures,'selectedCandidates':selected})
write(T/'qa/provenance-audit.json',{'tile':'r10_c10','checkedAt':stamp,'success':True,'nativeImages':len(entries),'referencesChecked':len(refchecks),'referenceEvidence':refchecks,'selectedCorePixelsExactlyMatch4K':True,'allNativeDimensions':[1254,1254],'submittedAndActualModelQuality':None,'actualModelQualityConfirmed':False,'layoutPixelsMechanicallyUsedInCandidate':False,'candidateSha256':sha(candidate)})
progress=read(T/'progress.json')
if progress.get('errors'):
 progress['historicalAttemptFindings']=[dict(e,resolution='superseded by later native joint repairs') for e in progress['errors']]
progress.update(updatedAt=stamp,status='internal_candidate_ready_external_review_pending',currentPatch=None,targetNativeCount=16,generatedNativeCount=len(entries),selectedNativeCount=16,complete4kCount=1,formalAcceptedCount=0,internalSeamsReviewed=24,internalCrossingsReviewed=9,externalSeamsRequireRecheck=True,nextStep='Final independent changed-source review and external neighbor QA; do not mark formal until zone acceptance',toolFailures=failures,toolFailuresResolvedByRetry=True,geometryBlockingCount=0,errors=[])
write(T/'progress.json',progress)
readme="""# r10_c10 — 4K internal candidate

16 selected native1254² patches have been hard-cropped at [115,115,1139,1139] into r10_c10-candidate-4096.png. Every1024² core matches the selected source exactly. No final pixels were enlarged.

The tile occupies world [36864,36864,40960,40960] in the57344²,14×14 map. Selection is local in selected-patches.json; root zone progress and r10_c09 were not changed.

Current primary QA covers24 native internal seam crops and9 crossings. Internal candidate is ready for final independent changed-source review and external-neighbor review. Formal acceptance remains false. Minor cloth/wood texture variation is recorded as nonblocking observation. qa/internal-primary-review.json is the current report; older first-row and independent interim reports describe their saved earlier source hashes.

generation-index.json lists every successful builtin image and source record. Each has prompt, request, actual tool output_hint receipt, configuration snapshot, references with roles and hashes, global coordinates and measured native size. Config target is recorded separately; submitted and actual model/quality are null because the host does not expose them. The p22-v1 network failure is retained as a receipt.

Geometry repairs use builtin-generated native1254 edits, exact native crops and explicit bounded adoption. Connected-net silhouette adoption preserves unrelated original bench/floor pixels. Additive color fields alter only RGB values at original pixel centers, never blur, shift or resample artwork; all fields and source hashes are saved. Cross-patch color finishing applies the same field to each patch's own image pixels.

layout-only/ contains enlarged input guides only. input-snapshots/ preserves a hash-verified earlier submitted guide. qa/ previews are downsamples only for inspection and are never delivery sources.

Scripts: tile_native_workflow.py in the parent zone prepares/refreshed guides; qa_tile.py assembles and refreshes inspection crops; finalize_tile.py verifies and refreshes this tile's records. Re-running qa_tile.py sets inspection status pending, so inspect changed sources and rerun finalize_tile.py only after reviewing them.
"""
(T/'README.md').write_text(readme,encoding='utf-8')
print(json.dumps({'nativeImages':len(entries),'referencesChecked':len(refchecks),'selected':16,'candidateDimensions':[4096,4096],'seams':24,'crossings':9,'formalAccepted':False,'failedCalls':len(failures)}))

