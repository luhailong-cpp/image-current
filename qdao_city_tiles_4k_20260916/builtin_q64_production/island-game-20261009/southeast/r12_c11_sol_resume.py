"""Exclusive r12_c11 resumption. Mechanically prepare inputs; never paint final art."""
from pathlib import Path
from PIL import Image
import json
from workflow import ROOT, read, write, sha, now, patch

AUTH = Path('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')
TILE = 'r12_c11'
PROGRESS = ROOT / 'progress-r12_c11.json'
RESUME = ROOT / 'production-resume-left-sol-20261012.json'

def audit_and_resume():
    authority = read(AUTH)
    assert authority['newArtworkGenerationAllowed'] and authority['builtinOnly']
    freeze = read(ROOT / 'migration-freeze-left-20261011.json')
    selection = read(ROOT / 'selection-r12_c11.json')['patchVersions']
    inventory = []
    for f in sorted((ROOT / 'native').glob(TILE + '_*.png')):
        rec = read(Path(str(f) + '.generation.json'))
        with Image.open(f) as im:
            dimensions, mode = list(im.size), im.mode
        assert dimensions == [1254, 1254]
        assert sha(f) == rec['sha256']
        assert sha(Path(rec['prompt'])) == rec['promptSha256']
        for ref in rec['references']:
            assert Path(ref['file']).exists() and sha(Path(ref['file'])) == ref['sha256']
        inventory.append({'file':str(f),'sha256':sha(f),'nativePixels':dimensions,'mode':mode,'sourceAndPromptHashesVerified':True})
    missing = [str(r)+str(c) for r in range(1,5) for c in range(1,5) if str(r)+str(c) not in selection]
    record = {'schemaVersion':1,'agent':'left_resume_sol','tile':TILE,'resumedAt':now(),'authority':str(AUTH),'authoritySha256':sha(AUTH),'route':'builtin','paidApiAllowed':False,'historicalFreeze':str(ROOT/'migration-freeze-left-20261011.json'),'historicalFreezeSha256':sha(ROOT/'migration-freeze-left-20261011.json'),'historicalFreezeUnmodified':True,'baselineNativeCount':freeze['actualNativeCount'],'baselineSelectedCoordinateCount':freeze['selectedCoordinateCount'],'actualNativeCount':len(inventory),'selectedVersions':selection,'missingCoordinates':missing,'nativeInventory':inventory,'status':'prepared_waiting_for_root_builtin_availability_confirmation','newGenerationAttempted':False,'pendingReview':['p21v03 water material continuity','p33v02 to p34v04 wood material continuity','complete native core mosaic and actual north/east/internal seams'],'inFlightRequests':[],'formalAcceptedCount':0,'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'nextStep':'Submit ordinary wooden bridge patch p13v02 after root confirms built-in availability; continue remaining four missing coordinates and necessary seam repair.'}
    assert not RESUME.exists(), 'Preserve initial resume record; update deliberately thereafter'
    write(RESUME,record)
    p=read(PROGRESS)
    p.update({'updatedAt':now(),'status':'resumed_preparing_inputs','productionResumeAuthority':str(AUTH),'productionResumeRecord':str(RESUME),'generatedNativeCount':len(inventory),'selectedCoordinateCount':len(selection),'missingPatches':[TILE+'_p'+x for x in missing],'inFlightRequests':[],'lastError':None,'nextStep':record['nextStep'],'fullyCovered4kCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0})
    write(PROGRESS,p)
    print(json.dumps({'nativeCount':len(inventory),'selectedCount':len(selection),'missing':missing,'resumeRecord':str(RESUME)}))

def prepare(rc,version,description):
    pid=TILE+'_p'+rc
    p=patch(pid);box=p['nativeGlobalBox']
    guide=ROOT/'guides'/f'{pid}.native-context-{version}.png'
    promptfile=ROOT/'prompts'/f'{pid}_{version}.prompt.txt'
    requestfile=ROOT/'prompts'/f'{pid}_{version}.request.json'
    assert not any(x.exists() for x in [guide,promptfile,requestfile,ROOT/'native'/f'{pid}_{version}.png'])
    base=ROOT/'guides'/f'{pid}.layout-only.png'
    im=Image.open(base).convert('RGB');sources=[];placements=[]
    def paste(file,nb,role):
        file=Path(file);src=Image.open(file).convert('RGB')
        inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
        if inter[2]<=inter[0] or inter[3]<=inter[1]:return
        crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]]
        im.paste(src.crop(crop),tuple(dest))
        sources.append({'file':str(file),'sha256':sha(file),'role':role})
        placements.append({'source':str(file),'sourceCrop':crop,'destination':dest,'globalIntersection':inter})
    def native(file,role):
        rec=read(Path(str(file)+'.generation.json'))
        assert [rec['width'],rec['height']]==[1254,1254]
        paste(file,rec['coordinate']['nativeGlobalBox'],role)
    r,c=map(int,rc)
    if r==1:
        for key,ver in {'41':'v02','42':'v01','43':'v02','44':'v01'}.items():native(ROOT/'native'/f'r11_c11_p{key}_{ver}.png','north accepted native halo')
        paste(ROOT/'tiles'/'r11_c11.candidate-v02.png',[40960,40960,45056,45056],'north accepted exact core authority')
    if c==4:
        for key,ver in {'11':'v03','21':'v01','31':'v02','41':'v01'}.items():
            f=ROOT/'native'/f'r12_c12_p{key}_{ver}.png'
            if f.exists():native(f,'east current approved native halo')
    selection=read(ROOT/'selection-r12_c11.json')['patchVersions']
    for nr,nc in [(r-1,c),(r,c+1),(r,c-1),(r+1,c)]:
        key=str(nr)+str(nc)
        if key in selection:native(ROOT/'native'/f'{TILE}_p{key}_{selection[key]}.png','selected adjacent native overlap')
    im.save(guide)
    write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'generatedAt':now(),'width':1254,'height':1254,'operation':'Mechanical unscaled crop and paste of real adjacent native overlap onto layout-only guide; reference only, never final art','usableAsFinalArt':False,'base':str(base),'baseSha256':sha(base),'derivedFrom':sources,'placements':placements,'globalBox':box})
    refs=[{'file':str(guide),'sha256':sha(guide),'role':'edit target: exact layout with current sharp adjacent native overlaps'}]+read(ROOT/'references.json')
    prompt=f'''Use case: precise-object-edit.
Asset type: one square daylight Q Daoist island game map patch, native 1254 x 1254 pixels.
Primary request: Render the unfinished soft area of image 1 as crisp matching painted game art. Keep its sharp surrounding overlap bands fixed in their existing coordinates. Continue all timber edges, water openings and light seamlessly through these bands. Output one opaque square patch at the same scale and framing.
Input images: Image 1 is the exact coordinate edit target. Image 2 is full-island layout authority. Image 3 is materials only. Image 4 is approved painting style only.
Exact patch: {pid}; global native extent {p['nativeGlobalBox']} within the 57344 square map. The final 1024 square core is local [115,115,1139,1139).
Scene and geometry: {description}
Style and light: Rounded elegant hand-painted forms, clear contours, warm gold and timber, bright blue water, soft daylight shadows. Match existing sharp neighboring pixels in image 1. Keep the water openings visible and timber geometry continuous. Keep this close crop without zooming or recomposing. No lettering, interface or watermark.
'''
    promptfile.write_text(prompt,encoding='utf-8')
    req={'promptPath':str(promptfile),'promptSha256':sha(promptfile),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None},'preparedAt':now(),'status':'prepared_not_submitted'}
    write(requestfile,req)
    resume=read(RESUME);resume.update({'updatedAt':now(),'nextRequest':str(requestfile),'currentPatch':pid,'currentVersion':version});write(RESUME,resume)
    prog=read(PROGRESS);prog.update({'updatedAt':now(),'currentPatch':pid,'currentVersion':version,'status':'request_prepared_waiting_builtin_confirmation','nextRequest':str(requestfile)});write(PROGRESS,prog)
    print(json.dumps({'request':str(requestfile),'guide':str(guide),'references':[x['file'] for x in refs]}))

def receive(rc,version,source):
    import workflow
    workflow.PROGRESS_FILE=PROGRESS
    pid=TILE+'_p'+rc
    src=Path(source);out=ROOT/'native'/f'{pid}_{version}.png'
    assert src.exists() and not out.exists()
    with Image.open(src) as im:
        assert im.size==(1254,1254) and im.mode=='RGB'
    receipt=ROOT/'receipts'/f'{pid}_{version}.json'
    assert not receipt.exists()
    request=ROOT/'prompts'/f'{pid}_{version}.request.json'
    req=read(request)
    assert sha(Path(req['promptPath']))==req['promptSha256']
    for ref in req['references']:assert sha(Path(ref['file']))==ref['sha256']
    write(receipt,{'patchId':pid,'version':version,'receivedAt':now(),'tool':'image_gen.imagegen','route':'builtin','status':'success','request':str(request),'requestSha256':sha(request),'promptPath':req['promptPath'],'promptSha256':req['promptSha256'],'references':req['references'],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'nativePixels':[1254,1254],'mode':'RGB','returnedFields':['image_url','output_hint'],'returnedSourcePathFromOutputHint':str(src),'actualModel':None,'actualQuality':None,'unverifiedReason':'Built-in host managed model/quality not disclosed.','largeImageDataLogged':False})
    workflow.ingest(pid,version,str(src),str(receipt))
    p=read(PROGRESS);p.update({'updatedAt':now(),'inFlightRequests':[],'lastError':None,'status':'native_received_pending_neighbor_review'});write(PROGRESS,p)
    j=read(RESUME);j.update({'updatedAt':now(),'status':'native_received_pending_neighbor_review','actualNativeCount':len(list((ROOT/'native').glob(TILE+'_*.png'))),'inFlightRequests':[],'lastNative':str(out),'lastNativeSha256':sha(out),'lastReceipt':str(receipt),'nextStep':'Inspect received native and actual neighbor core seams, then continue missing coordinates.'});write(RESUME,j)

def submit(rc,version):
    pid=TILE+'_p'+rc;f=ROOT/'prompts'/f'{pid}_{version}.request.json';req=read(f)
    assert not (ROOT/'native'/f'{pid}_{version}.png').exists()
    assert sha(Path(req['promptPath']))==req['promptSha256']
    for ref in req['references']:assert sha(Path(ref['file']))==ref['sha256']
    req.update({'status':'submitted_in_flight','submittedAt':now()});write(f,req)
    flight=[{'patch':pid,'version':version,'route':'builtin','submittedAt':req['submittedAt']}]
    p=read(PROGRESS);p.update({'status':'generating','updatedAt':now(),'inFlightRequests':flight,'lastError':None,'currentPatch':pid,'currentVersion':version});write(PROGRESS,p)
    j=read(RESUME);j.update({'status':'generating','updatedAt':now(),'inFlightRequests':flight,'newGenerationAttempted':True,'currentPatch':pid,'currentVersion':version});write(RESUME,j)
    print({'submitted':pid+'_'+version})

def prepare_repair(rc,version,target_version,description):
    prepare(rc,version,'Keep the existing dock geometry and painted water exactly as in the native target. '+description)
    pid=TILE+'_p'+rc;f=ROOT/'prompts'/f'{pid}_{version}.request.json';req=read(f)
    target=ROOT/'native'/f'{pid}_{target_version}.png'
    req['references']=[{'file':str(target),'sha256':sha(target),'role':'actual native edit target; all geometry and unmentioned pixels must remain fixed'}]+req['references']
    prompt=f'''Use case: precise-object-edit.
Edit image 1 only at its exact native 1254 x 1254 framing. It is the existing daylight Q-painted wooden dock patch {pid}. Image 2 is an exact coordinate continuity guide containing the current selected neighboring native overlap bands. Last three images are full-map layout, material and approved painting-style references.
Primary request: {description}
Keep every timber contour, post width, beam joint, platform edge, water pattern and reflected post shadow in the same position. Keep north, south, left and right overlap geometry fixed. Keep all unmentioned content identical. Retain the existing painting style and bright daylight. Do not zoom, shift, add objects, lettering, interface or watermark. Output one opaque square 1254 x 1254 image.
'''
    Path(req['promptPath']).write_text(prompt,encoding='utf-8');req['promptSha256']=sha(Path(req['promptPath']));write(f,req)
    print({'repairRequest':str(f)})

if __name__=='__main__':
    import sys
    if sys.argv[1]=='resume':audit_and_resume()
    elif sys.argv[1]=='prepare':prepare(*sys.argv[2:])
    elif sys.argv[1]=='receive':receive(*sys.argv[2:])
    elif sys.argv[1]=='submit':submit(*sys.argv[2:])
    elif sys.argv[1]=='repair':prepare_repair(*sys.argv[2:])
