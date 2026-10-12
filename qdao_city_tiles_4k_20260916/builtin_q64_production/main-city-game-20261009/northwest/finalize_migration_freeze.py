from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,runpy
Z=Path(__file__).resolve().parent;D=Z/'r05_c07'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
record=read(D/'native/s03_01.png.generation.json')
native=Path(record['file']);host=Path(record['evidence']['hostOutputPath'])
assert sha(native)==sha(host)==record['sha256']
assert sha(record['evidence']['receipt'])==record['evidence']['receiptSha256']
selection=read(D/'selection.json')
raw=list((D/'native').glob('*.png.generation.json'))
refs=[]
for f in raw:
 r=read(f);refs.append({'hostOutputPath':r['evidence']['hostOutputPath'],'workspaceCopy':r['file'],'sha256':r['sha256'],'generationRecord':str(f)})
logical=sorted({read(f)['logicalPatch'] for f in raw})
allids=[f's{r:02}_{c:02}' for r in range(1,5) for c in range(1,5)]
f=D/'migration-freeze-20261011.json'
assert not f.exists(),'Do not overwrite a child checkpoint if it appeared concurrently.'
state={'schemaVersion':1,'tile':'r05_c07','savedAtUtc':datetime.now(timezone.utc).isoformat(),'generationStopped':True,'confirmationActor':'root_independent_local_audit','auditBasis':['Worker stated no in-flight generation and last successful s03_01 needed saving.','Read-thread status showed s03_01 receipt written and ingest command completed successfully with exit0; last command was a completed read of selection.json.','Root observed saved s03_01 native, generation record and receipt and compared native/cache SHA256 exactly.','Root interrupted remaining worker turn before writing this independent checkpoint; no new generation or QA was started.'],'childAuthoredFinalAcknowledgement':False,'inFlight':{'imageGeneration':False,'shellCommands':False,'functionsExecCells':False,'pendingReceiptIngest':False,'knownUnreturnedRequests':[]},'unsavedSuccessfulOutputs':[],'selectedCount':len(selection),'selectionFile':str(D/'selection.json'),'selectionSha256':sha(D/'selection.json'),'selected':selection,'savedNativeVersionCount':len(raw),'availableLogicalPatches':logical,'missingPatches':[i for i in allids if i not in logical],'lastSuccessfulOutput':{'file':str(native),'sha256':sha(native),'hostOutputPath':str(host),'hostHashMatchesExactly':True,'explicitlySelected':False,'qaStatus':'not yet inspected or assembled after freeze','generationRecord':str(D/'native/s03_01.png.generation.json')},'nextMissingCoordinate':'r05_c07/s03_02','resumeBreakpoint':'s03_01 has been saved only. When migration is explicitly resumed, inspect it before explicit selection and before generating s03_02. No full4096 candidate or final33 seam QA exists.','outsideWorkspaceHostOutputs':refs,'outsideWorkspaceArtworkReferencesRequired':[],'preserveAllArtworkPreviewsRequestsReceipts':True,'gitMutations':False,'restartArtOnlyAfterMigration':True}
f.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
runpy.run_path(str(Z/'write_migration_freeze.py'),run_name='__main__')
root=read(Z/'migration-freeze-20261011.json')
assert root['checkpointComplete'] and root['state']=='frozen_ready_for_migration'
pins=[]
for tile in root['tiles']:
 v=tile.get('workerFreeze')
 if v:pins.append(v)
for worker in root['workerCheckpoints']:pins.append(worker['freeze'])
for v in pins:assert sha(v['file'])==v['sha256']
print(json.dumps({'rootFreeze':str(Z/'migration-freeze-20261011.json'),'rootFreezeSHA256':sha(Z/'migration-freeze-20261011.json'),'allCurrentWorkerPinsVerified':len(pins),'availableNativeCoreCount':root['availableNativeCoreCount'],'missingNativeCoreCount':root['missingNativeCoreCount'],'inFlight':root['inFlightRequests'],'checkpointComplete':root['checkpointComplete']}))
