from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
b=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
doc=Path(r'D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md');p=b/'progress.json';before=sha(p);progress=read(p);summary=b/'resume-20261012/production-summary.json';s=read(summary)
assert s['localArtProductionComplete'] and len(s['tiles'])==6 and not progress['pendingRepairs']
now=datetime.now(timezone.utc).isoformat();dest=b/'image-model-requirement-20261012.json';assert not dest.exists()
policy={'recordedAtUtc':now,'sourceDocument':str(doc),'sourceDocumentSha256':sha(doc),'requestedImageModel':'GPT Image 2.5','appliesTo':'Every future image generation and generative image edit/repair, including after machine migration.','verifiedSelectableRoute':None,'verifiedActualModel':None,'newGenerationAllowed':False,'newGenerationGateReason':'Currently exposed builtin route cannot explicitly select or independently verify GPT Image 2.5.','unspecifiedBuiltinRoutePermitted':False,'paidApiAuthorized':False,'routeInvestigationRequestedNow':False,'existingOutputsPreserved':True,'existingActualModelQualityRemainUnknown':True,'localArtProductionComplete':True,'localMissingCoreCoordinates':[],'localPausedGenerationTasks':[],'localPausedGenerationTaskReason':'Six assigned tiles already completed before this requirement; no current local missing image task is being relabeled complete.','exteriorReviewPending':s['exteriorReviewPending'],'exteriorSeamsPending':s['exteriorSeamsPending'],'externalMissingGenerationScope':'Neighbor images owned by other map tasks; not counted as completed by this task.','completedDelivery':{'summary':str(summary),'summarySha256':sha(summary),'region':s['region'],'generationCounts':s['generationCounts']},'progressBeforeSha256':before,'newImageCallsSinceInstruction':0,'gitOperationsByThisTask':False,'fixedUploadSnapshotUntouched':True}
write(dest,policy)
progress['updatedAt']=now;progress['imageGenerationPolicy']={'record':str(dest),'recordSha256':sha(dest),'sourceDocument':str(doc),'requestedModel':'GPT Image 2.5','verifiedRoute':None,'newGenerationAllowed':False,'paidApiAuthorized':False,'existingOutputsPreserved':True};progress['newGenerationPausedForModelRequirement']=True;progress['pausedLocalMissingGenerationTasks']=[]
write(p,progress)
assert read(p)['imageGenerationPolicy']['recordSha256']==sha(dest)
print(json.dumps({'policyRecord':str(dest),'newImageCalls':0,'localMissingImageTasks':0,'externalBoundaryPairsPending':len(s['exteriorSeamsPending']),'completedDeliveryPreserved':sha(summary)==policy['completedDelivery']['summarySha256']}))
