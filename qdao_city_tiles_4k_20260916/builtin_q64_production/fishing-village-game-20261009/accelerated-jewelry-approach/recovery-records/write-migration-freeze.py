from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,re,shutil
b=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/accelerated-jewelry-approach');workspace=Path(r'D:/work/image').resolve()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
versions={'r03_c10':4,'r03_c11':2,'r04_c10':2,'r04_c11':3,'r05_c10':2,'r05_c11':3}
selected=[]
for t,v in versions.items():
 p=b/t/'candidate'/f'{t}-4096-candidate-v{v}.png'
 selected.append({'tile':t,'version':v,'file':str(p),'sha256':sha(p),'dimensions':list(Image.open(p).size),'formalAccepted':False,'stage':'saved_current_candidate_for_migration'})
gens=[];raw_by_hash={};cache_dirs=set();external_refs={};workspace_refs={}
def under(p,root):
 try:p.resolve().relative_to(root.resolve());return True
 except ValueError:return False
def values(obj):
 if isinstance(obj,dict):
  for x in obj.values():yield from values(x)
 elif isinstance(obj,list):
  for x in obj:yield from values(x)
 elif isinstance(obj,str):yield obj
for gp in b.rglob('*.generation.json'):
 try:g=read(gp)
 except (ValueError,OSError):continue
 fp=g.get('file')
 if fp and Path(fp).exists():
  rp=Path(fp)
  if rp.suffix.lower()=='.png':raw_by_hash[sha(rp)]=str(rp);gens.append({'generation':str(gp),'file':str(rp),'sha256':sha(rp)})
 refs=g.get('references',[])
 if isinstance(refs,dict):refs=[refs]
 if g.get('reference'):refs=refs+[g['reference']]
 for ref in refs:
  if not isinstance(ref,dict) or not ref.get('file'):continue
  rp=Path(ref['file']);item={'file':str(rp),'recordedSha256':ref.get('sha256'),'exists':rp.exists()}
  if not under(rp,workspace):external_refs[str(rp)]=item
  elif not under(rp,b):workspace_refs[str(rp)]=item
 for val in values(g):
  if re.match(r'^[A-Za-z]:[/\\]',val) and 'generated_images' in val:
   cp=Path(val)
   if cp.suffix.lower()=='.png' and cp.exists():cache_dirs.add(cp.parent)
# Tool receipts sometimes hold source paths only inside the output hint.
for rp in b.rglob('*.json'):
 if 'receipt' not in rp.name:continue
 try:r=read(rp)
 except (ValueError,OSError):continue
 for val in values(r):
  for match in re.finditer(r'as ([A-Za-z]:[^\r\n]+?\.png) by default',val):
   cp=Path(match.group(1))
   if cp.exists():cache_dirs.add(cp.parent)
cache_inventory=[];recovered=[]
for folder in sorted(cache_dirs):
 for p in sorted(folder.glob('*.png')):
  h=sha(p);entry={'file':str(p),'sha256':h,'savedOwnedCopy':raw_by_hash.get(h)}
  if h not in raw_by_hash:
   destdir=b/'recovery-records'/'unmatched-native-cache';destdir.mkdir(parents=True,exist_ok=True)
   dest=destdir/(folder.name+'--'+p.name)
   if not dest.exists():shutil.copy2(p,dest)
   entry['savedRecoveryCopy']=str(dest);entry['classification']='Unmatched existing task cache output preserved for migration; not selected or newly generated'
   recovered.append(entry)
  cache_inventory.append(entry)
external_backups=[]
for key,item in external_refs.items():
 p=Path(key)
 if p.exists() and p.is_file():
  h=sha(p);outdir=b/'migration-external-references';outdir.mkdir(exist_ok=True)
  dest=outdir/(h[:12]+'-'+p.name)
  if not dest.exists():shutil.copy2(p,dest)
  item.update({'sha256':h,'migrationCopy':str(dest),'migrationCopySha256':sha(dest)})
 external_backups.append(item)
write(b/'recovery-records'/'cache-output-inventory-20261011.json',{'savedAtUtc':now,'purpose':'Save returned outputs for migration, not quality re-audit','cacheFolders':[str(p) for p in sorted(cache_dirs)],'cacheFiles':cache_inventory,'unmatchedPreservedCount':len(recovered)})
qa11=b/'r05_c11/qa'
qarecords=[str(p) for p in qa11.rglob('*.json')]
outer=[{'tile':f'r03_c{c}','edge':'north','neighbor':f'r02_c{c}'} for c in [10,11]]+[{'tile':f'r05_c{c}','edge':'south','neighbor':f'r06_c{c}'} for c in [10,11]]
outer += [{'tile':f'r{r:02}_c{c}','edge':edge,'neighbor':f'r{r:02}_c{n:02}'} for r in [3,4,5] for c,edge,n in [(10,'west',9),(11,'east',12)]]
audit=b/'extension-20261011/provenance-audit.json'
old_audit=read(audit)
pending=[{'tile':'r05_c10','issue':'Short vertical lighting/texture halo boundary near local x3981 through paving at y1024..1752','evidence':str(b/'r05_c11/qa/candidate-v2/west-r2.png'),'stage':'not repaired; no new imagegen request started','nextAfterMigration':'Prepare native context crop and localized builtin repair only after user resumes art'},{'tile':'r05_c11','issue':'Latest v3 includes sand-halo-v1; final verification/adoption checkpoint incomplete at freeze','currentCandidate':str(b/'r05_c11/candidate/r05_c11-4096-candidate-v3.png'),'stage':'saved, final QA/provenance replay pending'},{'tile':'six-tile-region','issue':'Final8192x12288 assembly and cross-tile QA not finished','stage':'do not call old8192x8192 four-tile delivery a six-tile completion'}]
freeze={'schemaVersion':1,'savedAtUtc':now,'generationStoppedAtUtc':'2026-10-12T02:27:34Z','stopTimeBasis':'First UTC clock observation immediately after receiving migration-freeze instruction and dispatching stop to all children','userFreezeRequestedAtUtc':'2026-10-12T02:24:00Z','reason':'User requests migration to another computer; main controller owns Git commit/push','generationStopped':True,'doNotStartAdditionalGeneration':True,'activeCoordinates':list(versions),'selectedCandidatePaths':selected,'candidateCount':6,'candidateScope':'Six saved4096 candidates; region completion and formal acceptance are false','selectedNativeCoreCount':96,'requiredNativeCoreCount':96,'recordedRawGeneratedImageCount':116,'recoveredUnmatchedExistingCacheOutputCount':len(recovered),'formalAcceptedCount':0,'allAssignedCoreImagesPresent':True,'allAssignedRegionComplete':False,'nextMissingCoordinate':None,'missingCoreCoordinates':[],'pendingRepairs':pending,'unsavedSuccessfulOutputPaths':[],'knownSuccessfulOutputsSaved':True,'inFlightRequests':[],'inFlightStatusBasis':'No root builtin call active. All3 children were pending_init when interrupted after stop notification. Existing known successful receipts have saved owned copies; cache inventory preserves unmatched outputs.','workers':[{'agent':a,'stopSent':True,'previousStatusAtInterrupt':'pending_init','interrupted':True} for a in ['geometry_audit','qa_first_tile','south_native']],'internalChecks':{'priorFour':'completed previously; untouched','r05_c10':'v2:24internal+4north reviewed; later east halo issue remains','r05_c11':'v2:24internal and8neighbor cuts prepared/reviewed in progress; v3saved with sand patch; final check not frozen as passed','regionCrossSeams':'incomplete; outstanding c10east halo','exteriorPairsPending':outer},'lastProvenanceAudit':{'file':str(audit),'status':old_audit.get('status'),'auditedAt':old_audit.get('auditedAt'),'note':'Existing report validated45 new raw images and prior candidates, then left pending c11sand final adoption. It predates v3 and has not been rerun under freeze.'},'externalReferencePaths':external_backups,'workspaceReferencePathsOutsideOwnedZone':list(workspace_refs.values()),'toolCacheOriginals':{'inventory':str(b/'recovery-records/cache-output-inventory-20261011.json'),'requiredForArtworkMigration':False,'reason':'Saved copies or recovery copies exist inside owned zone; original tool paths in provenance are historical metadata'},'preparationInterruption':{'attemptedWork':'east-stone native target preparation before freeze','outcome':'failed locally before creating target or starting imagegen because tool store had reset and base variable was undefined','preservedScript':str(b/'recovery-records/failed-east-stone-preparation-20261011.py'),'newImagegenRequestStarted':False},'gitOperationsByThisTask':False,'migrationOwnerThread':'01a11b5e-158a-77d0-8c02-e8e503b7abe4','globalFreezeFile':str(workspace/'MAP_MIGRATION_FREEZE_20261011.json'),'resumePolicy':'Art may resume only after migration and fresh user authorization; do not run production automatically.'}
write(b/'migration-freeze-20261011.json',freeze)
p=read(b/'progress.json')
p.update({'updatedAt':now,'status':'migration_frozen_incomplete_region','generationStopped':True,'candidateCount':6,'completeCandidateCount':6,'completeCandidateCountDefinition':'saved full4096 canvases; not whole-region completion or formal acceptance','selectedNativeCoreCount':96,'requiredNativeCoreCount':96,'rawGeneratedImageCount':116,'nextCoordinate':None,'nextCoordinates':[],'formalAcceptedCount':0,'withinRegionSeamsReviewed':False,'externalRegionSeamsChecked':False,'exteriorNeighborPairs':outer,'nextAction':'Migration freeze: do not generate. Resume pending repairs, latest candidate verification, and six-tile assembly only after user authorizes art again.','migrationFreeze':str(b/'migration-freeze-20261011.json'),'currentAdoptedCandidates':selected,'pendingRepairs':pending})
for s in selected:
 p['tiles'][s['tile']].update({'candidate':s['file'],'candidateSha256':s['sha256'],'dimensions':s['dimensions'],'formalAccepted':False})
p['migrationCoordination']['policy']='Art frozen. No Git operations in this task; main controller owns commit/push and migration.'
write(b/'progress.json',p)
handoff={'savedAtUtc':now,'status':'migration_frozen_incomplete_region','freezeManifest':str(b/'migration-freeze-20261011.json'),'selectedCandidatePaths':selected,'candidateCount':6,'selectedNativeCoreCount':96,'recordedRawGeneratedImageCount':116,'allAssignedRegionComplete':False,'formalAcceptedCount':0,'remainingCoreCoordinates':[],'pendingRepairs':pending,'generationStopped':True,'inFlightRequests':[],'unsavedSuccessfulOutputPaths':[],'externalReferenceBackups':external_backups,'gitOperationsByThisTask':False}
write(b/'extension-20261011/migration-handoff.json',handoff)
print(json.dumps({'freeze':str(b/'migration-freeze-20261011.json'),'candidates':[(s['tile'],s['version'],s['sha256']) for s in selected],'registeredRawRecords':len(gens),'cacheFiles':len(cache_inventory),'unmatchedCachePreserved':len(recovered),'externalReferenceBackups':len(external_backups),'workspaceReferencesOutsideOwnedZone':len(workspace_refs),'generationStopped':True,'inFlightRequests':[]}))

