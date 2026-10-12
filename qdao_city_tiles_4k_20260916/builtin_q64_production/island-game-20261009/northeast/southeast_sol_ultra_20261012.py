from native_work import *
import re, sys
mode, ident = sys.argv[1:3]
assert ident.startswith(('r05_c14_', 'r06_c14_'))
if mode == 'ingest':
    src=Path(sys.argv[3]); dest=ZONE/'native'/f'{ident}.png'
    if dest.exists():
        assert sha(dest)==sha(src), 'Existing PNG differs: never overwrite'
    else: shutil.copy2(src,dest)
    rp=dest.with_suffix('.png.generation.json');assert not rp.exists(), 'Existing generation record'
    with Image.open(dest) as im: size=list(im.size);fmt=im.format;imode=im.mode
    assert size==[1254,1254], 'Unexpected native size'
    p=patch(ident); cp=ROOT/'config/image-generation.json'
    rec={'id':ident,'file':dest.as_posix(),'sha256':sha(dest),'generatedAt':now(),'nativeWidth':size[0],'nativeHeight':size[1],'format':fmt,'mode':imode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(cp) if cp.exists() else None,'configSnapshotNote':'Local preferences are not evidence of host model or quality; current config file absent' if not cp.exists() else 'Local preference snapshot only, unverified host execution','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool exposes no model/quality selectors or verifiable model/quality result metadata.','prompt':(ZONE/'prompts'/f'{ident}.prompt.txt').as_posix(),'references':read(ZONE/'prompts'/f'{ident}.inputs.json'),'evidence':{'receipt':(ZONE/'receipts'/f'{ident}.tool.json').as_posix(),'originalToolPath':src.as_posix(),'fields':['output_hint'],'nativeSizeMeasuredBy':'Pillow PNG decode'},'coreWorldBox':p['coreWorldBox'],'nativeWorldBox':p['nativeWorldBox'],'coreCrop':p['coreCrop'],'resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'candidate_unreviewed','internalSeams':'unreviewed','externalSeams':'unreviewed'}
    write(rp,rec);print(json.dumps({'file':dest.as_posix(),'size':size,'sha256':rec['sha256']}))
elif mode == 'reject':
    p=ZONE/'native'/f'{ident}.png.generation.json';d=read(p);d.update(status='rejected_preserved',reviewNote=' '.join(sys.argv[3:]),reviewedAtUtc=now());write(p,d)
elif mode == 'accept':
    note=' '.join(sys.argv[3:])
    recpath=ZONE/'native'/f'{ident}.png.generation.json'
    rec=read(recpath)
    rec.update(status='usable_internal_reviewed', internalSeams='passed_reviewed_available_neighbors', reviewNote=note, reviewedAtUtc=now())
    write(recpath,rec)
    tid='_'.join(ident.split('_')[:2]); p=ZONE/f'selection-{tid}.json'
    sel=read(p) if p.exists() else {'tileId':tid,'cores':[[None]*4 for _ in range(4)],'overlays':[],'formalAccepted':False,'actualModel':None,'actualQuality':None}
    r,c=map(int,re.search(r'_p(\d{2})_(\d{2})',ident).groups())
    sel['cores'][r-1][c-1]=ident;sel['updatedAtUtc']=now();write(p,sel)
    for p in (ZONE/'qa').glob('*__'+ident+'.json'):
        d=read(p);d.update(status='passed_visual_100pct',geometryChecks={'note':note},reviewedAtUtc=now());write(p,d)
    cross=ZONE/'qa'/f'cross_{ident}.json'
    if cross.exists():
        d=read(cross);d.update(status='passed_visual_100pct',note=note,reviewedAtUtc=now());write(cross,d)
    write(ZONE/'qa'/f'{ident}.review.json',{'id':ident,'sha256':sha(ZONE/'native'/f'{ident}.png'),'status':rec['status'],'note':note,'reviewedAtUtc':now(),'formalAccepted':False})
    print(ident,rec['status'])
elif mode == 'crosspass':
    p=ZONE/'qa'/f'cross_{ident}.json';d=read(p);d.update(status='passed_visual_100pct',note=' '.join(sys.argv[3:]),reviewedAtUtc=now());write(p,d)
elif mode == 'checkpoint':
    tid='_'.join(ident.split('_')[:2]); sel=read(ZONE/f'selection-{tid}.json')
    write(ZONE/'qa'/f'{tid}-southeast-sol-ultra-checkpoint-20261012.json',{'worker':'southeast_sol_ultra','savedAtUtc':now(),'authorization':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json','selection':sel,'selectedCoreCount':sum(bool(v) for row in sel['cores'] for v in row),'lastSelected':ident,'builtinOnly':True,'actualModel':None,'actualQuality':None,'formalAccepted':False,'historicalFreezeModified':False})
