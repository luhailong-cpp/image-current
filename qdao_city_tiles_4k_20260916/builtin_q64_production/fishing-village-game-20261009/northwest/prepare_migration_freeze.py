"""Preserve migration evidence only; no generation, composition, QA or Git writes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, re

B=Path(__file__).resolve().parent
WORKSPACE=Path('D:/work/image')
GENERATED=Path('C:/Users/luyua/.codex/generated_images/01a1216d-24cd-7b61-8274-37c62f38654e')
STAMP='20261011'
def now(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def within(p,root): return Path(p).resolve().is_relative_to(root.resolve())
def file_info(p):
    p=Path(p)
    if not p.is_file(): return {'file':str(p),'exists':False}
    return {'file':str(p),'exists':True,'bytes':p.stat().st_size,'sha256':sha(p)}
started=now()
freeze=B/f'migration-freeze-{STAMP}.json'
prior=read(freeze) if freeze.exists() else {}
index=read(B/'current-artifacts.json')
adopted={k:v for k,v in index.items() if re.fullmatch(r'r\d{2}_c\d{2}',k)}
selected={k:{**v,'fileEvidence':file_info(B/v['candidate'])} for k,v in adopted.items()}
by_hash={}
for p in (B/'native').glob('*.png'):
    by_hash.setdefault(sha(p),[]).append(str(p))
originals=[]
preserved=B/'migration-preserved-outputs-20261011'
for p in sorted(GENERATED.glob('*')):
    if not p.is_file(): continue
    h=sha(p)
    matches=by_hash.get(h,[])
    if not matches:
        preserved.mkdir(exist_ok=True)
        dst=preserved/p.name
        if not dst.exists(): shutil.copy2(p,dst)
        if sha(dst)!=h: raise RuntimeError(f'Preserved copy differs: {p}')
        matches=[str(dst)]
    originals.append({'original':str(p),'sha256':h,'workspaceCopies':matches,'saved':True})
write(B/f'migration-generated-outputs-{STAMP}.json',{'savedAtUtc':now(),'scope':'All files present in root chat generated_images directory','files':originals})

# Collect concrete referenced local paths, including historical provenance.
paths={}
def walk(v,origin):
    if isinstance(v,dict):
        for x in v.values(): walk(x,origin)
    elif isinstance(v,list):
        for x in v: walk(x,origin)
    elif isinstance(v,str) and re.match(r'^[A-Za-z]:[/\\]',v) and '\n' not in v and len(v)<700:
        p=Path(v)
        if not within(p,B): paths.setdefault(str(p),set()).add(str(origin.relative_to(B)))
for p in B.rglob('*.json'):
    if p.name.startswith('migration-'): continue
    try: walk(read(p),p)
    except (ValueError, OSError): pass
external=[]
external_dir=B/'migration-external-references-20261011'
for raw,origins in sorted(paths.items()):
    p=Path(raw)
    row={'file':raw,'workspaceExternal':not within(p,WORKSPACE),'referencedBy':sorted(origins)}
    if p.is_file():
        h=sha(p)
        row.update(exists=True,bytes=p.stat().st_size,sha256=h)
        if not within(p,WORKSPACE):
            matches=by_hash.get(h,[])
            if not matches:
                existing=[x['workspaceCopies'][0] for x in originals if x['sha256']==h]
                matches=existing
            if matches: row['workspaceCopies']=matches
            else:
                external_dir.mkdir(exist_ok=True)
                dst=external_dir/(h[:16]+'-'+p.name)
                if not dst.exists(): shutil.copy2(p,dst)
                if sha(dst)!=h: raise RuntimeError(f'External reference copy differs: {p}')
                row['workspaceCopies']=[str(dst)]
    elif p.is_dir(): row.update(exists=True,kind='directory')
    else: row['exists']=False
    external.append(row)
write(B/f'migration-reference-inventory-{STAMP}.json',{'savedAtUtc':now(),'files':external,'instruction':'Preserve all workspace-relative dependencies. Historical absolute paths remain unchanged; use workspaceCopies to relocate external files.'})

workers={}
for tile in ['r02_c03','r02_c04','r05_c04']:
    p=B/f'work-{tile}'/f'migration-freeze-{STAMP}.json'
    workers[tile]={'checkpoint':str(p),'exists':p.exists()}
    if p.exists(): workers[tile]['contents']=read(p)
latest=B/'work-r04_c02/repair-v3/r04_c02.candidate.png'
assembly=B/'work-r04_c02/repair-v3/r04_c02.candidate.assembly.json'
ad=read(assembly)
missing=[f'r{r:02d}_c{c:02d}' for r in range(1,8) for c in range(1,8) if f'r{r:02d}_c{c:02d}' not in adopted]
manifest={
 'schemaVersion':1,'zone':'fishing-village/northwest','savedAtUtc':now(),
 'generationStopped':True,'stoppedAtUtc':prior.get('stoppedAtUtc',started),
 'stopTimeMeaning':'Time first local migration inventory was started; no new generation was started after the freeze instruction. First clock observation confirming root generation hold was 2026-10-12T02:34:43Z.',
 'stopReason':'Migration freeze requested by coordinator after user requested committing and pushing all files to continue on another computer.',
 'rootFreezeFile':'D:/work/image/MAP_MIGRATION_FREEZE_20261011.json',
 'newGenerationStartedAfterFreeze':False,'rootInFlightRequests':[],
 'workerFreezeCheckpoints':workers,
 'activeCoordinates':['r04_c02','r02_c03','r02_c04','r05_c04'],
 'selectedCandidatePaths':selected,
 'unadoptedLatestRootCandidate':{
   'coordinate':'r04_c02','candidate':file_info(latest),'assembly':file_info(assembly),
   'sourcePixelProofPreviouslyRecorded':ad.get('proof'),
   'status':'saved-unadopted-pending-visual-review','formalAccepted':False,
   'remaining':['Review latest paving repair mask edges and 16 full native core crops before adopting.','Correct repair-v3 assembly base provenance field from repair-v1 to repair-v2; composition actually started from repair-v2. No artwork changes needed for metadata correction.','West and south boundary reviews require future adjacent tiles.'],
   'completedRepairsBeforeFreeze':['green cloth hem','red cloth fold','suspension ropes','paving junction generated and composed; visual QA pending']
 },
 'counts':{'scope4kTiles':49,'adopted4kCandidates':len(adopted),'internallyPassedAdoptedCandidates':sum(str(v.get('status','')).startswith('internally-accepted') for v in adopted.values()),'formalAccepted':sum(bool(v.get('formalAccepted')) for v in adopted.values())},
 'coordinatesWithoutAdoptedCandidate':missing,
 'nextMissingCoordinate':{'currentRoot':'r04_c02 final QA/adoption','afterRootAdoptionSuggested':'r05_c02','workerCoordinates':'See workerFreezeCheckpoints; complete and reconcile their saved candidates/deltas before more generation.'},
 'pendingRepairs':['r04_c02 latest saved paving mask/full-core QA and provenance metadata correction.','r02_c03 south roof/west bridge and possible narrow r03_c02 delta: use worker checkpoint.','r02_c04 beam joins/paving/south pillar-foot delta: use worker checkpoint.','r05_c04 net post/paving/sand continuity and independent r04_c04 south delta: use worker checkpoint.','All uncompleted coordinates and required outer seams remain unfinished.'],
 'unsavedSuccessfulOutputPaths':[],
 'successfulOutputPreservationInventory':str(B/f'migration-generated-outputs-{STAMP}.json'),
 'externalReferencePaths':str(B/f'migration-reference-inventory-{STAMP}.json'),
 'workspaceExternalReferenceCount':sum(x['workspaceExternal'] for x in external),
 'missingReferencedPaths':[x for x in external if not x['exists']],
 'preserveAllOriginalsIntermediatesPreviews':True,
 'gitWritesPerformed':False,'commitPushOwner':'Migration chat 01a11b5e-158a-77d0-8c02-e8e503b7abe4; coordinator aggregates incremental files.',
 'resumeCondition':'Resume art only after migration is complete and authorization is renewed.',
 'knownProcessState':{'oldLocalCompositionSession54028':'No longer present; expected output files already saved.','rootGeneration':'No pending request.'},
 'runtimePortability':{'oldWorkspace':'D:/work/image','pythonUsed':'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','pathRelocation':'Historical paths in provenance are retained. Restore workspace at original path or resolve using inventories; obtain a local Python runtime on new computer. Any copied standalone python.exe is only preserved provenance, not a complete runnable runtime.'}
}
write(freeze,manifest)
write(B/'local-continuation-20261011.json',{'savedAtUtc':now(),'status':'migration-frozen','checkpoint':str(freeze),'generationStopped':True,'gitWrites':False,'instructions':'Do not resume artwork until migration is complete and authorization is renewed. Preserve current-artifacts.json as the adopted index; newer pending candidates are in the freeze checkpoint.'})
print(json.dumps({'freeze':str(freeze),'counts':manifest['counts'],'rootOriginalFilesPreserved':len(originals),'newlyPreservedUnclassifiedOutputs':len(list(preserved.glob('*'))) if preserved.exists() else 0,'externalReferences':len(external),'outsideWorkspace':manifest['workspaceExternalReferenceCount'],'missingReferencedPaths':len(manifest['missingReferencedPaths']),'workerCheckpointPresence':{k:v['exists'] for k,v in workers.items()}},ensure_ascii=False))
