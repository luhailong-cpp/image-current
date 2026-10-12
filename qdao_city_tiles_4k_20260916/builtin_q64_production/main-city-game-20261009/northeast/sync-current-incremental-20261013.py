from pathlib import Path
import json,hashlib,re
from PIL import Image
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent;ROOT=Path('D:/work/image')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();inv=read(Z/'current-native-inventory.json');by={str(Path(x['file']).resolve()):x for x in inv['outputs']};new=[];issues=[]
reserved=set(read(Z/'reserved-tiles-20261013.json')['reservedTiles'])
old=read(Z/'progress.json');prior={r['tile']:r for r in old['tiles']}
rows=[]
for T in sorted(Z.iterdir()):
    if not T.is_dir() or not re.fullmatch(r'r\d\d_c\d\d',T.name) or T.name in reserved:continue
    for f in (T/'native').rglob('*.generation.json'):
        j=read(f)
        if j.get('route')!='builtin':continue
        asset=j.get('file',j.get('native',j.get('workspaceFile',j.get('repairNative'))))
        if not asset:issues.append(str(f));continue
        j['sha256']=j.get('sha256',j.get('repairSha256'))
        p=Path(asset);key=str(p.resolve())
        if key in by and by[key]['sha256']==j['sha256']:continue
        if not p.exists() or sha(p)!=j['sha256']:issues.append(str(f));continue
        with Image.open(p) as im:
            if im.size!=(1254,1254) or im.format!='PNG':issues.append(str(f));continue
        by[key]={'file':str(p),'record':str(f),'sha256':j['sha256'],'dimensions':[1254,1254]}
        new.append(by[key])
    if not (T/'tile-progress.json').exists():continue
    p=read(T/'tile-progress.json');s=read(T/'selected-native.json') if (T/'selected-native.json').exists() else {}
    cores=[f'p{r}{c}' for r in range(1,5) for c in range(1,5) if str((T/'native'/s.get(f'p{r}{c}',f'p{r}{c}.png')).resolve()) in by]
    candidate=Path(p['candidate']) if p.get('candidate') else T/'candidates'/f'{T.name}.candidate.png'
    full=bool(len(cores)==16 and candidate.is_file());h=None
    if full:
        oldr=prior.get(T.name,{})
        if str(candidate)==oldr.get('candidate') and p.get('candidateSha256')==oldr.get('candidateSha256') and oldr.get('fullyCovered4kCount'):
            h=oldr['candidateSha256']
        else:
            with Image.open(candidate) as im:full=im.size==(4096,4096) and (im.mode=='RGB' or im.getextrema()[3]==(255,255))
            if full:h=sha(candidate)
    passed=int(full and p.get('internalPassed4kCount')==1 and p.get('candidateSha256')==h)
    rows.append({'tile':T.name,'generatedNativeCount':sum(Path(x['file']).is_relative_to(T) for x in by.values()),'selectedCoreCount':len(cores),'missingCoreCount':16-len(cores),'fullyCovered4kCount':int(full),'internalPassed4kCount':passed,'formalAcceptedCount':0,'candidate':str(candidate) if full else None,'candidateSha256':h,'workerStatus':p.get('status'),'nextPatch':p.get('nextPatch'),'fullInternalReview':p.get('fullInternalReview')})
core=sum(r['selectedCoreCount'] for r in rows);full=sum(r['fullyCovered4kCount'] for r in rows);passed=sum(r['internalPassed4kCount'] for r in rows)
old.update({'updatedAt':now,'status':'native_production_and_bounded_local_QA','generationStopped':False,'newArtworkGenerationAllowed':True,'tiles':rows,'generatedNativeCount':len(by),'generatedNativeInsideTileDirectories':sum(r['generatedNativeCount'] for r in rows),'generatedSharedBorderRepairCount':len(by)-sum(r['generatedNativeCount'] for r in rows),'usableSelectedCoreCount':core,'complete4kCandidateCount':full,'fullyCovered4kCount':full,'complete16Core4kCandidateCount':full,'internalPassed4kCount':passed,'formalAcceptedCount':0,'missingNativeCoreCount':60*16-core,'missingFullyCovered4kCount':60-full,'missingNativeTileCount':60-sum(r['selectedCoreCount']==16 for r in rows),'fullyNativeTilesAwaiting4kAssemblyCount':sum(r['selectedCoreCount']==16 and not r['fullyCovered4kCount'] for r in rows),'completeTilesPendingInternalReviewCount':full-passed,'inventoryIssues':issues,'nextStep':'Continue original assigned native tile lanes; local repairs remain unpassed until source-bound visual review.','workQueue':str(Z/'work-queue-finish-20261012.json')})
save(Z/'progress.json',old)
inv.update({'updatedAt':now,'outputs':list(by.values()),'issues':issues,'priorHashVerificationReused':True});save(Z/'current-native-inventory.json',inv)
idx=read(Z/'current-adopted-index-20261012.json')
priorCandidates={r['tile']:r for r in idx['candidates']}
candidates=[]
for r in rows:
    if not r['fullyCovered4kCount']:continue
    entry={'tile':r['tile'],'file':r['candidate'],'workspaceRelativePath':str(Path(r['candidate']).relative_to(ROOT)),'sha256':r['candidateSha256'],'internalPassed':bool(r['internalPassed4kCount'])}
    if r['fullInternalReview']:
        review=read(r['fullInternalReview']);assert review['candidateSha256']==r['candidateSha256']
        entry['internalReview']=r['fullInternalReview'];entry['internalReviewSha256']=sha(r['fullInternalReview'])
    elif r['tile'] in priorCandidates:entry['priorReviewEvidenceRetained']=True
    candidates.append(entry)
idx.update({'updatedAt':now,'updatedAtUtc':now,'candidates':candidates,'internalPassedCount':passed,'currentCandidateCount':full,'remainingNativeCoreCount':960-core,'newOutputCount':len(by)-176,'newSelectedCoreCount':core-128,'generationStopped':False,'newArtworkGenerationAllowed':True,'requestedImageModel':None,'imageModelPreference':'included2.5 preferred; builtin2.0 permitted; actual model undisclosed'})
idx.setdefault('nativeSelections',{}).update({r['tile']:str(Z/r['tile']/'selected-native.json') for r in rows if (Z/r['tile']/'selected-native.json').exists()})
save(Z/'current-adopted-index-20261012.json',idx)
resume=read(Z/'production-resume-20261012.json');resume.update({'updatedAtUtc':now,'internalPassedCount':passed,'currentCandidateCount':full,'remainingNativeCoreCount':960-core,'generationStopped':False,'newArtworkGenerationAllowed':True});save(Z/'production-resume-20261012.json',resume)
q=Z/'qa/progress-sync-20261013';q.mkdir(exist_ok=True)
save(q/'current-sync.json',{'atUtc':now,'reason':'Index lag after root r07_c15 repair review; source-bound QA added without rechecking unchanged visual windows.','internalPassedCount':passed,'completeCandidateCount':full,'newNativeRecordsVerified':len(new),'priorNativeRecordsReused':len(by)-len(new),'r07_c15Review':str(Z/'r07_c15/qa/local-repair-20261013/internal-review-v1.json'),'r07_c15CandidateSha256':next(r['candidateSha256'] for r in rows if r['tile']=='r07_c15'),'issues':issues})
print(json.dumps({'selectedCores':core,'completeCandidates':full,'internalPassed':passed,'newNativeVerified':len(new),'issues':issues}))
