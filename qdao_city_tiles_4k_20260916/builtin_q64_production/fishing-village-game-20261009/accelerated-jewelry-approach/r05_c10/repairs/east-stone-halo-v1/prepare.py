from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
b=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach');d=b/'r05_c10/repairs/east-stone-halo-v1';d.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze=read(b/'migration-freeze-20261011.json');now=datetime.now(timezone.utc).isoformat()
p1=b/'r05_c10/candidate/r05_c10-4096-candidate-v2.png';p2=b/'r05_c11/candidate/r05_c11-4096-candidate-v3.png'
canvas=Image.new('RGB',(8192,4096));canvas.paste(Image.open(p1),(0,0));canvas.paste(Image.open(p2),(4096,0))
box=[3354,950,4608,2204];im=canvas.crop(box);im.save(d/'target-native.png')
im=im.convert('RGBA');im.paste((0,0,0,0),(607,70,647,860));im.save(d/'target-inpaint-native.png')
der={'tile':'r05_c10','tileLocalBox':box,'globalPixelBox':[36864+box[0],16384+box[1],36864+box[2],16384+box[3]],'sources':[{'file':str(p),'sha256':sha(p)} for p in [p1,p2]],'operation':'Unscaled native candidate paste, native crop, mechanical alpha knockout; no resized or painted content','transparentHoleNativeBox':[607,70,647,860],'nativePixelsResized':False};write(d/'target-derivation.json',der)
resume={'schemaVersion':1,'startedAtUtc':now,'updatedAtUtc':now,'authorization':'继续做完给我; 边继续做边传吧','authorizationSource':r'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json','status':'final_native_repair_in_progress','generationStopped':False,'historicalFreezePreserved':{'file':str(b/'migration-freeze-20261011.json'),'sha256':sha(b/'migration-freeze-20261011.json')},'currentCandidates':freeze['selectedCandidatePaths'],'candidateCount':6,'selectedNativeCoreCount':96,'requiredNativeCoreCount':96,'rawGeneratedImageCount':116,'missingCoreCoordinates':[],'pendingRepairs':freeze['pendingRepairs'],'firstNewOutput':None,'builtinOnly':True,'paidApiUsed':False,'gitOperationsByThisTask':False,'fixedUploadSnapshotUntouched':True,'childFailures':[{'agent':a,'receivedAtUtc':now,'error':'Fatal error: application network permission was revoked','imagegenErrorEvidence':False} for a in ['south_native','qa_first_tile']]}
write(b/'production-resume-20261012.json',resume)
p=read(b/'progress.json');p.update({'updatedAt':now,'status':resume['status'],'generationStopped':False,'productionResume':str(b/'production-resume-20261012.json'),'nextAction':'Repair r05_c10 east stone halo, finalize r05_c11v3 QA and assemble six-tile native region.'})
p['migrationCoordination']['policy']='Artwork resumed under20261012 authority; Git and upload snapshots owned only by migration thread.'
write(b/'progress.json',p)
print(str(d/'target-native.png'))

