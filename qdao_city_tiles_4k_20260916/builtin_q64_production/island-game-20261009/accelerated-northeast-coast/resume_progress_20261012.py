from pathlib import Path
import json,re,sys
import coast_work as c
B=Path(__file__).resolve().parent
ORDER=['r02_c13','r02_c14','r01_c13','r01_c14']
RESUME=B/'production-resume-20261012.json'
def refresh():
    p=c.read(B/'progress.json')
    d=c.read(RESUME) if RESUME.exists() else {
        'resumedAtUtc':c.now(),'authorization':'边继续做边传吧',
        'authorityFile':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json',
        'historicalFreezePreserved':True,'builtinOnly':True,'paidApiAllowed':False,
        'gitOperationsPerformed':False,'firstNewSavedOutput':None,'errors':[]}
    selected={};missing=[];candidates=[]
    for tile in ORDER:
        selected[tile]=[]
        for r in range(4,0,-1):
            for col in range(1,5):
                ident=f'{tile}_p{r:02}_{col:02}'
                src=c.latest(B/'native',ident)
                if src:
                    rec=c.read(src.with_suffix('.png.generation.json'))
                    selected[tile].append({'id':src.stem,'file':src.as_posix(),'sha256':rec['sha256'],'dimensions':[rec['nativeWidth'],rec['nativeHeight']]})
                    if rec['generatedAtUtc']>d['resumedAtUtc']:
                        value={'id':src.stem,'file':src.as_posix(),'sha256':rec['sha256'],'generatedAtUtc':rec['generatedAtUtc']}
                        if not d['firstNewSavedOutput'] or value['generatedAtUtc']<d['firstNewSavedOutput']['generatedAtUtc']: d['firstNewSavedOutput']=value
                else: missing.append(ident)
        cand=B/'candidates'/f'{tile}.4096-candidate.png'
        if cand.exists():
            a=c.read(cand.with_suffix('.png.assembly.json'))
            candidates.append({k:a[k] for k in ['tileId','file','sha256','dimensions','selectedCores','formalAccepted']})
    updates={'generationAllowed':p.get('generationAllowed',True),'complete4096CandidateCount':len(candidates),'currentAdopted4096Files':candidates,
      'generatedNativeCount':len(list((B/'native').glob('*.png'))),'coveredCoreCount':64-len(missing),
      'remainingCoreCount':len(missing),'remainingCoordinates':missing,'selectedNativeSourcesByTile':selected,
      'nextMissingCore':missing[0] if missing else None,'nextStep':'Continue next missing native patch and pending seam checks.',
      'productionResumeFile':RESUME.as_posix()}
    p.update(updates);p['status']='active_builtin_production';p['updatedAtUtc']=c.now()
    d.update(updates);d.update(status=p['status'],updatedAtUtc=c.now(),currentPatch=p.get('currentPatch'),
       internalFullyReviewedTiles=p.get('internalFullyReviewedTiles',[]),internalReviewPending=p.get('internalReviewPending',[]))
    c.write(B/'progress.json',p);c.write(RESUME,d)
    c.write(B/'current-selection-20261012.json',{'updatedAtUtc':c.now(),'candidates':candidates,'native':selected,'formalAcceptedCount':0})
    return d
def prepare(core):
    r,col,pr,pc=map(int,re.fullmatch(r'r(\d+)_c(\d+)_p(\d+)_(\d+)',core).groups())
    files=list((B/'native').glob(core+'*.png'))+list((B/'guides').glob(core+'*.anchored-layout-only.png'))
    versions=[int(m.group(1)) for f in files if (m:=re.search(r'_v(\d+)',f.name))]
    ident=core+'_v'+str(max(versions,default=0)+1)
    south=f'r{r+(pr==4):02}_c{col:02}_p{1 if pr==4 else pr+1:02}_{pc:02}'
    west=f'r{r:02}_c{col-(pc==1):02}_p{pr:02}_{4 if pc==1 else pc-1:02}'
    neighbors=[]
    for key in [south,west]:
        for folder in [B/'native',B.parent/'northeast/native']:
            f=c.latest(folder,key)
            if f: neighbors.append(str(f));break
    assert not (B/'native'/f'{ident}.png').exists()
    c.prepare(ident,neighbors)
if __name__=='__main__':
    d=refresh()
    if len(sys.argv)>1: prepare(sys.argv[1])
    else: print(json.dumps({k:d[k] for k in ['status','complete4096CandidateCount','generatedNativeCount','remainingCoreCount','nextMissingCore','firstNewSavedOutput']},ensure_ascii=False))

