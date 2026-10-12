from pathlib import Path
import json,hashlib,runpy,shutil
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,j:Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pausepath=Z/'image-model-pause-20261012.json';archive=Z/'image-model-pause-20261012.superseded-20261013.json'
if not archive.exists():shutil.copy2(pausepath,archive)
pause=read(pausepath);pause.update({'newGenerationPaused':False,'supersededAtUtc':now,'supersededByUserClarification':'Free/included 2.5 preferred; existing builtin 2.0 allowed if unavailable. Mandatory2.5 stop revoked.','rootNextMissingPatch':'r07_c15/p44'});save(pausepath,pause)
r=read(Z/'production-resume-20261012.json');r.update({'status':'resumed_builtin_art_after_user_free_2_5_preference_clarification','generationStopped':False,'newArtworkGenerationAllowed':True,'imageModelPreference':'Free/included GPT Image2.5 preferred; builtin2.0 allowed; no paidAPI; returned actual model unknown','projectRulesSha256':sha('D:/work/image/AGENTS.md'),'modelClarificationAuthority':'D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md','modelClarificationAuthoritySha256':sha('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md'),'updatedAtUtc':now,'currentCoordinate':'r07_c15/p44 pending; then2P2 native repairs and complete assembly review','nextStep':'Continue missing cores and bounded P2 native repairs under current project rules; exclude four formally transferred north tower tiles.'});save(Z/'production-resume-20261012.json',r)
q=read(Z/'work-queue-finish-20261012.json');q.update({'updatedAt':now,'targetTiles':60,'originalZoneTiles':64,'excludedTransferredTiles':read(Z/'reserved-tiles-20261013.json')['reservedTiles'],'transferAuthority':'D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json','generationStopped':False,'imageModelPreference':r['imageModelPreference']})
for a in q['exclusiveAssignments']:
 if a['owner']=='root':a['targetTiles']=12;a['excludedTransferredTiles']=q['excludedTransferredTiles']
save(Z/'work-queue-finish-20261012.json',q)
t=Z/'r07_c15/tile-progress.json';v=read(t);v.update({'status':'native_production_resumed_missing_one_core_then2P2','generationStopped':False,'updatedAt':now,'requestedImageModel':None,'imageModelPreference':r['imageModelPreference']});save(t,v)
runpy.run_path(str(Z/'refresh_progress.py'),run_name='__main__')
