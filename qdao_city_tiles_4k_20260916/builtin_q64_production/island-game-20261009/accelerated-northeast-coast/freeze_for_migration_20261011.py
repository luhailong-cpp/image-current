"""Local freeze inventory only. No image generation, visual re-review, or Git."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter
import json, hashlib, shutil, re
import coast_work as c

B=Path(__file__).resolve().parent
ROOT=Path('D:/work/image')
CACHE=Path('C:/Users/luyua/.codex/generated_images/01a12555-c57d-71f2-bbd6-68944dc616bc')
ORDER=['r02_c13','r02_c14','r01_c13','r01_c14']
def stamp(): return datetime.now(timezone.utc).isoformat()
def rel(p):
    try: return Path(p).relative_to(ROOT).as_posix()
    except ValueError: return None
def item(p):
    p=Path(p)
    return {'file':p.as_posix(),'workspaceRelativePath':rel(p),'sizeBytes':p.stat().st_size,'sha256':c.sha(p)}
def summary_review(p):
    d=c.read(p)
    return {'file':p.as_posix(),'sha256':c.sha(p),'metadata':{k:v for k,v in d.items() if k not in ['seams','crosses','sources']},
            'historicalSeamEntryCount':len(d.get('seams',[])),
            'historicalSeamStatusCounts':dict(Counter(x.get('status','unknown') for x in d.get('seams',[]))),
            'note':'Existing review read only; no new visual review at freeze. Historical entries may refer to superseded originals.'}

before=c.read(B/'progress.json')
natives=[]
byhash={}
for p in sorted((B/'native').glob('*.png')):
    rec=c.read(p.with_suffix('.png.generation.json'))
    info=item(p)
    assert info['sha256']==rec['sha256'], p
    info.update({'id':p.stem,'dimensions':[rec['nativeWidth'],rec['nativeHeight']],'sourcePath':rec.get('sourcePath'),
                 'generationRecord':p.with_suffix('.png.generation.json').as_posix()})
    natives.append(info)
    byhash.setdefault(info['sha256'],[]).append(p.as_posix())
assert len(natives)==47
cache_inventory=[]
recovered=[]
for p in sorted(CACHE.glob('*.png')):
    info=item(p)
    equivalents=byhash.get(info['sha256'],[])
    if not equivalents:
        dest=B/'migration-recovered-successful-outputs'/p.name
        dest.parent.mkdir(exist_ok=True)
        if not dest.exists(): shutil.copy2(p,dest)
        assert c.sha(dest)==info['sha256']
        equivalents=[dest.as_posix()]
        recovered.append(item(dest))
    info['verifiedWorkspaceCopies']=equivalents
    cache_inventory.append(info)
selected={}
missing=[]
candidates=[]
for tile in ORDER:
    selected[tile]=[]
    for pr in range(4,0,-1):
        for pc in range(1,5):
            ident=f'{tile}_p{pr:02}_{pc:02}'
            p=c.latest(B/'native',ident)
            if p: selected[tile].append(item(p)|{'id':p.stem,'coreId':ident})
            else: missing.append(ident)
    cand=B/'candidates'/f'{tile}.4096-candidate.png'
    if cand.exists():
        rec=c.read(cand.with_suffix('.png.assembly.json'))
        info=item(cand)
        assert info['sha256']==rec['sha256']
        assert len(rec['sources'])==16
        info.update({'tile':tile,'dimensions':rec['dimensions'],'assemblyRecord':cand.with_suffix('.png.assembly.json').as_posix(),
                     'selectedCores':rec['selectedCores'],'formalAccepted':False})
        candidates.append(info)
assert len(candidates)==2 and len(missing)==26
refs={}
def collect(v):
    if isinstance(v,dict):
        if isinstance(v.get('file'),str) and re.match(r'^[A-Za-z]:[/\\]',v['file']):
            p=Path(v['file'])
            if p.exists(): refs[p.as_posix()]=p
        for value in v.values(): collect(value)
    elif isinstance(v,list):
        for value in v: collect(value)
for p in (B/'prompts').glob('*.inputs.json'): collect(c.read(p))
outside_zone=[item(p) for p in refs.values() if not p.is_relative_to(B)]
outside_workspace=[x for x in outside_zone if x['workspaceRelativePath'] is None]
latest=max(natives,key=lambda x:c.read(x['generationRecord'])['generatedAtUtc'])
reviews=[summary_review(B/'qa/audit-final-r02-c13/final-review.json'),summary_review(B/'qa/audit-c14/review.json')]
status={
 'schemaVersion':1,'zone':'accelerated-northeast-coast','threadId':'01a12555-c57d-71f2-bbd6-68944dc616bc',
 'status':'stopped_for_migration','generationAllowed':False,'newRequestsStartedThisTurn':0,
 'stoppedAtUtc':'2026-10-12T02:37:13Z','stoppedAtUserTime':'2026-10-11T22:37:13-04:00',
 'stopTimeBasis':'Clock-confirmed quiescent state after migration stop instruction; no generation request was started in this resumed turn.',
 'freezeRecordedAtUtc':stamp(),'userTimezone':'America/New_York',
 'stopReason':'User is moving to another computer; main control relayed freeze instruction. Only save already successful/in-flight outputs.',
 'assignment':ORDER,'target4096TileCount':4,'complete4096CandidateCount':len(candidates),'formalAcceptedCount':0,
 'currentAdopted4096Files':candidates,'allSavedNativeVersionCount':len(natives),
 'coveredCoreCount':sum(map(len,selected.values())),'totalRequiredCoreCount':64,
 'selectedNativeSourcesByTile':selected,'allNativeVersions':natives,
 'remainingCoreCount':len(missing),'remainingCoordinatesInProductionOrder':missing,
 'resumeBreakpoint':{'nextMissingCore':'r01_c13_p03_03','guideAlreadyPrepared':str(B/'guides/r01_c13_p03_03.anchored-layout-only.png').replace('\\','/'),
    'inputs':str(B/'prompts/r01_c13_p03_03.inputs.json').replace('\\','/'),
    'lastSavedOutput':latest,'awaitingReview':'r01_c13_p03_02_v4',
    'repairNote':'v4 replaced visible lower-right rectangular water transition; root preview found it improved. Final native west/south seam check remains pending. v1-v3 are preserved and superseded.',
    'rule':'Do not resume generation until user lifts migration freeze. Reuse existing successful output; do not redraw completed groups.'},
 'qaState':{'r02_c13':'Full existing internal seam and junction review passed; south checked. West c12 remains unreviewed.',
            'r02_c14':'Complete candidate exists. Partial seam review and repair checks are saved; final complete internal/junction review not documented.',
            'r01_c13':'6 of 16 cores saved; v4 repair seam check and assembled-tile review pending.',
            'r01_c14':'0 of 16 cores saved.',
            'external':'Existing c13 south and c14 south/west evidence retained. North row incomplete; west c12 not verified. No formal region acceptance.',
            'reviewRecords':reviews},
 'inFlightRequests':[],'inFlightRequestCount':0,'activeChildTasks':[],
 'childStopPropagation':'Live collaboration inventory contained only /root; audit_geometry is not running, so no child remained to notify.',
 'unsavedSuccessfulOutputsRemaining':[],'recoveredSuccessfulOutputs':recovered,
 'externalGeneratedCache':cache_inventory,
 'outsideWorkspaceRequiredArtworkReferences':outside_workspace,
 'sharedWorkspaceDependenciesOutsideZone':outside_zone,
 'migrationNote':'All cached PNGs in this thread were hash-matched to a workspace copy or preserved in migration-recovered-successful-outputs. Transfer shared workspace dependencies too. Absolute paths in historical receipts must be remapped to the new workspace root.',
 'runtimeDependency':{'python':str(Path('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')).replace('\\','/'),
                      'packages':['Pillow'],'mustCopyRuntime':False,'note':'Install/use Python with Pillow on destination; these are tooling, not unique artwork.'},
 'gitOperationsPerformed':False,'filesDeleted':False,'newVisualReviewPerformed':False,
 'historicalProgressBeforeFreeze':before
}
c.write(B/'migration-freeze-20261011.json',status)
c.progress(status='stopped_for_migration',generationAllowed=False,currentTile='r01_c13',currentPatch='r01_c13_p03_03',
  candidateTiles=[Path(x['file']).stem for x in candidates],currentAdopted4096Files=candidates,
  complete4096CandidateCount=2,generatedNativeCount=47,coveredCoreCount=38,remainingCoreCount=26,
  remainingCoordinates=missing,internalFullyReviewedTiles=['r02_c13'],internalReviewPending=['r02_c14'],
  inFlightRequestCount=0,nextStep='Wait for user to lift migration freeze. Resume from r01_c13_p03_03; verify v4 seams first.',
  migrationFreezeFile=(B/'migration-freeze-20261011.json').as_posix())
old=c.read(B/'continuation-round-20261011.json')
old.update(status='stopped_for_migration',currentCoordinate='r01_c13_p03_03',latestSaved=latest,
  remainingUnrenderedCoreCount=26,nextStep='Migration freeze: no generation until explicitly resumed.',
  migrationFreezeFile=(B/'migration-freeze-20261011.json').as_posix(),updatedAtUtc=stamp())
c.write(B/'continuation-round-20261011.json',old)
c.write(B/'continuation-status-20261011-evening.json',{
  'status':'stopped_for_migration','recordedAtUtc':stamp(),'newImageRequests':0,'complete4096Candidates':2,
  'nativeVersionsSaved':47,'coreCoverage':38,'remainingCores':26,'inFlightRequests':0,
  'recoveredSuccessfulOutputs':recovered,'migrationFreezeFile':(B/'migration-freeze-20261011.json').as_posix(),
  'latestSaved':latest,'gitOperationsPerformed':False})
print(json.dumps({'freezeFile':(B/'migration-freeze-20261011.json').as_posix(),
 'complete4096Candidates':2,'nativeVersions':47,'coveredCores':38,'missingCores':26,
 'cacheImagesChecked':len(cache_inventory),'recoveredSuccessfulOutputs':len(recovered),
 'outsideWorkspaceArtworkReferences':len(outside_workspace),'sharedWorkspaceDependencies':len(outside_zone),
 'qaSummary':[{ 'file':r['file'],'historicalSeamEntryCount':r['historicalSeamEntryCount'],'counts':r['historicalSeamStatusCounts'],'metadataKeys':list(r['metadata'])} for r in reviews],
 'inFlight':0},ensure_ascii=False))

