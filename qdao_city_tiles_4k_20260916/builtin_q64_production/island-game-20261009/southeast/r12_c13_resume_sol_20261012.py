"""Right tile continuation: coordinate guides, receipts, exact pixel crops and QA. No painting."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import json, hashlib, shutil, sys

ROOT=Path(__file__).resolve().parent
TID='r12_c13'
PROGRESS=ROOT/'progress-r12_c13.json'
RESUME=ROOT/'production-resume-right-sol-20261012.json'
QA=ROOT/'qa/r12_c13-resume-sol-20261012'
AUTH=Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def patch(pid):
    for rp in (ROOT/'prompts').glob(pid+'_v*.request.json'):
        req=read(rp)
        if req.get('coordinate',{}).get('id')==pid:return req['coordinate']
    if pid=='r12_c13_deck_corner_whole':
        return {'id':pid,'tile':TID,'tileRelativeOrigin':[-115,2452],'nativeGlobalBox':[49037,47508,50291,48762],'coreGlobalBox':[49152,47623,50176,48647],'nativePixels':[1254,1254],'coreCrop':[115,115,1139,1139],'operation':'registered whole-object native source, adoption requires explicit source crop manifest'}
    for t in read(ROOT/'coordinate-plan.json')['tiles']:
        for p in t['patches']:
            if p['id']==pid:return p
    raise ValueError(pid)
def change_progress(**changes):
    d=read(PROGRESS);d.update(changes);d['updatedAt']=now();write(PROGRESS,d)
def change_resume(**changes):
    d=read(RESUME);d.update(changes);d['updatedAtUtc']=now();write(RESUME,d)

mode=sys.argv[1]
if mode=='initialize':
    a=read(AUTH);assert a['newArtworkGenerationAllowed'] and a['builtinOnly']
    req=ROOT/'prompts/r12_c13_p23_v01.request.json';r=read(req)
    for ref in r['references']:assert sha(Path(ref['file']))==ref['sha256']
    guide=Path(r['references'][0]['file']);g=read(Path(str(guide)+'.generation.json'))
    for ref in g['derivedFrom']:assert sha(Path(ref['file']))==ref['sha256']
    if not RESUME.exists():write(RESUME,{'schemaVersion':1,'owner':'right_resume_sol','tile':TID,'createdAtUtc':now(),'updatedAtUtc':now(),'authorization':str(AUTH),'authorizationSha256':sha(AUTH),'builtinOnly':True,'historicalFreezeUnmodified':'migration-freeze-right-20261011.json','status':'prepared_waiting_root_builtin_recovery_confirmation','inFlightRequests':[],'newOutputs':[],'selectedVersions':read(PROGRESS)['selectedVersions'],'preparedInheritedRequest':{'file':str(req),'sha256':sha(req),'promptSha256':sha(Path(r['promptPath'])),'guideSha256':sha(guide),'note':'Preserved exactly; historical frozen dispatch status is superseded by new authorization.'},'rootWestRow2Authority':'pending accepted r12_c12_p24 repair','formalAccepted':False})
    change_progress(status='resume_prepared_waiting_builtin_confirmation',productionFrozen=False,productionResumedAt=now(),resumeAuthority=str(AUTH),resumeRecord=RESUME.name,inFlightRequestCount=0,currentPatchDispatchStatus='prepared_not_submitted_waiting_root_confirmation',nextStep='After root builtin recovery confirmation, dispatch preserved p23v01, then continue p22. p21 requires accepted root west p24.')
    print(json.dumps({'status':'ready','prepared':str(req),'referenceHashesPassed':True}))
elif mode=='export':
    name=sys.argv[2];r=read(ROOT/'prompts'/f'{name}.request.json')
    for ref in r['references']:assert sha(Path(ref['file']))==ref['sha256']
    args={'prompt':Path(r['promptPath']).read_text(encoding='utf-8-sig'),'referenced_image_paths':[x['file'] for x in r['references']],'transparent_background':False}
    print(json.dumps(args,ensure_ascii=True))
elif mode=='dispatch':
    name=sys.argv[2];pid,ver=name.rsplit('_',1);assert pid.startswith(TID)
    assert read(RESUME).get('rootBuiltinRecoveryConfirmed'), 'Wait for root successful builtin confirmation.'
    r=read(ROOT/'prompts'/f'{name}.request.json')
    args={'prompt':Path(r['promptPath']).read_text(encoding='utf-8-sig'),'referenced_image_paths':[x['file'] for x in r['references']],'transparent_background':False}
    receipt=ROOT/'receipts'/f'{name}.json';assert not receipt.exists()
    write(receipt,{'tool':'image_gen.imagegen','route':'builtin','submittedAtUtc':now(),'resumeAuthorization':str(AUTH),'submittedArguments':args,'status':'submitted','returned':None,'savedOutputPath':None,'actualModel':None,'actualQuality':None})
    change_progress(status='generating',currentPatch=pid,currentPatchDispatchStatus='submitted',inFlightRequestCount=1,nextStep='Await builtin native result, save original byte-for-byte, then inspect exact core seams.')
    d=read(RESUME)
    for x in d.get('preparedRequests',[]):
        if x['id']==name:x.update({'requestSha256':sha(ROOT/'prompts'/f'{name}.request.json'),'promptSha256':sha(Path(r['promptPath'])),'guideSha256':r['references'][0]['sha256'],'dispatchStatus':'submitted','submittedAtUtc':now()})
    d.update({'status':'generating','inFlightRequests':[name],'updatedAtUtc':now()});write(RESUME,d)
    print(json.dumps({'receipt':str(receipt),'name':name}))
elif mode=='returned':
    name,source,hint=sys.argv[2:5];receipt=ROOT/'receipts'/f'{name}.json';r=read(receipt)
    assert r['status']=='submitted'
    r.update({'completedAtUtc':now(),'status':'succeeded','returned':{'output_hint':hint},'savedOutputPath':source});write(receipt,r)
elif mode=='gate':
    proof=sys.argv[2]
    change_resume(rootBuiltinRecoveryConfirmed=True,rootBuiltinRecoveryConfirmedAtUtc=now(),rootBuiltinRecoveryProof=proof,status='ready_to_dispatch')
    change_progress(status='ready_to_dispatch',currentPatch='r12_c13_p23',currentPatchDispatchStatus='prepared_not_submitted',nextStep='Dispatch prepared p23v01 with unchanged prompt and references.')
    print(json.dumps({'rootBuiltinRecoveryConfirmed':True,'proof':proof}))
elif mode=='failed':
    name,error=sys.argv[2:4];receipt=ROOT/'receipts'/f'{name}.json';r=read(receipt)
    r.update({'completedAtUtc':now(),'status':'failed','error':error});write(receipt,r)
    change_progress(status='builtin_failed',currentPatchDispatchStatus='failed',inFlightRequestCount=0,lastError=error,nextStep='Report builtin failure to root; preserve submitted receipt and prepared inputs; do not switch routes.')
    change_resume(status='builtin_failed',inFlightRequests=[],lastError={'id':name,'error':error,'atUtc':now()})
    print(json.dumps({'failed':name,'error':error}))
elif mode=='ingest':
    name=sys.argv[2];pid,ver=name.rsplit('_',1);assert pid.startswith(TID)
    req=read(ROOT/'prompts'/f'{name}.request.json');rp=ROOT/'receipts'/f'{name}.json';receipt=read(rp);src=Path(receipt['savedOutputPath']);out=ROOT/'native'/f'{name}.png';assert not out.exists()
    assert receipt['submittedArguments']['prompt'].replace('\r\n','\n')==Path(req['promptPath']).read_text(encoding='utf-8-sig')
    assert receipt['submittedArguments']['referenced_image_paths']==[r['file'] for r in req['references']]
    with Image.open(src) as im:im.load();size=list(im.size);fmt=im.format;imode=im.mode
    shutil.copy2(src,out)
    rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':size[0],'height':size[1],'format':fmt,'mode':imode,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'configSnapshot':read(PROGRESS)['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin host-managed tool; model and quality are not disclosed.','prompt':req['promptPath'],'promptSha256':sha(Path(req['promptPath'])),'references':req['references'],'evidence':{'toolReceipt':f'receipts/{name}.json','returnedFields':['image_url','output_hint'],'largeImageDataLogged':False},'coordinate':patch(pid),'resizedAfterGeneration':False,'status':'candidate_pending_visual_review' if size==[1254,1254] else 'rejected_wrong_native_dimensions_preserved'}
    write(Path(str(out)+'.generation.json'),rec)
    d=read(RESUME);d['newOutputs'].append({'id':name,'file':str(out),'sha256':sha(out),'sourceOutputPath':str(src),'pixels':size,'receipt':str(rp),'status':rec['status']});d.update({'status':'native_received','inFlightRequests':[],'updatedAtUtc':now()});write(RESUME,d)
    change_progress(status='native_received',generatedNativeCount=len(list((ROOT/'native').glob(TID+'*.png'))),currentPatch=pid,currentPatchDispatchStatus='saved',inFlightRequestCount=0,unsavedSuccessfulOutputCount=0,nextStep='Inspect saved native output and exact 1024 core joins before selecting it.')
    if size==[1254,1254]:
        core=QA/f'{name}.core1024.png'
        with Image.open(out) as im:im.crop((115,115,1139,1139)).save(core)
        write(QA/f'{name}.core1024.trace.json',{'source':str(out),'sourceSha256':sha(out),'crop':[115,115,1139,1139],'destination':str(core),'destinationSha256':sha(core),'resampled':False,'operation':'exact native 1024 core crop'})
    print(json.dumps({'file':str(out),'sha256':sha(out),'pixels':size,'sourceByteIdentical':sha(src)==sha(out),'coreTrace':str(QA/f'{name}.core1024.trace.json') if size==[1254,1254] else None}))
elif mode=='prepare':
    pid,ver,description=sys.argv[2:5];neighbors=sys.argv[5:];assert pid.startswith(TID)
    name=f'{pid}_{ver}';reqpath=ROOT/'prompts'/f'{name}.request.json';assert not reqpath.exists()
    import workflow
    workflow.context(pid,neighbors,ver)
    guide=ROOT/'guides'/f'{pid}.native-context-{ver}.png'
    refs=[{'file':guide.as_posix(),'sha256':sha(guide),'role':'EDIT TARGET / exact coordinate guide. Sharp adjacent overlap is immutable, blurry region requires native redraw. Guide not usable as final art.'}]
    refs+=read(ROOT/'references.json')
    template=(ROOT/'prompts/r12_c13_p23_v01.prompt.txt').read_text(encoding='utf-8-sig')
    start=template.index('Exact crop identity:');end=template.index('\n\nKeep clear crisp painted contours',start)
    p=patch(pid)
    block=f"Exact crop identity: {pid}. Global native extent {p['nativeGlobalBox']} in 57344 square map; overview extent {p['layoutReferenceBox']} in 1254 square reference. Core local [115,115,1139,1139). Never zoom out or invent a miniature island/building inside this small crop.\nLOCAL CONTENT AND GEOMETRY: {description}"
    prompt=template[:start]+block+template[end:]
    prompt=prompt.replace('A horizontal neighbor contributes its rightmost 230 pixels to this crop\'s leftmost 230 pixels; a vertical neighbor contributes its bottommost 230 pixels to this crop\'s topmost 230 pixels.','A west neighbor contributes its rightmost 230 pixels to this crop\'s leftmost 230 pixels; an east neighbor contributes its leftmost 230 pixels to this crop\'s rightmost 230 pixels; a north neighbor contributes its bottommost 230 pixels to this crop\'s topmost 230 pixels. Exact embedded sharp overlap geometry is the continuity authority.')
    pp=ROOT/'prompts'/f'{name}.prompt.txt';pp.write_text(prompt,encoding='utf-8')
    write(reqpath,{'promptPath':pp.as_posix(),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'preparedAtUtc':now(),'resumeAuthorization':str(AUTH),'dispatchStatus':'prepared_not_submitted'})
    d=read(RESUME);d.setdefault('preparedRequests',[]).append({'id':name,'request':str(reqpath),'requestSha256':sha(reqpath),'promptSha256':sha(pp),'guideSha256':sha(guide),'dispatchStatus':'prepared_not_submitted'});d['updatedAtUtc']=now();write(RESUME,d)
    change_progress(status='request_prepared',currentPatch=pid,currentPatchDispatchStatus='prepared_not_submitted',nextStep='View guide and actual neighbor references, then submit builtin request.')
    print(json.dumps({'name':name,'request':str(reqpath),'guide':str(guide),'references':[r['file'] for r in refs]}))
elif mode=='pairs':
    name=sys.argv[2];pid,ver=name.rsplit('_',1);p=ROOT/'native'/f'{name}.png';im=Image.open(p).convert('RGB');a=im.crop((115,115,1139,1139));items=[]
    for spec in sys.argv[3:]:
        side,neighbor=spec.split('=',1);n=ROOT/'native'/neighbor;ni=Image.open(n).convert('RGB').crop((115,115,1139,1139))
        if side=='north':size=(1024,512);nc=[0,768,1024,1024];tc=[0,0,1024,256];nd=[0,0];td=[0,256]
        elif side=='east':size=(512,1024);nc=[0,0,256,1024];tc=[768,0,1024,1024];nd=[256,0];td=[0,0]
        elif side=='west':size=(512,1024);nc=[768,0,1024,1024];tc=[0,0,256,1024];nd=[0,0];td=[256,0]
        else:raise ValueError(side)
        out=QA/f'{name}-{side}-core-seam.png';o=Image.new('RGB',size);o.paste(ni.crop(tuple(nc)),tuple(nd));o.paste(a.crop(tuple(tc)),tuple(td));out.parent.mkdir(parents=True,exist_ok=True);o.save(out)
        items.append({'file':str(out),'sha256':sha(out),'side':side,'neighbor':str(n),'neighborSha256':sha(n),'neighborCoreCrop':nc,'thisCoreCrop':tc,'neighborDestination':nd,'thisDestination':td,'resampled':False})
    write(QA/f'{name}-pairs.json',{'createdAtUtc':now(),'source':str(p),'sourceSha256':sha(p),'operation':'hard adjacent native 1024 core crop/paste, no resampling, no feather or paint','items':items,'status':'pending_visual_review'})
    print(json.dumps(items))
elif mode=='native_edit':
    name,body=sys.argv[2:4];neighbors=sys.argv[4:];pid,ver=name.rsplit('_',1);base=ROOT/'native'/body;box=patch(pid)['nativeGlobalBox'];out=ROOT/'guides'/f'{pid}.native-edit-{ver}.png';assert not out.exists()
    im=Image.open(base).convert('RGB');sources=[{'file':base.as_posix(),'sha256':sha(base),'role':'native coordinate-valid edit body; preserve content except requested correction'}];placements=[{'source':base.as_posix(),'sourceCrop':[0,0,1254,1254],'destination':[0,0]}]
    for neighbor in neighbors:
        np=ROOT/'native'/neighbor;nb=read(Path(str(np)+'.generation.json'))['coordinate']['nativeGlobalBox'];ni=Image.open(np).convert('RGB');inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])];assert inter[2]>inter[0] and inter[3]>inter[1]
        crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]];im.paste(ni.crop(tuple(crop)),tuple(dest));sources.append({'file':np.as_posix(),'sha256':sha(np),'role':'exact accepted adjacent overlap replaces prior body boundary'});placements.append({'source':np.as_posix(),'sourceCrop':crop,'destination':dest,'globalIntersection':inter})
    im.save(out);write(Path(str(out)+'.generation.json'),{'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'operation':'unscaled full native edit body plus exact accepted overlap crop/paste; reference guide only','derivedFrom':sources,'placements':placements,'usableAsFinalArt':False,'coordinate':patch(pid)})
    rp=ROOT/'prompts'/f'{name}.request.json';r=read(rp);r['references'][0]={'file':out.as_posix(),'sha256':sha(out),'role':'EDIT TARGET native coordinate-valid body plus exact accepted adjacent overlap. Make only requested local correction; preserve remaining geometry and scale.'}
    pp=Path(r['promptPath']);s=pp.read_text(encoding='utf-8-sig');start=s.index('Attached image 1');end=s.index('Attached adjacent native images',start);s=s[:start]+'Attached image 1 is the EDIT TARGET: detailed coordinate-valid native artwork with the exact accepted adjacent overlap pasted in place. Preserve all accepted boundary overlaps. Make ONLY the local correction specified below, leaving other existing scene elements fixed. Do not reproduce internal paste boundaries. Preserve crop, scale, viewpoint, objects and daylight. Output one complete native square crop, no comparison panel.\n'+s[end:];pp.write_text(s,encoding='utf-8');write(rp,r)
    print(json.dumps({'guide':out.as_posix(),'request':rp.as_posix()}))
elif mode=='select':
    name,note=sys.argv[2:4];pid,ver=name.rsplit('_',1);rc=pid[-2:];recp=ROOT/'native'/f'{name}.png.generation.json';r=read(recp);assert [r['width'],r['height']]==[1254,1254]
    prior=read(PROGRESS)['selectedVersions'].get(rc);rd=read(RESUME)
    for old in rd['newOutputs']:
        if prior and prior!=ver and old['id']==f'{pid}_{prior}':
            old['status']='superseded_preserved';old['supersededBy']=name;op=Path(old['file']+'.generation.json');orec=read(op);orec.update({'status':'superseded_preserved','supersededBy':name});write(op,orec)
    write(RESUME,rd)
    r.update({'status':'selected_local_visual_seams_passed','reviewedAtUtc':now(),'visualReviewNote':note});write(recp,r)
    d=read(PROGRESS);d['selectedVersions'][rc]=ver;d['usableNativeCount']=len(d['selectedVersions']);d['uniqueGeneratedPatchCoordinates']=len(d['selectedVersions']);d['missingPatchCoordinates']=[f'{row}{col}' for row in range(1,5) for col in range(1,5) if f'{row}{col}' not in d['selectedVersions']];d['status']='continuing';d['updatedAt']=now();write(PROGRESS,d)
    d=read(RESUME);d['selectedVersions'][rc]=ver
    for x in d['newOutputs']:
        if x['id']==name:x.update({'status':'selected_local_visual_seams_passed','reviewedAtUtc':now(),'visualReviewNote':note})
    d['updatedAtUtc']=now();write(RESUME,d)
    write(QA/f'{name}-visual-review.json',{'createdAtUtc':now(),'file':r['file'],'sha256':r['sha256'],'nativePixels':[1254,1254],'coreCrop':[115,115,1139,1139],'localVisualSeamsPassed':True,'note':note,'formalAccepted':False})
    print(json.dumps({'selected':name,'remaining':read(PROGRESS)['missingPatchCoordinates']}))
elif mode=='reject':
    name,note=sys.argv[2:4];recp=ROOT/'native'/f'{name}.png.generation.json';r=read(recp);r.update({'status':'rejected_preserved_visual_seam_failure','reviewedAtUtc':now(),'visualReviewNote':note});write(recp,r)
    d=read(RESUME)
    for x in d['newOutputs']:
        if x['id']==name:x.update({'status':'rejected_preserved_visual_seam_failure','reviewedAtUtc':now(),'visualReviewNote':note})
    d['updatedAtUtc']=now();write(RESUME,d)
    change_progress(status='repair_required',rejectedOutputCount=2+sum(x['status'].startswith('rejected') for x in d['newOutputs']),nextStep=note)
    write(QA/f'{name}-visual-review.json',{'createdAtUtc':now(),'file':r['file'],'sha256':r['sha256'],'nativePixels':[r['width'],r['height']],'coreCrop':[115,115,1139,1139],'localVisualSeamsPassed':False,'note':note,'formalAccepted':False,'preserved':True})
    print(json.dumps({'rejectedPreserved':name,'note':note}))
else:raise ValueError(mode)
