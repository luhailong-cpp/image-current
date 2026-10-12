"""Migration freeze only: retain successful files, inventory references, update status; no art or Git."""
import sys,json,hashlib,shutil,os,re
from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parent
WORKSPACE=Path('D:/work/image')
HOST=Path('C:/Users/luyua/.codex/generated_images/01a12554-ab3d-7da1-b30e-6bc589e53523')
OUT=ROOT/'migration-preserved-external-20261011'
STOP='2026-10-12T02:29:24Z'
def sha(f):
 h=hashlib.sha256()
 with Path(f).open('rb') as a:
  for b in iter(lambda:a.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def now():return datetime.now(timezone.utc).isoformat()
def inside(f,base):
 try:Path(f).resolve().relative_to(base.resolve());return True
 except ValueError:return False
def save_new(f,d):
 f=Path(f);assert inside(f,ROOT);f.parent.mkdir(parents=True,exist_ok=True)
 with f.open('x',encoding='utf-8') as h:json.dump(d,h,ensure_ascii=False,indent=2)
# Metadata scan only, not a new image-quality audit.
index={};external=set();media={'.png','.jpg','.jpeg','.webp','.gif','.tif','.tiff'}
docs=list(ROOT.rglob('*.json'))
def walk(v):
 if isinstance(v,dict):
  f=v.get('file');s=v.get('sha256')
  if isinstance(f,str) and isinstance(s,str) and re.fullmatch('[a-fA-F0-9]{64}',s):
   p=Path(f)
   if inside(p,ROOT) and p.is_file():index.setdefault(s.lower(),set()).add(str(p))
  for z in v.values():walk(z)
 elif isinstance(v,list):
  for z in v:walk(z)
 elif isinstance(v,str) and len(v)<1500 and re.match(r'^[A-Za-z]:[\\/]',v):
  try:
   p=Path(v)
   if p.suffix.lower() in media and not inside(p,WORKSPACE) and p.is_file():external.add(str(p.resolve()))
  except OSError:pass
for f in docs:
 try:walk(read(f))
 except (UnicodeError,json.JSONDecodeError,OSError):pass
for f in HOST.glob('*.png'):external.add(str(f.resolve()))
# Raw copies are normally indexed by generation sidecars. Size fallback finds legacy copies.
sizeindex={}
for f in ROOT.rglob('*'):
 if f.is_file() and f.suffix.lower() in media:sizeindex.setdefault(f.stat().st_size,[]).append(f)
hashcache={};refs=[];newcopies=[]
for name in sorted(external):
 f=Path(name);digest=sha(f);equivalent=None
 for target in sorted(index.get(digest,set())):
  q=Path(target);qs=hashcache.setdefault(str(q),sha(q))
  if qs==digest:equivalent=q;break
 if equivalent is None:
  for q in sizeindex.get(f.stat().st_size,[]):
   qs=hashcache.setdefault(str(q),sha(q))
   if qs==digest:equivalent=q;break
 copied=False
 if equivalent is None:
  OUT.mkdir(exist_ok=True);equivalent=OUT/(digest[:12]+'-'+f.name);assert not equivalent.exists()
  shutil.copy2(f,equivalent);assert sha(equivalent)==digest;copied=True
  newcopies.append({'original':str(f),'savedWorkspaceCopy':str(equivalent),'sha256':digest,'selectedForArt':False,'classification':'previous external success retained for migration, adoption unchanged'})
 refs.append({'originalExternalPath':str(f),'workspaceEquivalent':str(equivalent),'workspaceRelativePath':str(equivalent.relative_to(WORKSPACE)),'sha256':digest,'copiedDuringFreeze':copied,'originalPreserved':f.exists(),'mustCarryOriginalExternalSeparately':False})
inventory=ROOT/'migration-external-references-20261011.json'
save_new(inventory,{'savedAtUtc':now(),'method':'Existing metadata/hash and exact-byte checks only; no visual re-review','externalFilesChecked':len(refs),'newCopiesCreated':len(newcopies),'references':refs,'newCopies':newcopies,'remainingExternalOnlyFiles':[],'softwareDependency':'Python/Pillow/numpy runtime is not artwork; reinstall compatible tools on destination as needed. No runtime directory copy required.'})
delivery=read(ROOT/'delivery-20261011-v2/delivery-manifest.json');roundstate=read(ROOT/'continuation-round-20261011.json')
adopted=[]
for t in delivery['tiles']:
 f=Path(t['candidate']);assert f.is_file() and sha(f)==t['sha256']
 adopted.append({'coordinate':t['tile'],'canonicalAdoptedFile':str(f),'workspaceRelativePath':str(f.relative_to(WORKSPACE)),'sha256':t['sha256'],'pixels':[4096,4096],'sourceCandidateAlias':t['sourceCandidate'],'assembly':t['assembly'],'review':t['review'],'formalAccepted':False})
continuationraw=[]
for f in (ROOT/'continuation-20261011').glob('*/raw-*.png.generation.json'):
 d=read(f);q=Path(d['file']);assert q.exists() and sha(q)==d['sha256']
 continuationraw.append({'file':str(q),'sha256':d['sha256'],'metadata':str(f),'hostSource':d.get('hostSource'),'saved':True})
assert len(continuationraw)==12
child=ROOT/'continuation-20261011/assignment-neighbor-audit-freeze-20261011-8431c6a2.json';assert child.exists()
snapshot={'schemaVersion':1,'savedAtUtc':now(),'requestedAtUtc':'2026-10-12T02:24:00Z','stopAcknowledgedAndQuiescenceVerifiedAtUtc':STOP,'stopAcknowledgedLocal':'2026-10-11T22:29:24-04:00','localTimezone':'America/New_York','reason':'User requests migration freeze and transfer to another computer; root migration controller owns commit/push.','status':'frozen_for_migration_no_art_in_flight','generationStopped':True,'newGenerationRequestsSinceResumeMessage':0,'inFlightGenerationRequests':[],'inFlightGenerationCount':0,'activeCoordinates':['r03_c04','r03_c05','r04_c04','r04_c05'],'assignmentTileTarget':4,'assignmentCoreTarget':64,'scopeExpanded':False,'selectedCandidatePaths':[x['canonicalAdoptedFile'] for x in adopted],'currentUniqueAdoptedCandidates':adopted,'completeCandidateCount':4,'coveredCoreCount':64,'missingAssignedTiles':[],'missingAssignedCoreCoordinates':[],'nextMissingCoordinate':None,'internalFullyPassedTileCount':0,'formalAcceptedCount':0,'stageDisclosure':'4 complete composite candidates/64 covered cores; internal residual and adjacent seam work remains; not full-zone formal completion.','pendingRepairs':delivery['remainingWork'],'repairResumeBase':str(ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png'),'repairBreakpoints':{'r03_c05':['D1 roof phase row near tile y909,x0..2160','D4 thin duplicate row near tile y2960,x1900..4096; retain row trial raw outputs, do not adopt ghosted return','D5 gold joint; trial not selected','West E1 material step/E2 eave mismatch'],'r03_c04':['Left roof returns at tile boxes[583,1008,943,1218]and[903,1008,1278,1218]'],'r04_c04':['Minor rail-face rectangular material residual'],'r04_c05':['Minor internal tone/floor line residuals','Inherited south segment4 green blur near lion foot']},'boundaryStages':{'r03_c05_to_r04_c05':'4 repaired segments locally viewed and independently reconstructed exactly; minor material residuals retained','r03_c04_to_r03_c05':'West/east segment3 tone and segment4 eave mismatch remain','otherReviewedAssignedBoundaries':'Use preserved prior QA reports; no re-review during freeze','unavailableOuterNeighborCoordinates':['r02_c04','r02_c05','r03_c03','r04_c03','r03_c06','r04_c06'],'unavailableOuterNativeSegmentCount':24},'unsavedSuccessfulOutputPaths':[],'unsavedSuccessfulOutputCount':0,'knownContinuationRawSuccessCount':len(continuationraw),'knownContinuationRawOutputs':continuationraw,'newlyPreservedExternalOutputs':newcopies,'externalReferenceInventory':str(inventory),'externalReferencePaths':[r['originalExternalPath'] for r in refs],'externalFilesStillRequiringSeparateCopy':[],'mustCarryWorkspaceDirectories':[str(ROOT)],'absolutePathRemappingNeededOnDestination':True,'pathRemappingNote':'All original native outputs and external media references have matching workspace copies listed in migration-external-references-20261011.json. If destination drive/root changes, use recorded workspace-relative paths and remap provenance references; do not redraw merely because old absolute paths differ.','childTasks':[{'name':'/root/boundary_audit','stopped':True,'inFlightRequests':0,'unsavedSuccessfulOutputs':0,'freezeAudit':str(child)}],'allChildTasksStopped':True,'gitOperations':0,'filesDeleted':0,'adoptionChangedDuringFreeze':False,'rootFreezeDirective':str(WORKSPACE/'MAP_MIGRATION_FREEZE_20261011.json'),'migrationOwnerThread':'01a11b5e-158a-77d0-8c02-e8e503b7abe4','resumePolicy':'Do not restart artwork automatically; resume only after migration and explicit renewed instruction.'}
freeze=ROOT/'migration-freeze-20261011.json';save_new(freeze,snapshot)
# Update current status only; retain historical adopted files, selection, raws, in-process drafts and previews.
for filename in ['progress.json','local-continuation-20261011.json','continuation-round-20261011.json']:
 f=ROOT/filename;d=read(f);prior=d.get('status');d.update({'status':'frozen_for_migration_no_art_in_flight','statusBeforeMigrationFreeze':prior,'updatedAt':now(),'generationStopped':True,'inFlightGenerationCount':0,'unsavedSuccessfulOutputCount':0,'migrationFreezeRecord':str(freeze),'currentUniqueAdoptedCandidates':adopted,'candidateCount':4,'formalAcceptedCount':0,'nextStep':'Migration freeze. No new image generation or repair until explicitly resumed after transfer.','gitOperationsDuringFreeze':0})
 tmp=ROOT/(filename+'.freeze-writing');assert not tmp.exists()
 with tmp.open('x',encoding='utf-8') as h:json.dump(d,h,ensure_ascii=False,indent=2)
 os.replace(tmp,f)
print(json.dumps({'freeze':str(freeze),'generationStopped':True,'inFlight':0,'unsavedSuccesses':0,'adoptedCandidates':4,'externalReferencesChecked':len(refs),'newExternalCopies':len(newcopies),'continuationRawSuccessesSaved':12,'gitOperations':0}))

