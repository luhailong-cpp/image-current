"""Final independent preservation audit. Do not run periodically."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import hashlib,json,shutil
B=Path(__file__).resolve().parent
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def info(p):
 p=Path(p);v={'file':str(p),'exists':p.is_file()}
 if p.is_file():
  v.update(sha256=sha(p),bytes=p.stat().st_size,lastModifiedUtc=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat())
  if p.suffix.lower()=='.png':
   with Image.open(p) as im:v['dimensions']=list(im.size)
 return v
refs=read(B/'migration-reference-inventory-20261011.json')['files']
roots=read(B/'migration-generated-outputs-20261011.json')['files']
known={}
for x in roots:known[x['sha256']]=x['workspaceCopies']
for x in refs:
 if x.get('sha256') and x.get('workspaceCopies'):known[x['sha256']]=x['workspaceCopies']
for p in (B/'native').glob('*.png'):known.setdefault(sha(p),[str(p)])
dirs={Path(x['file']).parent for x in refs if '/generated_images/' in x['file'].replace('\\','/')}
dirs.update(Path(x['original']).parent for x in roots)
cache=[];extra=B/'migration-cache-outputs-20261011'
for d in sorted(dirs):
 for p in sorted(d.glob('*.png')):
  h=sha(p);copies=known.get(h)
  if not copies:
   extra.mkdir(exist_ok=True);dst=extra/(h[:16]+'-'+p.name)
   if not dst.exists():shutil.copy2(p,dst)
   if sha(dst)!=h:raise RuntimeError(str(p))
   copies=[str(dst)];known[h]=copies
  cache.append({'original':str(p),'sha256':h,'workspaceCopies':copies,'saved':True})
cachefile=B/'migration-all-known-caches-20261011.json'
write(cachefile,{'savedAtUtc':now(),'author':'root independent filesystem audit; not child confirmation','cacheDirectories':[str(p) for p in sorted(dirs)],'files':cache,'unsavedSuccessfulOutputs':[]})
configs={
 'r02_c03':('converge-v1/r02_c03.candidate.png','converge-v1/assembly.json',['Review latest converge-v1 paving, rail and roof continuity after migration.','Reconcile south roof corrections against current r03_c03 and any west r03_c02 delta; no new adoption performed during freeze.']),
 'r02_c04':('assembly-v2/r02_c04.candidate.png','assembly-v2/r02_c04.assembly.json',['Latest joint-v2/joint.context.png is newer than standalone 4K candidate; preserve joint-v3 as well.','Review final joint context and extract/reconcile intended tile plus independent south pillar-foot delta after migration.']),
 'r05_c04':('final-v1/r05_c04.candidate.png','final-v1/assembly.json',['Review latest sand-band/repair results against final-v1 before adoption.','Preserve final-v1/north-delta.json and r04_c04.with-north-head.png for north-neighbor reconciliation.','Two prepared request files lack receipts; dispatch status cannot be established from disk. Do not treat them as successful generations.'])
}
for tile,(candidate,assembly,pending) in configs.items():
 w=B/f'work-{tile}';receipts=list((w/'receipts').glob('*.receipt.json'));requests=list((w/'receipts').glob('*.request.json'))
 outstanding=[info(p) for p in requests if not p.with_name(p.name.replace('.request.json','.receipt.json')).exists()]
 successes=sorted(receipts,key=lambda p:p.stat().st_mtime)
 v={'schemaVersion':1,'author':'/root independent filesystem evidence; child did not return a personal confirmation','savedAtUtc':now(),'generationStopped':True,'stoppedAtUtc':'2026-10-12T02:45:05Z','stopTimeMeaning':'First recorded clock after root interrupted the local freeze-only child turn; collaboration runtime subsequently listed all three children as interrupted.','activeCoordinates':[tile],'selectedCandidatePaths':[],'unadoptedLatestCompleteCandidate':info(w/candidate),'assembly':info(w/assembly),'candidateStatus':'Saved on disk; not adopted or newly visually reviewed by root during freeze.','pendingRepairs':pending,'requestsOnDisk':len(requests),'receiptsOnDisk':len(receipts),'requestsWithoutReceipt':outstanding,'lastSavedReceipt':info(successes[-1]) if successes else None,'knownInFlightGenerationCount':0,'runtimeStatus':'interrupted','unresolvedRequestDispatchStatus':len(outstanding),'inFlightCaveat':'No active child turn remains. Request files without receipts do not prove tool dispatch or in-flight work; no successful output is inferred from them.','successfulOutputPreservationInventory':str(cachefile),'unsavedSuccessfulOutputPaths':[],'externalReferencePaths':str(B/'migration-reference-inventory-20261011.json'),'gitWritesPerformed':False,'newGenerationStartedForFreeze':False,'nextMissingCoordinate':'Resume QA/reconciliation at this coordinate after migration authorization, using saved pending work.'}
 write(w/'migration-freeze-20261011.json',v)

# Embed independent worker checkpoints and finish once. Preserve the adopted index.
p=B/'migration-freeze-20261011.json';v=read(p)
v['workerFreezeCheckpoints']={tile:{'checkpoint':str(B/f'work-{tile}/migration-freeze-20261011.json'),'exists':True,'contents':read(B/f'work-{tile}/migration-freeze-20261011.json')} for tile in configs}
v['workerCheckpointsAllPresent']=True
v['workerRuntimeFinalState']={'paving_resume':'interrupted','e3_integration_resume':'interrupted','north_joint_resume':'interrupted','evidence':'collaboration.list_agents after explicit interrupt_agent calls; previous states running; root did not receive personal child confirmation.'}
v['knownInFlightGenerationCount']=0
v['unresolvedPreparedRequests']=[x for tile in configs for x in v['workerFreezeCheckpoints'][tile]['contents']['requestsWithoutReceipt']]
v['inFlightCaveat']='No active child turns or root generation calls. Two request files have no receipt; tool dispatch cannot be established from disk. All image files currently in every referenced generated-image cache are preserved.'
v['allKnownGeneratedCacheInventory']=str(cachefile)
v['counts']['complete4kCandidateCoordinatesOnDiskIncludingUnadopted']=len(v['selectedCandidatePaths'])+len(configs)
v['counts']['internallyPassedAdoptedCandidates']=6
v['finalizedForMigration']=True;v['savedAtUtc']=now();v['doNotPeriodicallyRewrite']=True
write(p,v)
local=B/'local-continuation-20261011.json';lv=read(local);lv.update(finalizedForMigration=True,workerRuntimeStatus='All three child turns interrupted; no active child turn.',knownInFlightGenerationCount=0,unresolvedPreparedRequestCount=2);write(local,lv)
print(json.dumps({'finalized':str(p),'cacheDirectories':len(dirs),'cacheOutputsPreserved':len(cache),'newCacheCopies':len(list(extra.glob('*'))) if extra.exists() else 0,'completeCandidateCoordinatesOnDisk':v['counts']['complete4kCandidateCoordinatesOnDiskIncludingUnadopted'],'adoptedCandidateCount':v['counts']['adopted4kCandidates'],'unresolvedPreparedRequests':len(v['unresolvedPreparedRequests'])},ensure_ascii=False))
