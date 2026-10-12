from pathlib import Path
from PIL import Image
import hashlib,json,datetime
B=Path(__file__).resolve().parent;T=B/'r13_c13';C=T/'candidate'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
image=C/'r13_c13-4k-candidate-repaired.png';context=C/'r13_c13-context-4326-repaired.png';qapath=T/'review'/'current'/'qa-report.json';qa=read(qapath);replay=read(C/'replay-verification.json')
assert qa['imageSha256']==sha(image)==replay['sha256'],'QA/replay must cover current exact candidate'
assert Image.open(image).size==(4096,4096) and Image.open(context).size==(4326,4326)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
passed=qa['internalVerdict']=='pass'
pr=read(B/'progress.json');pr.update(updatedAt=now,status='candidate_internal_pass_external_pending' if passed else 'candidate_internal_repair_required',plannedTileCount=64,notStartedTileCount=63,activeNativePatchCount=16,nativePatchGeneratedCount=22,nativeRepairCount=7,generatedNativeCount=29,complete4kCandidateCount=1,formalAcceptedCount=0,internalQaPassed=passed,externalSeamsVerified=False,qaReport=str(qapath),qaReportSha256=sha(qapath),provenanceVerified=True,exactReplayVerified=True,underlyingTaskComplete=False,nextStep='Review corrected outside-right halo and generate r13_c14 with current native boundary context; repair cross-tile join before formal acceptance.' if passed else 'Resolve current qa-report findings before generating neighboring tile.')
write(B/'progress.json',pr)
derived={'schemaVersion':1,'createdAt':now,'file':str(image),'sha256':sha(image),'dimensions':[4096,4096],'zone':'southeast','tile':'r13_c13','artCanvasPixels':[65536,65536],'coreBox':[49152,49152,53248,53248],'status':pr['status'],'formalAccepted':False,'internalQaPassed':passed,'externalSeamsVerified':False,'sourceNativePatchCount':16,'sourceNativeRepairCount':7,'measuredNativeSize':[1254,1254],'upscaledArt':False,'resampledArt':False,'nativeGenerationRoute':'builtin image_gen.imagegen','actualModel':None,'actualQuality':None,'actualModelQualityReason':'Host tool did not expose selectors or return backend version/quality metadata. Targets remain recorded per image, not asserted as actual.','recipeFiles':[{'path':str(p),'sha256':sha(p)} for p in [C/'assembly-manifest.json',T/'repairs'/'composition-history.json',T/'repairs'/'context-composition.json',C/'replay-verification.json',qapath]],'context':{'file':str(context),'sha256':sha(context),'dimensions':[4326,4326],'coreCrop':[115,115,4211,4211],'outsideHaloSeams':'pending; do not assume unchanged outer context is automatically geometry-correct'},'worldSize':None,'clientMappingValidated':False,'capacity5000Validated':False}
write(str(image)+'.derived.json',derived)
print(json.dumps({'status':pr['status'],'candidateCount':1,'internalQaPassed':passed,'formalAcceptedCount':0,'notStartedTiles':63,'candidateSha256':sha(image)},ensure_ascii=False))

