from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
T=Path(__file__).resolve().parent;Z=T.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
color=read(T/'colorpass-selected.json');src=Path(color['candidate']['file'])
qa=Z/'seam-qa/independent-20261010/r10_c08-final/repair-geometry-review.json'
assert qa.exists();assert sha(src)==color['candidate']['sha256']
snap=T/'selected-before-final-color-20261010.json'
if not snap.exists():shutil.copy2(T/'selected-patches.json',snap)
dest=Z/'ready-for-edge-QA/r10_c08.png';shutil.copy2(src,dest)
assert sha(dest)==sha(src)
report={'tile':'r10_c08','reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'internal_ready_external_seams_pending','candidate':str(src),'candidateSha256':sha(src),'coverage':{'nativeCoreCount':16,'dimensions':[4096,4096],'resamplingApplied':False,'layoutPixelsUsed':False},'reviewBasis':{'baseGeometryFull24Seams9Crossings':str(T/'qa/root-primary-review.json'),'priorIndependentTargetedGeometry':str(T/'qa/independent-review-round2.json'),'newBenchAndCanopyIndependentGeometry':str(qa),'newBenchAndCanopyIndependentReportSha256':sha(qa),'colorFieldsAndCumulativeBounds':str(T/'qa/color-pipeline-audit.json'),'colorCandidateFullPreviewRootViewed':str(T/'processed/colorpass/r10_c08-colorpass-QA-preview-1024.png')},'resolved':['G3 whole bench/rim native repair adopted; shared contours continuous','T1 canopy edge regenerated sharply and adopted at native coordinates'],'residualObservation':'Minor woodgrain/shadow tone variation near world x32371,y40700..40960; independent review finds continuous plank joints and beam contours, no geometry blocker. Verify again with final south/east neighbor context.','maxCumulativeRgbChangeFromGeometry':27,'internalReady':True,'formalAccepted':False,'externalSeams':'pending final neighbors'}
write(T/'qa/internal-review-final.json',report)
sel={'tile':'r10_c08','patches':color['patches'],'status':'internal_ready_external_seams_pending','internalReady':True,'formalAccepted':False,'candidate':str(src),'readyForExternalQA':str(dest),'internalReview':str(T/'qa/internal-review-final.json'),'colorPipelineAudit':str(T/'qa/color-pipeline-audit.json')}
write(T/'selected-patches.json',sel)
write(dest.with_suffix('.png.derivation.json'),{'file':str(dest),'sha256':sha(dest),'source':str(src),'sourceSha256':sha(src),'operation':'byte-identical copy of internally reviewed 4096 candidate','resamplingApplied':False,'internalReview':str(T/'qa/internal-review-final.json'),'formalAccepted':False})
print(json.dumps({'file':str(dest),'sha256':sha(dest),'internalReady':True,'formalAccepted':False}))
