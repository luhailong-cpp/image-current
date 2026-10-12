from pathlib import Path
import json,hashlib,runpy
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,j:Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
rules=Path('D:/work/image/AGENTS.md');req=Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pause=read(Z/'image-model-pause-20261012.json');pause.update({'projectRules':str(rules),'projectRulesSha256':h(rules),'modelRequirementSha256':h(req),'updatedAtUtc':now})
save(Z/'image-model-pause-20261012.json',pause)
r=read(Z/'production-resume-20261012.json');r.update({'status':'new_generation_paused_required_verified_GPT_Image_2_5','generationStopped':True,'newArtworkGenerationAllowed':False,'imageModelPause':str(Z/'image-model-pause-20261012.json'),'requestedImageModel':'GPT Image 2.5','projectRules':str(rules),'projectRulesSha256':h(rules),'nextStep':'Continue existing asset inventory, assembly and review. Missing cores and AI repairs pause until an explicitly selectable verified GPT Image 2.5 route is available without paid API.','updatedAtUtc':now,'currentCoordinate':'r07_c15/p44 prepared but never submitted; 15/16 partial review recorded'})
save(Z/'production-resume-20261012.json',r)
t=Z/'r07_c15/tile-progress.json';v=read(t);v.update({'status':'paused_pending_verified_GPT_Image_2_5_missing_one_core_two_P2','updatedAt':now,'selectedCoreCount':15,'remainingCoreCount':1,'nextPatch':'p44','inflightGeneration':None,'candidate':None,'completeCandidateCount':0,'internalPassed4kCount':0,'formalAcceptedCount':0,'requestedImageModel':'GPT Image 2.5','generationStopped':True,'partialAssembly':str(Z/'r07_c15/qa/core-baseline/cc4957ad3118e1d860b7/assembly.json'),'partialVisualReview':str(Z/'r07_c15/qa/model-pause-20261012/visual-review.json'),'pendingP2RepairCount':2,'preparedNeverSubmitted':['p44-v20261012']});save(t,v)
runpy.run_path(str(Z/'refresh_progress.py'),run_name='__main__')
p=read(Z/'progress.json');r.update({'currentCandidateCount':p['complete4kCandidateCount'],'internalPassedCount':p['internalPassed4kCount'],'connectedGroupReviewedCount':p['connectedGroupReviewed4kCount'],'newSelectedCoreCount':p['usableSelectedCoreCount']-128,'remainingNativeCoreCount':p['missingNativeCoreCount']});save(Z/'production-resume-20261012.json',r)
i=read(Z/'current-adopted-index-20261012.json');i.update({'updatedAt':now,'generationStopped':True,'newOutputCount':p['generatedNativeCount']-176,'newSelectedCoreCount':p['usableSelectedCoreCount']-128,'requestedImageModel':'GPT Image 2.5','imageModelPause':str(Z/'image-model-pause-20261012.json')});save(Z/'current-adopted-index-20261012.json',i)
print(json.dumps({k:p[k] for k in ['deduplicatedTargetTileCount','complete16Core4kCandidateCount','internalPassed4kCount','missingNativeTileCount','completeTilesPendingInternalReviewCount','usableSelectedCoreCount','missingNativeCoreCount','generatedNativeCount']},ensure_ascii=False))
