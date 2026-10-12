from native_work import *
import re, sys
stamp=now()
records=[read(f) for f in sorted((ZONE/'native').glob('*.png.generation.json'))]
byid={r['id']:r for r in records}
selections={f.stem[10:]:read(f) for f in sorted(ZONE.glob('selection-r??_c??.json'))}
bases={re.sub(r'_v\d+$','',r['id']) for r in records if re.fullmatch(r'r\d{2}_c\d{2}_p\d{2}_\d{2}(?:_v\d+)?',r['id'])}
original_excluded={'r01_c13','r01_c14','r02_c13','r02_c14'}
split_file=Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json')
split=read(split_file)
transferred={t for b in split['batches'] if b.get('owner')=='01a1216d-6907-7641-b5b1-a9c29f365c4c' and b.get('status')=='allocated_root_reserved' for t in b['tiles']}
excluded=original_excluded|transferred
owned_count=49-len(excluded); target_cores=owned_count*16
bases={b for b in bases if b[:7] not in excluded}
inventory=[];complete=[];passed=[];candidates=[];selected=[]
for tr in range(1,8):
 for tc in range(8,15):
  tid=f'r{tr:02d}_c{tc:02d}'
  if tid in excluded:continue
  s=selections.get(tid,{'cores':[[None]*4 for _ in range(4)]})
  ids=[v for row in s['cores'] for v in row if v];selected+=ids
  chosen={re.sub(r'_v\d+$','',v) for v in ids}
  coords=[f'{tid}_p{r:02d}_{c:02d}' for r in range(1,5) for c in range(1,5)]
  candidate=Path(s.get('candidatePath',ZONE/'tiles'/f'{tid}.png'))
  dp=Path(s.get('derivationPath',str(candidate)+'.derivation.json'));d=read(dp) if dp.exists() else {}
  full=len(ids)==16 and dp.exists();internal=full and str(d.get('internalReview','')).startswith('passed')
  if full:complete.append(tid);candidates.append({'tileId':tid,'file':str(candidate),'sha256':d.get('sha256'),'internalReview':d.get('internalReview'),'formalAccepted':False})
  if internal:passed.append(tid)
  inventory.append({'tileId':tid,'selectedCoreCount':len(ids),'selectedCoreIds':ids,'selectedFiles':[byid[i]['file'] for i in ids],'completeNativeCoverage':full,'internalPassed':internal,'formalAccepted':False,'missingGeneratedCoordinates':[c for c in coords if c not in bases],'unselectedCoordinates':[c for c in coords if c not in chosen],'pendingIssues':s.get('pendingIssues',[])+s.get('pendingNativeRepairs',[])})
ip=ZONE/'qa/production-inventory-20261012.json'
summary={'ownedTileCount':owned_count,'ownedTarget4kCount':owned_count,'ownedRemainingTarget4kCount':owned_count,'targetCoreCoordinates':target_cores,'generatedNativeCount':len(records),'generatedCoreCoordinateCount':len(bases),'selectedCoreCoordinateCount':len(selected),'fullyCovered4kCount':len(complete),'internalPassed4kCount':len(passed),'formalAcceptedCount':0,'missingFullCoverage4kCount':owned_count-len(complete),'nativeIncompleteOwnedTileCount':sum(t['selectedCoreCount']<16 for t in inventory),'fullCandidatePendingRepairOrQACount':len(complete)-len(passed),'fullCandidatePendingRepairOrQAIds':[t for t in complete if t not in passed],'allOwnedTilesPainted':len(complete)==owned_count,'countScope':f'{owned_count} currently owned northeast tiles; transferred coordinates excluded, not counted as completion','missingGeneratedCoreCoordinates':target_cores-len(bases),'missingSelectedCoreCoordinates':target_cores-len(selected),'previousOwnedTileCount':45,'transferred20261013':sorted(transferred),'delegatedElsewhere':sorted(excluded),'allocationManifest':str(split_file)}
write(ip,{'updatedAtUtc':stamp,**summary,'excludedElsewhere':sorted(excluded),'tileInventory':inventory})
rp=ZONE/'production-resume-20261012.json'
resume=read(rp) if rp.exists() else {'schemaVersion':1,'resumedAtUtc':stamp,'authorizationFile':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json','userAuthorization':'边继续做边传吧','historicalFreezeUnchanged':True,'historicalFreezeSha256':sha(ZONE/'migration-freeze-20261011.json'),'historicalBaseline':read(ZONE/'migration-freeze-20261011.json')['coverage'],'firstNewOutput':None,'newOutputs':[]}
new_identifiers=list(dict.fromkeys([*sys.argv[1:],*[r['id'] for r in records if r.get('generatedAt','')>=resume['resumedAtUtc']]]))
if new_identifiers:
 for ident in new_identifiers:
  r=byid[ident];entry={k:r[k] for k in ('id','file','sha256','generatedAt','nativeWidth','nativeHeight','prompt','references','evidence','status')}
  if not resume['firstNewOutput']:resume['firstNewOutput']=entry
  if ident not in [x['id'] for x in resume['newOutputs']]:resume['newOutputs'].append(entry)
for entry in resume['newOutputs']:
 if entry['id'] in byid:entry['status']=byid[entry['id']].get('status');entry['internalSeams']=byid[entry['id']].get('internalSeams');entry['externalSeams']=byid[entry['id']].get('externalSeams')
if resume['firstNewOutput'] and resume['firstNewOutput']['id'] in byid:resume['firstNewOutput']['status']=byid[resume['firstNewOutput']['id']].get('status')
resume.update(updatedAtUtc=stamp,status='art_production_resumed_during_fixed_snapshot_upload',generationStopped=False,newArtworkGenerationAllowed=True,coverage=summary,inventory=str(ip),currentSelections=[str(ZONE/f'selection-{t}.json') for t in selections if t not in excluded],completeCandidates=candidates,activeCoordinates=['r03_c09','r04_c10','r05_c11','r06_c12','r06_c14'],nextCoordinates={'root':'r03_c09','west':'r04_c10','repair':'r06_c12; r05_c11 residual QA held for later concentrated repair','southeast':'r06_c14'},internalStage='Inspect new native cores, joins and crossings only; retain prior passes.',adjacentStage='Available individual native core joins first; full tile boundaries after coverage; formal acceptance still pending.',builtinOnly=True,actualModel=None,actualQuality=None,submittedModel=None,submittedQuality=None,gitActionsAllowed=False)
write(rp,resume)
for name in ('progress.json','handoff.json'):
 p=ZONE/name;d=read(p);d.update(**summary,status=resume['status'],updatedAtUtc=stamp,generationStopped=False,productionResume=str(rp),continuationInventory=str(ip),activeTiles=resume['activeCoordinates'],currentTile='r03_c10',currentPatch='current selection and generation records are authoritative',inFlightStatus='production active; per-worker generation requests reported separately',nextStep='Continue latest saved candidates and exact native neighboring coordinates; retain historical migration evidence.',nextAction='Continue artwork while the independent upload snapshot transfers.',finishedInternalCandidates=[c['file'] for c in candidates if c['tileId'] in passed],pixelCoveredCandidates=[c['file'] for c in candidates],tileSummary={t['tileId']:{'coreCoverage':t['selectedCoreCount'],'missingCores':16-t['selectedCoreCount'],'internalPassed':t['internalPassed'],'pendingIssues':t['pendingIssues']} for t in inventory})
 d.setdefault('legacyPreReconciliationCounts20261013',{k:d.get(k) for k in ('generatedNativeFiles','generatedCoreCoordinates','selectedCoreCoordinates','completeNativeCoverageTiles','internalPassedTiles','missingFullCoverageTiles','complete4kCount')})
 d.update(generatedNativeFiles=len(records),generatedCoreCoordinates=len(bases),selectedCoreCoordinates=len(selected),completeNativeCoverageTiles=len(complete),internalPassedTiles=passed,missingFullCoverageTiles=owned_count-len(complete),complete4kCount=len(passed),formalAcceptedTiles=0,currentTile='r03_c09',currentCoordinate='see selected cores and per-worker checkpoint',inventory=str(ip),pausedIncompleteTiles=[],complete4kCountDefinition='internally passed candidates only; not formal full-map acceptance')
 d.pop('inFlightImagegen',None);write(p,d)
print(json.dumps({'coverage':summary,'firstNewOutput':resume['firstNewOutput']['id'] if resume['firstNewOutput'] else None,'freezeUnchanged':sha(ZONE/'migration-freeze-20261011.json')==resume['historicalFreezeSha256']}))
