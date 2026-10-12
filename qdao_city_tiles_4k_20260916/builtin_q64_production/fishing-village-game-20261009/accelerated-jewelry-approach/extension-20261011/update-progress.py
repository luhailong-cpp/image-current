from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
b=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
old=read(b/'progress.json')
old['updatedAt']=datetime.now(timezone.utc).isoformat()
old['status']='south_extension_native_generation_in_progress'
old['originalFourCandidateCount']=4
old['originalFourPreserved']=True
old['requiredNativeCoreCount']=96
old['assignedCoordinates']=['r03_c10','r03_c11','r04_c10','r04_c11','r05_c10','r05_c11']
old['assignmentSource']=str(b.parent.parent/'acceleration-20261010/assignments.json')
old['activeExtensionCoordinates']=['r05_c10','r05_c11']
nexts=[]
for t in old['activeExtensionCoordinates']:
 p=read(b/t/'progress.json');old['tiles'][t]=p
 if p.get('nextCoordinate'):nexts.append({'tile':t,'patch':p['nextCoordinate']})
old['selectedNativeCoreCount']=64+sum(old['tiles'][t]['selectedNativeCoreCount'] for t in old['activeExtensionCoordinates'])
new_core_raw_count=sum(len(list((b/t/'native').glob('p*-v*.png'))) for t in old['activeExtensionCoordinates'])
repair_paths=set()
for t in old['activeExtensionCoordinates']:
 for pattern in ['*/native-result.png','*/repair-native.png']:
  repair_paths.update(p.resolve() for p in (b/t/'repairs').glob(pattern))
 for g in (b/t/'repairs').rglob('*.generation.json'):
  item=read(g)
  if item.get('file'):repair_paths.add(Path(item['file']).resolve())
new_repair_raw_count=len(repair_paths)
new_raw_count=new_core_raw_count+new_repair_raw_count
old['rawGeneratedImageCount']=71+new_raw_count
old['extensionRawGeneratedImageCount']=new_raw_count
old['extensionCoreVersionCount']=new_core_raw_count
old['extensionRepairRawCount']=new_repair_raw_count
old['nextCoordinates']=nexts
old['nextCoordinate']=nexts[0] if nexts else None
old['nextAction']='Complete r05_c10 and r05_c11 native detail, assemble 4096 candidates, review new inter-tile seams, and deliver six-tile region.'
old['withinRegionSeamsReviewed']=False
old['previousFourTileInternalSeamsReviewed']=True
old['formalAcceptedCount']=0
old['migrationCoordination']={'centralOwnerThread':'01a11b5e-158a-77d0-8c02-e8e503b7abe4','localGitOperationsPaused':True,'automaticGitScriptsOwnedByThisTask':[],'policy':'Continue image production only; preserve all source, preview and QA files; central migration collects new files.'}
temp=b/'progress.extension.tmp';temp.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(b/'progress.json')
handoff={'updatedAt':old['updatedAt'],'directory':str(b),'priorFourCandidatesManifest':str(b/'delivery/candidate-manifest.json'),'priorFourCandidatesIntact':True,'currentScope':old['assignedCoordinates'],'newCoordinates':old['activeExtensionCoordinates'],'status':old['status'],'selectedNativeCoreCount':old['selectedNativeCoreCount'],'requiredNativeCoreCount':96,'nextCoordinates':nexts,'productionProgress':str(b/'progress.json'),'gitOperationsByThisTask':False,'ownAutomaticGitScripts':[],'doNotRemoveFiles':True,'currentDeliveryScope':'The existing delivery manifest covers original four completed candidates; extension is tracked separately until two new candidates and seams are reviewed.'}
(b/'extension-20261011/migration-handoff.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
round_path=b/'continuation-round-20261011.json'
if round_path.exists():
    continuation=read(round_path)
    continuation['updatedAt']=old['updatedAt']
    continuation['candidateStatus']['extensionSelectedCores']=old['selectedNativeCoreCount']-64
    continuation['candidateStatus']['extensionRawImageCount']=new_raw_count
    continuation['nextCoordinates']=nexts
    round_temp=b/'continuation-round-20261011.tmp'
    round_temp.write_text(json.dumps(continuation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');round_temp.replace(round_path)
print(json.dumps({'selectedCores':old['selectedNativeCoreCount'],'required':96,'next':nexts}))
