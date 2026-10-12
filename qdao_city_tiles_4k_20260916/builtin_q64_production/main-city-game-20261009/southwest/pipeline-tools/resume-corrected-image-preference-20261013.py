from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil,sys
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
evidence=[]
for src,name in [(Path('D:/work/image/AGENTS.md'),'project-root-AGENTS.corrected-free-preference-20261013.md'),(Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md'),'IMAGE_MODEL_REQUIREMENT.corrected-free-preference-20261013.md')]:
 dst=B/'pipeline-tools'/name;assert not dst.exists();shutil.copy2(src,dst);assert sha(dst)==sha(src);evidence.append({'source':str(src),'sha256':sha(src),'preservedCopy':str(dst),'fullyReadByRoot':True})
ack={'recordedAtUtc':now,'userCorrection':'Prefer GPT Image2.5 through free/included route; if unavailable, existing builtin2.0 allowed. Prior mandatory2.5 stop revoked as coordinator misunderstanding.','evidence':evidence,'existingBuiltinAllowed':True,'stopForMissing25SelectorOrMetadata':False,'paidApiAllowed':False,'actualModel':'not returned; do not infer from historical target config','preserveOldGateFilesAsHistorical':True,'noWholeSaleRegeneration':True,'gitOperationsAllowed':False,'rootLane':'col6 rows9-16','currentFrontier':'r13_c06:p01_03'}
out=B/'pipeline-tools/corrected-image-preference-resume-20261013.json';assert not out.exists();atomic_json(out,ack)
p=read(B/'progress.json');p.update(updatedAtUtc=now,status='native_production_resumed_under_corrected_free_image_preference',currentStage='native_coverage_and_targeted_repairs',productionInProgress=True,generationStopped=False,holdNewImageGeneration=False,productionLines=4,imageGenerationInFlight=False,rootImageGenerationInFlight=False,inFlightStatus='parallel_production_resumed',networkBlocked=False,networkPermissionStatus='Normal tools being used under resumed authorization; prior actual errors preserved. No paidAPI or bypass.',activeTile='r13_c06',activeCoordinate='r13_c06:p01_03',activeImagePolicy=str(out),requestedImageModelPreference='Free/included GPT Image2.5 preferred; builtin2.0 allowed if unavailable; actual tool model undisclosed',requestedExactImageModel=None,localQaPhaseComplete=True,nextStep='Continue only missing native slots and necessary targeted native repairs, save actual outputs, then review all64 tiles and shared edges. Do not pause over missing model selector/metadata.',finalCityComplete=False)
p['workerStatus'].update(reportedAtUtc=now,activeWorkers=['/root','/root/sw_left_resume_20261012b','/root/sw_right_resume_20261012b','/root/sw_col5_resume_20261012b'],activeGenerationWorkers=['root','sw_left_resume_20261012b','sw_right_resume_20261012b','sw_col5_resume_20261012b'],activeGenerationTiles=['r13_c06','r09_c03','r10_c08','r15_c05'],activeReviewWorkers=[],productionLines=4,individualWorkerGenerationInFlight='Assignments resumed; individual calls tracked by actual receipts.',supportActivities='Corrected free-image preference explicitly revokes forced2.5 pause. Existing builtin authorized, actualmodel unreturned; saved native QA queues guide necessary repairs.')
atomic_json(B/'progress.json',p)
src=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png')
dst=B/'r13_c06/pipeline/guides/approved-geometry-context-20261013-v01.png';assert not dst.exists()
Image.open(src).convert('RGB').crop((375,900,500,1000)).resize((750,600),Image.Resampling.NEAREST).save(dst)
atomic_json(Path(str(dst)+'.derivation.json'),{'file':str(dst),'sha256':sha(dst),'source':str(src),'sourceSha256':sha(src),'sourceCrop':[375,900,500,1000],'operation':'nearest-neighbor enlargement for approved coarse geometry inspection only','guideOnly':True,'gameArt':False})
print(json.dumps({'resumeAck':str(out),'geometryGuide':str(dst),'newImageCalls':0},ensure_ascii=False))
