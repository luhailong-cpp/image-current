"""Exclusive left-column native work. No painting or resampling of final sources."""
from pathlib import Path
from PIL import Image
from workflow import ROOT, read, write, sha, now, patch
import r12_c11_sol_resume as original
import sys

TILE=sys.argv[1]
assert TILE in ['r13_c11','r14_c11']
PROGRESS=ROOT/f'progress-{TILE}.json'
RESUME=ROOT/f'production-resume-left-sol-{TILE}-20261012.json'
SELECTION=ROOT/f'selection-{TILE}.json'
NORTH='r12_c11' if TILE=='r13_c11' else 'r13_c11'
NORTH_CANDIDATE=ROOT/'tiles'/f'{NORTH}.candidate-sol-20261012-v02.png' if NORTH=='r12_c11' else ROOT/'tiles'/f'{NORTH}.candidate-sol-20261012-v01.png'
if (ROOT/f'progress-{NORTH}.json').exists():
    NORTH_CANDIDATE=Path(read(ROOT/f'progress-{NORTH}.json').get('candidate',str(NORTH_CANDIDATE)))

def configure():
    original.TILE=TILE;original.PROGRESS=PROGRESS;original.RESUME=RESUME

def init():
    authority=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json');a=read(authority);assert a['newArtworkGenerationAllowed'] and a['builtinOnly']
    assert not any(f.exists() for f in [PROGRESS,RESUME,SELECTION])
    assert not list((ROOT/'native').glob(TILE+'_*.png'))
    write(SELECTION,{'tile':TILE,'createdAt':now(),'patchVersions':{},'pendingFindings':[]})
    p={'tile':TILE,'updatedAt':now(),'status':'layout_and_actual_neighbors_preparing','generatedNativeCount':0,'selectedCoordinateCount':0,'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'missingPatches':[TILE+'_p'+str(r)+str(c) for r in range(1,5) for c in range(1,5)],'inFlightRequests':[],'productionResumeAuthority':str(authority),'productionResumeRecord':str(RESUME),'currentPatch':None,'lastError':None,'nextStep':'Review actual layout and north accepted sources, then generate all sixteen native coordinates.'}
    write(PROGRESS,p);write(RESUME,{'schemaVersion':1,'agent':'left_resume_sol','tile':TILE,'resumedAt':now(),'authority':str(authority),'authoritySha256':sha(authority),'route':'builtin','paidApiAllowed':False,'selectedVersions':{},'nativeInventory':[],'actualNativeCount':0,'newGenerationAttempted':False,'inFlightRequests':[],'formalAcceptedCount':0,'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'status':p['status'],'northAnchorTile':NORTH,'northAnchorCandidate':str(NORTH_CANDIDATE),'nextStep':p['nextStep']})
    print({'progress':str(PROGRESS),'resume':str(RESUME)})

def prepare(rc,version,description):
    pid=TILE+'_p'+rc;pp=patch(pid);box=pp['nativeGlobalBox'];r,c=map(int,rc)
    guide=ROOT/'guides'/f'{pid}.native-context-{version}.png';promptfile=ROOT/'prompts'/f'{pid}_{version}.prompt.txt';requestfile=ROOT/'prompts'/f'{pid}_{version}.request.json'
    assert not any(f.exists() for f in [guide,promptfile,requestfile,ROOT/'native'/f'{pid}_{version}.png'])
    base=ROOT/'guides'/f'{pid}.layout-only.png';im=Image.open(base).convert('RGB');sources=[];placements=[]
    def paste(f,nb,role):
        f=Path(f);inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
        if inter[2]<=inter[0] or inter[3]<=inter[1]:return
        src=Image.open(f);crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]];im.paste(src.crop(crop),tuple(dest));sources.append({'file':str(f),'sha256':sha(f),'role':role});placements.append({'source':str(f),'sourceCrop':crop,'destination':dest,'globalIntersection':inter})
    def native(f,role):
        rec=read(Path(str(f)+'.generation.json'));assert sha(f)==rec['sha256'] and [rec['width'],rec['height']]==[1254,1254]
        if 'coordinate' in rec:nb=rec['coordinate']['nativeGlobalBox']
        elif 'globalBox' in rec:nb=rec['globalBox']
        else:
            o=patch(rec['tile']+'_p11')['coreGlobalBox'];x,y=rec['tileRelativeOrigin'];nb=[o[0]+x,o[1]+y,o[0]+x+1254,o[1]+y+1254]
        paste(f,nb,role)
    if r==1:
        sel=read(ROOT/f'selection-{NORTH}.json')['patchVersions']
        for key in ['41','42','43','44']:native(ROOT/'native'/f'{NORTH}_p{key}_{sel[key]}.png','passed north native overlap')
        rec=read(Path(str(NORTH_CANDIDATE)+'.generation.json'));assert sha(NORTH_CANDIDATE)==rec['sha256']
        pcore=patch(NORTH+'_p11')['coreGlobalBox'];paste(NORTH_CANDIDATE,[pcore[0],pcore[1],pcore[0]+4096,pcore[1]+4096],'passed north exact candidate authority')
    if c==4:
        etile=TILE.replace('c11','c12');esel=ROOT/f'selection-{etile}.json'
        es={}
        if esel.exists():
            es=read(esel)['patchVersions']
        elif (ROOT/f'progress-{etile}.json').exists():
            es=read(ROOT/f'progress-{etile}.json').get('workingVersions',{})
        if es:
            for er in range(1,5):
                key=str(er)+'1';v=es.get(key)
                f=ROOT/'native'/f'{etile}_p{key}_{v}.png'
                if v and f.exists():native(f,'root current selected real east native halo')
        if TILE=='r13_c11' and r==1:
            anchor=ROOT/'native/r13_c12_p11_v02.png'
            if anchor.exists():native(anchor,'root approved r13 east p11v02 exact native halo')
    sel=read(SELECTION)['patchVersions']
    for nr,nc in [(r-1,c),(r,c+1),(r,c-1),(r+1,c)]:
        key=str(nr)+str(nc)
        if key in sel:native(ROOT/'native'/f'{TILE}_p{key}_{sel[key]}.png','selected adjacent exact native overlap')
    if TILE=='r13_c11' and rc=='14':
        lower=ROOT/'native/r13_c11_c12_shared_column_lower_v01.png';assert lower.exists();native(lower,'passed whole shared lower column; preserve this sharp right half')
        rec=read(Path(str(NORTH_CANDIDATE)+'.generation.json'));pcore=patch(NORTH+'_p11')['coreGlobalBox'];paste(NORTH_CANDIDATE,[pcore[0],pcore[1],pcore[0]+4096,pcore[1]+4096],'actual final north pixels over lower native north halo')
    if TILE=='r13_c11' and rc=='24':
        lower=ROOT/'native/r13_c11_c12_shared_column_lower_v01.png';assert lower.exists();native(lower,'actual first-row right-half ownership; passed whole lower-column source, not unused p14 right half')
    if c==4:
        etile=TILE.replace('c11','c12');ep=ROOT/f'progress-{etile}.json';candidate=None
        if ep.exists():
            value=read(ep).get('candidate')
            if value and Path(value).exists():candidate=Path(value)
        if candidate is None:
            matches=sorted((ROOT/'tiles').glob(etile+'.candidate-sol-20261013-v*.png'))
            if matches:candidate=matches[-1]
        if candidate is not None:
            a=Image.open(candidate);assert a.size==(4096,4096) and a.mode=='RGB';o=patch(etile+'_p11')['coreGlobalBox'];paste(candidate,[o[0],o[1],o[0]+4096,o[1]+4096],'actual final east candidate pixels take authority over unused native halo')
    im.save(guide);write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'generatedAt':now(),'width':1254,'height':1254,'operation':'Unscaled integer crop and paste of real adjacent source overlap onto layout-only guide; reference only','usableAsFinalArt':False,'base':str(base),'baseSha256':sha(base),'derivedFrom':sources,'placements':placements,'globalBox':box})
    refs=[{'file':str(guide),'sha256':sha(guide),'role':'exact coordinate edit target; sharp native overlap fixed'}]+read(ROOT/'references.json')
    prompt=f'''Use case: precise-object-edit.
Asset type: one native 1254 x 1254 square daylight Q-painted Daoist island game map patch.
Primary request: Render only the unfinished soft interior of image 1 into crisp matching game art. Keep the existing sharp overlap geometry fixed, smoothly continuing it at the same scale. Image 1 is the exact coordinate edit target; image 2 is full-island layout authority; image 3 supplies materials only; image 4 supplies the approved painting style only.
Exact coordinate: {pid}, native global extent {box} within a 57344 square map. Final core is local [115,115,1139,1139).
Scene: {description}
Keep the close crop, current scale and object positions. Match rounded clear contours, delicate painted detail, bright blue and turquoise water, warm tan stone or wood where actually present, and soft daylight. Keep the sharp neighboring bands fixed. Output a single opaque square 1254 x 1254 patch. No lettering, interface or watermark.
'''
    promptfile.write_text(prompt,encoding='utf-8');write(requestfile,{'promptPath':str(promptfile),'promptSha256':sha(promptfile),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'preparedAt':now(),'status':'prepared_not_submitted'})
    for f in [PROGRESS,RESUME]:
        p=read(f);p.update({'updatedAt':now(),'nextRequest':str(requestfile),'nextPreparedPatch':pid,'nextPreparedVersion':version})
        if not p.get('inFlightRequests'):p.update({'status':'request_prepared','currentPatch':pid,'currentVersion':version})
        write(f,p)
    print({'request':str(requestfile),'guide':str(guide)})

def select(rc,version):
    f=ROOT/'native'/f'{TILE}_p{rc}_{version}.png';assert f.exists()
    s=read(SELECTION);s['patchVersions'][rc]=version;write(SELECTION,s)
    for f in [PROGRESS,RESUME]:
        p=read(f);p.update({'updatedAt':now(),'selectedCoordinateCount':len(s['patchVersions']),'selectedVersions':s['patchVersions'],'actualNativeCount':len(list((ROOT/'native').glob(TILE+'_*.png'))),'generatedNativeCount':len(list((ROOT/'native').glob(TILE+'_*.png'))),'missingPatches':[TILE+'_p'+str(r)+str(c) for r in range(1,5) for c in range(1,5) if str(r)+str(c) not in s['patchVersions']],'status':'native_selected_pending_full_candidate_qa'});write(f,p)
    print(s['patchVersions'])

def repair(rc,version,target_version,description):
    prepare(rc,version,description)
    pid=TILE+'_p'+rc;requestfile=ROOT/'prompts'/f'{pid}_{version}.request.json';req=read(requestfile);target=ROOT/'native'/f'{pid}_{target_version}.png'
    req['references']=[{'file':str(target),'sha256':sha(target),'role':'existing native edit target; same crop scale and geometry'}]+req['references']
    prompt=f'''Use case: precise-object-edit.
Edit image 1 at its exact native 1254 x 1254 framing. Image 2 is the coordinate continuity guide made from actual sharp adjacent originals; images 3 to 5 are full-island layout, materials and approved style.
Primary request: {description}
Keep every actual sea-rock silhouette, waterline, reflection, broad light direction, object size and framing in place. Preserve the sea and the exact upper border. Continue the existing physical rock planes coherently through the edited area with delicate irregular facets. Output one opaque square 1254 x 1254. No lettering, interface or watermark.
'''
    Path(req['promptPath']).write_text(prompt,encoding='utf-8');req['promptSha256']=sha(Path(req['promptPath']));write(requestfile,req);print({'repairRequest':str(requestfile)})

def inspect_layout():
    board=Image.new('RGB',(1024,1024));sources=[]
    for r in range(1,5):
        for c in range(1,5):
            f=ROOT/'guides'/f'{TILE}_p{r}{c}.layout-only.png';im=Image.open(f);board.paste(im.crop((115,115,1139,1139)).resize((256,256),Image.Resampling.BICUBIC),((c-1)*256,(r-1)*256));sources.append({'file':str(f),'sha256':sha(f)})
    f=ROOT/'qa'/f'{TILE}-layout-inspection-sol.png';assert not f.exists();board.save(f);write(Path(str(f)+'.generation.json'),{'file':str(f),'sha256':sha(f),'createdAt':now(),'operation':'Layout guide core contact sheet only; downsized for layout inspection; never final art','usableAsFinalArt':False,'derivedFrom':sources});print(str(f))

configure()
action=sys.argv[2]
if action=='init':init()
elif action=='prepare':prepare(*sys.argv[3:])
elif action=='submit':original.submit(*sys.argv[3:])
elif action=='receive':original.receive(*sys.argv[3:])
elif action=='select':select(*sys.argv[3:])
elif action=='repair':repair(*sys.argv[3:])
elif action=='inspect-layout':inspect_layout()
