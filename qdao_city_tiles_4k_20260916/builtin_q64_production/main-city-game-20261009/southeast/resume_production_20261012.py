from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,os,uuid

Z=Path(__file__).resolve().parent
authority=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):
    p=Path(p);t=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    t.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(t,p)
control=read(authority)
assert control['newArtworkGenerationAllowed'] and control['builtinOnly'] and not control['gitMutationsAllowedForProductionWorkers']
fpath=Z/'migration-freeze-20261011.json';freeze=read(fpath)
rp=Z/'production-resume-20261012.json'
report=read(rp) if rp.exists() else {'resumedAtUtc':datetime.now(timezone.utc).isoformat(),'firstNewOutput':None}
selected=[]
for row in freeze['selectedCandidatePaths']:
    td=Z/row['tile']
    p=read(td/'progress.json') if (td/'progress.json').exists() else {}
    cp=Path(p.get('candidate',row['candidate']['path']))
    selected.append({'tile':row['tile'],'candidate':str(cp),'sha256':sha(cp),'internalArtQA':p.get('internalArtQA','passed'),'externalQA':p.get('externalNeighborSeamQA','pending'),'formalAccepted':False})
report.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),userAuthorization='边继续做边传吧; 继续做完给我',
    authority={'path':str(authority),'sha256':sha(authority)},historicalFreeze={'path':str(fpath),'sha256':sha(fpath)},
    generationStopped=False,newArtworkGenerationAllowed=True,builtinOnly=True,paidApiAllowed=False,
    status='resumed_from_saved_native_and_repair_checkpoints',selectedCandidates=selected,
    complete4kCandidateCount=6,formalAcceptedCount=0,remainingUnstartedTileCount=58,
    activeWork={'root':'r14_c15 next native coordinate; shared four-tile corner remains pending',
                'seam_audit':'r13_c15 merge saved three structural repair steps then necessary local seams',
                'south_production':'r15_c13 north texture band and small railing relief',
                'assembly_support':'r14_c14 offline checkpoint recovery after this turn network rejection'},
    currentRootCoordinate='r14_c15/p01_01',historicalFreezeAndAuditsModified=False,
    gitOperationsPerformed=False,sourceDeletionPerformed=False,currentUploadIsIndependentSnapshot=True)
write(rp,report)
p=read(Z/'progress.json')
p.update(status='resumed_native_production_and_seam_repair',updatedAt=report['updatedAtUtc'],generationStopped=False,
    productionResume=str(rp),authority=str(authority),activeWork=report['activeWork'],
    nextStep='Merge saved r13_c15 structural repairs; continue r14_c15 native patches and r15_c13 boundary repairs.')
write(Z/'progress.json',p)
local={f'p{r:02d}_{c:02d}':
    'Render only the approved cropped tea-house waterside terrace, its existing warm timber deck/legs/stone-railing, blue pond, lotus and attached small foliage visible in the layout guide. Preserve existing object placements and camera. Do not add any new building, pot, railing cap, hanging ornament or rabbit.'
    for r in range(1,5) for c in range(1,5)}
local['p01_01']='Exact upper-left crop of the waterside tea-house terrace below the previously completed bench. Extend the warm timber bench/deck and existing vertical thick square supporting post entering from the north; natural stone paving and attached foliage remain at the west/lower-left according to the guide. Maintain the north and west native anchor strips. No new props or caps.'
write(Z/'r14_c15/local-content.json',local)
print(json.dumps({'resumeRecord':str(rp),'historicalFreezeSha256':sha(fpath),'currentCoordinate':'r14_c15/p01_01'}))
