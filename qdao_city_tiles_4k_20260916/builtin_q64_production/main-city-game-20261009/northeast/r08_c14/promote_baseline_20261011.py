from pathlib import Path
import hashlib,json,shutil
from datetime import datetime,timezone
from PIL import Image
T=Path(__file__).resolve().parent
B=T/'qa/core-baseline/a08b236df6a6c9ae8a1d'
A=json.loads((B/'assembly.json').read_text(encoding='utf-8'))
assert A['validSelectedNativeCount']==16 and not A['invalidSelectedSources'] and A['allReferenceBytesReverified']
src=B/'r08_c14-core-baseline.candidate.png'
dst=T/'candidates/r08_c14.candidate.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not dst.exists() or sha(dst)==sha(src),'Preserve changed candidate'
if not dst.exists():shutil.copy2(src,dst)
save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save(Path(str(dst)+'.generation.json'),{'file':str(dst),'sha256':sha(dst),'width':4096,'height':4096,'format':'PNG','assetRole':'complete4kCandidate awaiting visual review','derivedFrom':[{'file':str(src),'sha256':sha(src),'assembly':str(B/'assembly.json'),'assemblySha256':sha(B/'assembly.json')}],'operation':{'method':'exact baseline PNG copy; sixteen native 1024 cores','resized':False,'feathered':False},'actualModel':None,'actualQuality':None,'formalAcceptedCount':0})
native=[{'patch':f'p{r}{c}','file':str(T/f'native/p{r}{c}.png'),'sha256':sha(T/f'native/p{r}{c}.png')} for r in range(1,5) for c in range(1,5)]
save(T/'tile-progress.json',{'tile':'r08_c14','status':'complete_4k_candidate_awaiting_internal_seam_review','updatedAt':datetime.now(timezone.utc).isoformat(),'nativeCount':16,'selectedCoreCount':16,'remainingCoreCount':0,'nativeSources':native,'completeCandidateCount':1,'internalPassed4kCount':0,'formalAcceptedCount':0,'candidate':str(dst),'candidateSha256':sha(dst),'nextPatch':None,'inflightGeneration':None,'nextStep':'Review 24 internal seams and 9 intersections, then second connected-group shared edges','actualModel':None,'actualQuality':None})
preview=T/'qa/r08_c14-preview-25pct.png'
Image.open(dst).resize((1024,1024),Image.Resampling.LANCZOS).save(preview)
print(json.dumps({'candidate':str(dst),'sha256':sha(dst),'preview':str(preview)}))

