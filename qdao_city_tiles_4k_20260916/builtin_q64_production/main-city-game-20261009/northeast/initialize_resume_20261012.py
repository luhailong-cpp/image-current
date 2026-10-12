from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
Z=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,j:Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
auth=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
f=Z/'migration-freeze-20261011.json';freeze=read(f);progress=read(Z/'progress.json')
assignments=[{'tile':'r07_c15','owner':'root'},{'tile':'r07_c16','owner':'east_tile_resume','initialDependency':'r07_c15/p14'},{'tile':'r08_c15','owner':'native_quality','initialDependency':'r07_c15/p41 + r08_c14/p14'},{'tile':'r08_c16','owner':'root after r07_c15 completion','initialDependency':'r07_c16/p41 + r08_c15/p14'}]
record={'schemaVersion':1,'resumedAtUtc':datetime.now(timezone.utc).isoformat(),'authority':str(auth),'authoritySha256':sha(auth),'userAuthorization':'边继续做边传吧；继续','status':'resumed_native_production','historicalFreeze':str(f),'historicalFreezeSha256':sha(f),'freezeUnmodified':True,'generationStopped':False,'newArtworkGenerationAllowed':True,'uploadFixedSnapshotIndependent':True,'initialCandidateCount':8,'initialInternalPassedCount':8,'initialConnectedReviewedCount':8,'initialRemainingTiles':56,'firstNewOutput':None,'currentCoordinate':'r07_c15/p11-v20261012','assignments':assignments,'currentSelectedCandidates':freeze['selectedCandidatePaths'],'pendingRepairsAtResume':freeze['pendingRepairs'],'unsavedSuccessfulOutputPathsAtResume':freeze['unsavedSuccessfulOutputPaths'],'inflightAtResume':freeze['inflightRequests'],'excludedAcceleratedMainCityCoordinates':['r03_c04','r03_c05','r04_c04','r04_c05'],'exclusionOverlapsNortheast':False,'builtinOnly':True,'paidApiAllowed':False,'actualImageModel':None,'actualImageQuality':None,'userRequestedAgentModel':'gpt-6.1-sol','userRequestedReasoningEffort':'ultra','gitMutationsAllowed':False,'preserveOriginalsAndPreviews':True,'imageFilenameVersion':'v20261012','nextStep':'Generate adjacent group rows7-8 columns15-16 using verified current west/north native boundaries','errors':[]}
out=Z/'production-resume-20261012.json';assert not out.exists();save(out,record)
save(Z/'work-queue-20261012.json',{'createdAt':record['resumedAtUtc'],'authority':str(auth),'assignments':assignments,'group':['r07_c15','r07_c16','r08_c15','r08_c16'],'noOverlappingOwners':True})
progress.update({'status':'resumed_native_generation_during_snapshot_upload','generationStopped':False,'productionResume':str(out),'nextStep':record['nextStep'],'workQueue':str(Z/'work-queue-20261012.json')});save(Z/'progress.json',progress)
save(Z/'r07_c15/tile-progress.json',{'tile':'r07_c15','status':'native_generation_in_progress','selectedCoreCount':0,'completeCandidateCount':0,'internalPassed4kCount':0,'formalAcceptedCount':0,'nextPatch':'p11','inflightGeneration':'p11-v20261012','actualModel':None,'actualQuality':None})
save(Z/'current-adopted-index-20261012.json',{'updatedAt':record['resumedAtUtc'],'candidates':freeze['selectedCandidatePaths'],'nativeSelections':{},'resume':str(out),'newOutputCount':0})
print(json.dumps({'resume':str(out),'active':'r07_c15/p11-v20261012','missingCoreCount':896}))

