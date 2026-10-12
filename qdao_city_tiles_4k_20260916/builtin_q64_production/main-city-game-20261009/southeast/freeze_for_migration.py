"""Freeze metadata and preserve returned outputs. No generation, art edits or Git."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re,shutil
from PIL import Image

Z=Path(__file__).resolve().parent
WORK=Path('D:/work/image')
STOP='2026-10-12T02:28:55Z'
OUT=Z/'migration-preserved-20261011';OUT.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def art(p):
    p=Path(p)
    return {'path':str(p),'workspaceRelativePath':p.relative_to(WORK).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def strings(o):
    if isinstance(o,str):yield o
    elif isinstance(o,dict):
        for v in o.values():yield from strings(v)
    elif isinstance(o,list):
        for v in o:yield from strings(v)

# Inspect provenance text only. Do not rerun art QA or promote pending trials.
external=set(); unreadable=[]; generation_records=[]; prepared_without_result=[]
for p in Z.rglob('*.json'):
    if OUT in p.parents or p.name=='migration-freeze-20261011.json':continue
    try:o=read(p)
    except Exception as e:
        unreadable.append({'path':str(p),'error':str(e)});continue
    if p.name.endswith('generation.json'):generation_records.append(str(p))
    for s in strings(o):
        normalized=s.replace('\\','/')
        if re.match(r'^[A-Za-z]:/',normalized) and normalized.count(':')==1 and '\n' not in normalized and not normalized.lower().startswith('d:/work/image/'):
            if len(normalized)<1000:external.add(normalized)
        for q in re.findall(r'C:[\\/][^\n"<>:]*?\.png',s):external.add(q.replace('\\','/'))
    if p.name in ('preparation.json','prepare.json'):
        parent=p.parent
        if not list(parent.glob('*generation.json')) and not list(parent.glob('*receipt.json')):
            prepared_without_result.append(str(p))

# Returned images in this zone's known image-generation session directories are
# preserved even if their receipt was never ingested before the freeze.
session_dirs={Path(s).parent for s in external if '/.codex/generated_images/' in s and s.lower().endswith('.png')}
session_dirs.add(Path('C:/Users/luyua/.codex/generated_images/01a12076-19f9-7f00-8135-01e1b5fb7007'))
external_images={Path(s) for s in external if Path(s).suffix.lower() in ('.png','.jpg','.jpeg','.webp') and Path(s).is_file()}
for d in session_dirs:
    if d.is_dir():external_images.update(d.glob('*.png'))

# Compare bytes to local native-sized sources so equal originals need not be
# duplicated. Copies retain the original bytes, source path and SHA mapping.
native_hashes={}
for p in Z.rglob('*.png'):
    try:
        with Image.open(p) as im:size=im.size
    except Exception:continue
    if size==(1254,1254):native_hashes.setdefault(sha(p),p)
preserved=[];prior_index=OUT/'external-image-preservation-index.json'
new_copies=read(prior_index).get('newCopies',[]) if prior_index.exists() else []
for src in sorted(external_images,key=str):
    digest=sha(src);dest=native_hashes.get(digest)
    if dest is None:
        dest=OUT/(digest[:16]+'-'+src.name)
        if not dest.exists():shutil.copyfile(src,dest)
        assert sha(dest)==digest
        native_hashes[digest]=dest
        if str(dest) not in new_copies:new_copies.append(str(dest))
    else:assert sha(dest)==digest
    preserved.append({'externalPath':str(src),'sha256':digest,'portableCopy':str(dest),'workspaceRelativeCopy':dest.relative_to(WORK).as_posix(),'byteIdentical':True})

selected=[];missing=[];pending=[];active=[];maps=[]
for r in range(9,17):
    for c in range(9,17):
        name=f'r{r:02d}_c{c:02d}';td=Z/name
        amap=read(td/'active-native-map.json') if (td/'active-native-map.json').exists() else {}
        maps.append({'tile':name,'activeNativeCount':len(amap),'missingNativeCoordinates':[f'p{a:02d}_{b:02d}' for a in range(1,5) for b in range(1,5) if f'p{a:02d}_{b:02d}' not in amap]})
        if not amap:missing.append(name);continue
        active.append(name)
        if name=='r13_c13':
            p={'candidate':str(td/'candidate/r13_c13-4k-candidate-repaired.png'),'context':str(td/'candidate/r13_c13-context-4326-repaired.png'),'assemblyManifest':str(td/'candidate/replay-verification.json'),'internalArtQA':'passed','formalAccepted':False,'nextStep':'Historical core immutable; neighboring joint review remains pending.'}
        else:p=read(td/'progress.json')
        item={'tile':name,'candidate':art(p['candidate']),'context':art(p['context']),'formalAccepted':False,'activeNativeMap':art(td/'active-native-map.json')}
        for k in ('assemblyManifest','repairManifest','visualQA','localOrnamentQAReport'):
            value=p.get(k)
            path=value.get('path') if isinstance(value,dict) else value
            if path and Path(path).is_file():item[k]=art(path)
        selected.append(item)
        pending.append({'tile':name,'internalArtQA':p.get('internalArtQA'),'externalNeighborSeamQA':p.get('externalNeighborSeamQA'),'resumeOnlyAfterMigration':p.get('nextStep'),'remainingQA':p.get('remainingQA',[])})

unmerged=[]
for d in sorted((Z/'r13_c15/repairs').glob('structure-*')):
    if not d.is_dir():continue
    entry={'directory':str(d),'adopted':False,'reason':'Preserved independent repair; no root merge or new QA during migration freeze.','files':[]}
    for name in ('generation.json','preparation.json','receipt.json','composition.json','replay.json','visual-qa.json','qa.json'):
        p=d/name
        if p.exists():entry['files'].append(art(p))
    for name in ('native-1254.png','candidate-4096.png','context-4326.png'):
        p=d/name
        if p.exists():entry[name]=art(p)
    unmerged.append(entry)

contract=read(Z.parent/'production-contract.json')
shared=[]
for key in ('layoutReference','detailStyleReference','primaryStyleReference'):
    p=Path(contract[key]);shared.append({'role':key,**art(p)})
external_missing=[s for s in sorted(external) if Path(s).suffix.lower() in ('.png','.jpg','.jpeg','.webp') and not Path(s).exists()]
non_image_external=[s for s in sorted(external) if Path(s).suffix.lower() not in ('.png','.jpg','.jpeg','.webp')]
write(OUT/'external-image-preservation-index.json',{'externalImages':preserved,'newCopies':new_copies,'originalsDeleted':False,'sessionDirectoriesInspected':[str(d) for d in sorted(session_dirs,key=str)]})
now=datetime.now(timezone.utc).isoformat()
report={'schemaVersion':1,'zone':'southeast','savedAtUtc':now,'generationStopped':True,'stopObservedAtUtc':STOP,
 'stopObservedAtUserLocalTime':'2026-10-11T22:28:55-04:00','reason':'User requested all project materials committed/pushed for migration to another computer; art work frozen.',
 'rootFreezeRecord':art(WORK/'MAP_MIGRATION_FREEZE_20261011.json'),
 'childStopMessagesSentTo':['/root/assembly_support','/root/seam_audit','/root/south_production'],
 'childRuntimeSnapshot':{'observedAtUtc':STOP,'liveAgents':['/root'],'runningChildCount':0,'basis':'collaboration.list_agents returned only root before messages'},
 'inFlightImageGenCount':0,'inFlightBasis':'No root pending tool call and no live child workers; prepared-only records are not treated as active requests.',
 'newGenerationOrRepairCallsSinceFreeze':0,'activeCoordinates':active,'selectedCandidatePaths':selected,
 'plannedTileCount':64,'currentCandidateCount':len(selected),'formalAcceptedCount':0,'notStartedTileCount':len(missing),
 'missingTiles':missing,'nextMissingCoordinate':{'selection':'row-major inventory position; not a production assignment','tile':missing[0] if missing else None,'nativePatch':'p01_01' if missing else None},
 'nativeCoordinateCoverage':maps,'pendingRepairs':pending,
 'fourTileCornerBreakpoint':{'status':'failed_not_applied','immutableOldCoreSha256':'db5f956694c700b16094eb532ad9097e8a54f4a19d14797325f6fbd0ca18971f','latestAttempt':str(Z/'corner-repair-20261011/narrow-upper-joint-20261011T125355'),'reason':'Generated upper-right joint still requires moving fixed upper-left pixels; source rejected. Both attempts preserved.'},
 'unmergedSuccessfulRepairArtifacts':unmerged,
 'independentRepairCheckpoint':art(Z/'r13_c15/repairs/structure-checkpoint-20261011.json') if (Z/'r13_c15/repairs/structure-checkpoint-20261011.json').exists() else None,
 'unsavedSuccessfulOutputPaths':[],'returnedExternalImageCount':len(preserved),'newlyPreservedOutputCount':len(new_copies),
 'externalReferencePaths':preserved,'externalImagePreservationIndex':art(OUT/'external-image-preservation-index.json'),
 'missingHistoricalExternalImagePaths':external_missing,'otherExternalPathsForEnvironmentOrHistory':non_image_external,
 'sharedWorkspaceReferencesRequired':shared,'preparedRecordsWithoutSuccessReceipt':prepared_without_result,
 'unreadableProvenanceJson':unreadable,'generationRecordCount':len(generation_records),
 'retainedMaterials':'Keep all original/native/candidate/context/repair/rejected/preview/layout-only/request/receipt/manifest files. External original images remain untouched.',
 'resumeInstructions':'After migration, remap absolute D:/work/image and C:/Users paths using workspaceRelativePath and the external preservation index. Retain the selected pointers above; do not silently promote independent r13_c15 trials. Resume art only after renewed migration-complete direction.',
 'artworkReauditedDuringFreeze':False,'gitOperationsPerformed':False,'sourceDeletionPerformed':False,'uploaderPrivateStateTouched':False,'allMapsComplete':False}
write(Z/'migration-freeze-20261011.json',report)
for name in ('progress.json','local-continuation-20261011.json','continuation-round-20261011.json'):
    p=Z/name
    if p.exists():
        old=read(p)
        old.update(generationStopped=True,migrationFreeze=str(Z/'migration-freeze-20261011.json'),generationStopObservedAtUtc=STOP,inFlightImageGenCount=0)
        if name=='progress.json':old['status']='migration_frozen_no_new_generation'
        write(p,old)
print(json.dumps({'freeze':str(Z/'migration-freeze-20261011.json'),'generationStopped':True,'inFlightImageGenCount':0,'selectedCandidateCount':len(selected),'externalReturnedImagesPreserved':len(preserved),'newCopies':len(new_copies),'missingHistoricalExternalImages':len(external_missing),'unmergedRepairDirectories':len(unmerged),'unreadableJson':len(unreadable)}))
