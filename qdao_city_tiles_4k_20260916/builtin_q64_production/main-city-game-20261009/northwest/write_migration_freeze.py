"""Save the migration checkpoint without creating/reviewing artwork or changing Git."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
Z=Path(__file__).resolve().parent;WORK=Path('D:/work/image').resolve()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def inside(p):
 try: Path(p).resolve().relative_to(WORK);return True
 except ValueError: return False
def ref(p): return {'file':str(p),'sha256':sha(p)}
def write(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze=read(WORK/'MAP_MIGRATION_FREEZE_20261011.json')
assignment_path=Z.parents[1]/'acceleration-20261010/assignments.json'
assignments=read(assignment_path)
excluded=set(next(a['coordinates'] for a in assignments['assignments'] if a['id']=='city_yamen_north' and a['previousZone']=='northwest'))
allpatch=[f's{r:02}_{c:02}' for r in range(1,5) for c in range(1,5)]
tiles=[];hostcopies=[];external={};missingrefs={};rawcount=0
for row in range(1,9):
 for col in range(1,9):
  t=f'r{row:02}_c{col:02}'
  if t in excluded: continue
  d=Z/t;sel=read(d/'selection.json') if (d/'selection.json').exists() else {}
  selected=[];available=[]
  for pid in allpatch:
   native=Path(sel.get(pid,str(d/'native'/f'{pid}.png')))
   if native.is_file():
    record=native.with_suffix('.png.generation.json');g=read(record)
    entry={'id':pid,'file':str(native),'sha256':g['sha256'],'generationRecord':str(record),'explicitlySelected':pid in sel}
    available.append(entry)
    if pid in sel: selected.append(entry)
  candidates=[]
  for pp in [d/'delivery-summary.json',d/'qa/acceptance.json']:
   if pp.is_file():
    a=read(pp);c=a.get('candidate',a.get('finalCandidate'))
    if c: candidates.append({'checkpoint':ref(pp),'candidate':c,'internalQA':a.get('internalQA'),'externalQA':a.get('externalQA'),'formalAccepted':a.get('formalAccepted',False)})
  child=d/'migration-freeze-20261011.json'
  tiles.append({'tile':t,'availableNativeCount':len(available),'explicitlySelectedCount':len(selected),'selectedSources':selected,'availableSources':available,'missingLogicalPatches':[pid for pid in allpatch if pid not in {e['id'] for e in available}],'candidateRecords':candidates,'workerFreeze':ref(child) if child.is_file() else None})
for gp in list(Z.glob('r??_c??/native/*.png.generation.json'))+list(Z.glob('r??_c??/bridges/*/generation.json')):
 g=read(gp);rawcount+=1
 ev=g.get('evidence',{});host=ev.get('hostOutputPath',g.get('sourceHostFile'))
 copied=g.get('file')
 if not copied:
  probe=gp.parent/'native.png'
  if probe.is_file():copied=str(probe)
 if host:
  hostcopies.append({'originalHostFile':host,'workspaceCopy':copied,'record':str(gp),'sha256':g.get('sha256',g.get('sourceHostSha256')),'workspaceCopyExists':bool(copied and Path(copied).is_file())})
 for rr in g.get('references',[]):
  f=rr.get('file')
  if not f: continue
  p=Path(f)
  if not p.is_file():missingrefs[f]={'file':f,'recordedSHA256':rr.get('sha256'),'status':'historical_reference_unavailable; preserve original record; do not replace'}
  elif not inside(p):
   digest=sha(p);out=Z/'migration-dependencies'/(digest[:16]+'-'+p.name)
   out.parent.mkdir(parents=True,exist_ok=True)
   if not out.exists():shutil.copyfile(p,out)
   assert sha(out)==digest
   external[f]={'externalOriginal':f,'workspaceCopy':str(out),'sha256':digest,'copiedExactBytes':True}
six=Z/'joint-six-tile-review/ac2031be4f9bb37b/delivery-summary.json'
seven=Z/'r07_c04/delivery-summary.json'
savedlast=Z/'r07_c05/native/s02_03.png'
last={'file':str(savedlast),'sha256':sha(savedlast),'logicalPatch':'s02_03','savedDuringFreeze':True,'explicitlySelected':False,'qaStatus':'Not assembled or seam reviewed; no new QA started after freeze.'}
rootcheckpoint={'schemaVersion':1,'savedAtUtc':now(),'generationStoppedAtUtc':'2026-10-12T02:32:02Z','generationStopped':True,'activeCoordinate':'r07_c05/s02_03','selectedSourceCount':len(read(Z/'r07_c05/selection.json')),'lastSuccessfulOutputSaved':last,'nextMissingCoordinate':'r07_c05/s02_04','pendingRepairs':['No complete 4096 candidate yet; inspect seams after remaining sources exist.','s02_03 begins blue-strip turn near its lower edge; continue actual native geometry in row3.'],'unsavedSuccessfulOutputPaths':[],'inFlightRequests':[],'restartArtOnlyAfterMigration':True,'gitMutations':False}
ownfreeze=Z/'r07_c05/migration-freeze-20261011.json'
if not ownfreeze.exists():write(ownfreeze,rootcheckpoint)
for tileentry in tiles:
 if tileentry['tile']=='r07_c05':tileentry['workerFreeze']=ref(ownfreeze)
pending=['r05_c03','r05_c07','r07_c06']
workers=[]
for t in pending:
 f=Z/t/'migration-freeze-20261011.json'
 independent=f.is_file() and read(f).get('confirmationActor')=='root_independent_local_audit'
 workers.append({'tile':t,'freeze':ref(f) if f.is_file() else None,'acknowledgement':('independently_confirmed_by_root_after_worker_saved_output' if independent else 'saved') if f.is_file() else 'awaiting_worker_acknowledgement','inFlightStatus':read(f).get('inFlightRequests',read(f).get('inFlight',read(f).get('inFlightStatus','see worker checkpoint'))) if f.is_file() else 'not yet confirmed'})
out={'schemaVersion':1,'savedAtUtc':now(),'freezeRequestedAtUtc':freeze['requestedAtUtc'],'rootGenerationStoppedAtUtc':'2026-10-12T02:32:02Z','generationStopped':True,'newGenerationProhibited':True,'rootInFlightRequests':[],'workerCheckpoints':workers,'allWorkersAcknowledged':all(x['freeze'] for x in workers),'activeCoordinates':['r05_c03','r05_c07','r07_c05','r07_c06'],'ownedTileCount':60,'excludedCoordinates':sorted(excluded),'scopeAssignment':ref(assignment_path),'wholeZoneComplete':False,'formalAcceptedCount':0,'reviewedTileCount':7,'sixTileDelivery':ref(six),'sixTilePackage':ref(six.parent/'northwest-six-4k-tiles.zip'),'seventhTile':ref(seven),'availableNativeCoreCount':sum(t['availableNativeCount'] for t in tiles),'missingNativeCoreCount':sum(len(t['missingLogicalPatches']) for t in tiles),'storedGenerationRecords':rawcount,'tiles':tiles,'nextMissingCoordinate':'r07_c05/s02_04','pendingRepairs':{'r05_c03':'Latest worker stopped after s04_01_fix04 selected; await worker frozen QA/repair checkpoint. Previous fix03 and hybrid were rejected due geometric steps. Do not assume full acceptance.','r05_c07':'Eight selected core patches at last report; row3 not complete. Use worker checkpoint for returned in-flight output.','r07_c05':'7 native cores saved, 6 explicitly selected; remaining9 absent. Latest s02_03 saved without new QA.','r07_c06':'First row4/16 saved and hard first-row/north checks passed; s02_01 waiting west r07_c05/s02_04. Do not launch while frozen.'},'unsavedSuccessfulOutputPaths':[],'unsavedOutputScope':'Root has saved every successful returned image; worker status is separately recorded above.','externalReferencePaths':list(external.values()),'historicalMissingReferencePaths':list(missingrefs.values()),'externalHostOutputCopies':hostcopies,'externalRuntimeRequirement':'Python with Pillow and NumPy is required by mechanical assembly scripts; current bundled absolute executable path is machine-specific.','preserveAllOriginalsWorkingFilesPreviews':True,'noCleanup':True,'gitMutations':False,'gitOwner':'migration controller; do not touch .git/migration-sync-20261011','restartArtOnlyAfterMigration':True}
write(Z/'migration-freeze-20261011.json',out)
out['supervisorObservation']={'sourceThreadId':'01a10997-f575-7002-8029-c9cdf6a0e32a','finding':'Independent freeze audit observed all three children idle, last turn interrupted, with no running or in-flight requests. Followup tasks dispatched for local-save-only checkpoint acknowledgements.'}
out['existingProgressFileNote']='The freeze checkpoint takes precedence over earlier progress/continuation statuses. A progress.json write attempt returned OSError22, so existing progress files are not rewritten during migration.'
material=Z/'r05_c03/migration-freeze-20261011.json'
if material.exists():
 child=read(material)
 out['latestUnreviewedMaterialCandidate']=child.get('latestCandidate')
 out['pendingRepairs']['r05_c03']=child.get('repairBreakpoint','s04_01_fix04 selected; final hard candidate remains unreviewed after repair.')
east=Z/'r05_c07/migration-freeze-20261011.json'
if east.exists():
 out['pendingRepairs']['r05_c07']='Frozen after eight explicit selections. Last returned s03_01 saved without new QA or selection; continue only after migration. See child freeze for exact breakpoint.'
out['allWorkerStatesConfirmed']=all(x['freeze'] for x in workers)
out['allWorkersAcknowledged']=all(x['freeze'] and x['acknowledgement']=='saved' for x in workers)
out['acknowledgementNote']='r05_c03 and r07_c06 workers confirmed final checkpoint directly. Root independently confirmed r05_c07 after observing successful last-output ingestion and interrupting the remaining local-save turn; no child-authored final acknowledgement is claimed.'
out['inFlightRequests']=[] if out['allWorkerStatesConfirmed'] else None
out['state']='frozen_ready_for_migration' if out['allWorkerStatesConfirmed'] else 'frozen_awaiting_worker_save_checkpoints'
out['checkpointComplete']=out['allWorkerStatesConfirmed']
write(Z/'migration-freeze-20261011.json',out)
print(json.dumps({'freeze':str(Z/'migration-freeze-20261011.json'),'availableNativeCores':out['availableNativeCoreCount'],'missingNativeCores':out['missingNativeCoreCount'],'outsideRefsCopied':len(external),'allWorkersAcknowledged':out['allWorkersAcknowledged'],'rootInFlight':0,'rootUnsavedSuccessfulOutputs':0}))
