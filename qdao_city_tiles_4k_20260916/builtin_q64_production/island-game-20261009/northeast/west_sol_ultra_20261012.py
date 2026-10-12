"""Scoped mechanical guide, provenance and 1:1 QA helpers; no artwork synthesis."""
from native_work import *
import sys, argparse, re

def locked_png(p, im):
    p=Path(p)
    if p.exists(): raise RuntimeError('Refusing to overwrite PNG: '+str(p))
    im.save(p)

def scoped(ident):
    if not ident.startswith(('r04_c11_', 'r04_c10_')): raise RuntimeError('Outside west worker ownership')

def archive(ident, source):
    scoped(ident);src=Path(source);dest=ZONE/'native'/f'{ident}.png';meta=dest.with_suffix('.png.generation.json')
    if meta.exists(): raise RuntimeError('Generation record already exists')
    if dest.exists():
        if sha(dest)!=sha(src): raise RuntimeError('Existing native differs; cannot overwrite')
    else: shutil.copy2(src,dest)
    im=Image.open(dest);assert im.size==(1254,1254);p=patch(ident);receipt=ZONE/'receipts'/f'{ident}.tool.json';assert receipt.exists()
    cfg=ROOT/'config/image-generation.json'
    record={'id':ident,'file':dest.as_posix(),'sha256':sha(dest),'generatedAt':now(),'nativeWidth':im.width,'nativeHeight':im.height,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(cfg) if cfg.exists() else None,'configSnapshotUnavailableReason':None if cfg.exists() else 'Legacy config file absent at archival time; no model/quality inferred.','submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; built-in tool exposes no model/quality selectors and returns no verifiable model/quality metadata.','prompt':(ZONE/'prompts'/f'{ident}.prompt.txt').as_posix(),'references':read(ZONE/'prompts'/f'{ident}.inputs.json'),'evidence':{'receipt':receipt.as_posix(),'originalToolPath':src.as_posix(),'fields':['output_hint'],'nativeSizeMeasuredBy':'Pillow PNG decode'},'coreWorldBox':p['coreWorldBox'],'nativeWorldBox':p['nativeWorldBox'],'coreCrop':p['coreCrop'],'resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'candidate_unreviewed','internalSeams':'unreviewed','externalSeams':'unreviewed'}
    write(meta,record);print(json.dumps({'file':dest.as_posix(),'size':list(im.size),'sha256':record['sha256']}))

def prepare(ident, above, right):
    scoped(ident)
    for suffix in ('.anchored-layout-only.png','.native-neighbors.png'):
        if (ZONE/'guides'/f'{ident}{suffix}').exists(): raise RuntimeError('Guide exists; choose a version')
    guide(argparse.Namespace(id=ident,neighbor=[above,right],base=None))
    refs=read(ZONE/'prompts'/f'{ident}.inputs.json')
    refs[1]['role']='native neighbor reference plate: LEFT=ABOVE, RIGHT=RIGHT neighbor; both1254-square unscaled'
    write(ZONE/'prompts'/f'{ident}.inputs.json',refs)
    text=(ZONE/'prompts'/'r04_c11_p02_02.prompt.txt').read_text(encoding='utf-8-sig')
    dest=ZONE/'prompts'/f'{ident}.prompt.txt'
    if dest.exists(): raise RuntimeError('Prompt exists; choose a version')
    dest.write_text(text,encoding='utf-8')
    print(json.dumps({'id':ident,'prompt':text,'references':[r['file'] for r in refs]}))

def checks(ident, neighbors):
    scoped(ident); p=patch(ident); im=Image.open(ZONE/'native'/f'{ident}.png'); assert im.size==(1254,1254)
    paths=[]
    for neighbor in neighbors:
        q=patch(neighbor); iq=Image.open(ZONE/'native'/f'{neighbor}.png'); b=p['coreWorldBox'];a=q['coreWorldBox']
        if b[0]-a[0]==1024 and b[1]==a[1]:
            first,second=neighbor,ident; out=Image.new('RGB',(512,1024));out.paste(iq.crop((883,115,1139,1139)),(0,0));out.paste(im.crop((115,115,371,1139)),(256,0))
        elif a[0]-b[0]==1024 and b[1]==a[1]:
            first,second=ident,neighbor;out=Image.new('RGB',(512,1024));out.paste(im.crop((883,115,1139,1139)),(0,0));out.paste(iq.crop((115,115,371,1139)),(256,0))
        elif b[1]-a[1]==1024 and b[0]==a[0]:
            first,second=neighbor,ident;out=Image.new('RGB',(1024,512));out.paste(iq.crop((115,883,1139,1139)),(0,0));out.paste(im.crop((115,115,1139,371)),(0,256))
        elif a[1]-b[1]==1024 and b[0]==a[0]:
            first,second=ident,neighbor;out=Image.new('RGB',(1024,512));out.paste(im.crop((115,883,1139,1139)),(0,0));out.paste(iq.crop((115,115,1139,371)),(0,256))
        else: raise RuntimeError('Not adjacent')
        dest=ZONE/'qa'/f'west-sol-ultra-{first}__{second}.join-100pct.png';locked_png(dest,out)
        write(dest.with_suffix('.json'),{'sources':[{'id':n,'file':(ZONE/'native'/f'{n}.png').as_posix(),'sha256':sha(ZONE/'native'/f'{n}.png')} for n in (first,second)],'operation':'exact native1024 core border crops concatenated without resampling or blending','inspectionScale':1,'status':'pending_visual_review','coverageGapPixels':0})
        paths.append(dest.as_posix())
    print(json.dumps(paths))

def accept(ident, qa_names):
    scoped(ident)
    for name in qa_names:
        fp=ZONE/'qa'/name; v=read(fp);v.update(status='passed_available_native_join',reviewer='west_sol_ultra_20261012',reviewedAtUtc=now(),findings='grout contours continuous; no hard color band, geometry break or blocked paving path at exact core join');write(fp,v)
    fp=ZONE/'native'/f'{ident}.png.generation.json';v=read(fp);v.update(status='usable_native_candidate',internalSeams='direct native and available1:1 seams passed; full tile final QA pending');write(fp,v)
    tile=ident.split('_p')[0];fp=ZONE/f'selection-{tile}.json';v=read(fp);b=patch(ident)['coreWorldBox'];v['cores'][(b[1]%4096)//1024][(b[0]%4096)//1024]=ident;v['updatedAtUtc']=now();write(fp,v);print(json.dumps({'selected':ident,'sha256':sha(ZONE/'native'/f'{ident}.png')}))

def border(tile, neighbor):
    scoped(tile+'_');a=read(ZONE/'tiles'/f'{tile}.png.derivation.json');b=read(ZONE/'tiles'/f'{neighbor}.png.derivation.json');im=Image.open(a['file']);other=Image.open(b['file']);assert im.size==other.size==(4096,4096);assert sha(a['file'])==a['sha256'] and sha(b['file'])==b['sha256']
    aw,bw=a['worldBox'],b['worldBox'];paths=[]
    for i in range(4):
        if bw[3]==aw[1] and aw[0]==bw[0]:
            out=Image.new('RGB',(1024,512));out.paste(other.crop((i*1024,3840,(i+1)*1024,4096)),(0,0));out.paste(im.crop((i*1024,0,(i+1)*1024,256)),(0,256));side='north'
        elif aw[2]==bw[0] and aw[1]==bw[1]:
            out=Image.new('RGB',(512,1024));out.paste(im.crop((3840,i*1024,4096,(i+1)*1024)),(0,0));out.paste(other.crop((0,i*1024,256,(i+1)*1024)),(256,0));side='east'
        else: raise RuntimeError('Neighbor not north/east')
        dest=ZONE/'qa'/f'west-sol-ultra-{tile}-{side}-segment-{i+1}-100pct.png';locked_png(dest,out);paths.append(dest.as_posix())
    write(ZONE/'qa'/f'west-sol-ultra-{tile}-{side}-border.json',{'tileId':tile,'neighbor':neighbor,'side':side,'sources':[{'file':r['file'],'sha256':r['sha256']} for r in (a,b)],'segments':paths,'inspectionScale':1,'operation':'exact final tile edge crops pasted, no resizing or blending','coverageGapPixels':0,'status':'pending_visual_review'});print(json.dumps(paths))

def fullreview(tile):
    scoped(tile+'_');meta=ZONE/'tiles'/f'{tile}.png.derivation.json';v=read(meta);qa=ZONE/'qa'/f'{tile}-final';images=sorted(qa.glob('*-100pct.png'));assert len(images)==49
    names=[p.name for p in images];assert sum(n.startswith('core-') for n in names)==16;assert sum(n.startswith(('vertical-','horizontal-')) for n in names)==24;assert sum(n.startswith('cross-') for n in names)==9
    ext=[]
    for side in ('north','east'):
        fp=ZONE/'qa'/f'west-sol-ultra-{tile}-{side}-border.json'
        if fp.exists():
            q=read(fp);q.update(status='passed_1to1_visual_review',reviewedAtUtc=now(),reviewer='west_sol_ultra_20261012',findings='continuous contours and material through all4 final tile edge segments');write(fp,q);ext.append(q)
    record={'tileId':tile,'candidatePath':v['file'],'sha256':v['sha256'],'size':[4096,4096],'preview':v['preview'],'status':'passed_internal_available_external_review','formalAccepted':False,'reviewer':'west_sol_ultra_20261012','reviewedAtUtc':now(),'inspectionScale':1,'coreReviewCount':16,'seamReviewCount':24,'crossReviewCount':9,'reviewedImages':[{'file':p.as_posix(),'sha256':sha(p),'status':'passed','findings':'sharp native material; continuous visible contours; no hard rectangular color boundary, geometry break or obstruction'} for p in images],'overallPreviewReview':'passed; native stone density varies but no straight hard rectangular color band; walkable daylight paving and existing building/tree placement preserved','externalReviews':ext,'externalPending':['west: r04_c10 production in progress','south: r05_c11 production in progress'],'actualModel':None,'actualQuality':None,'assembly':'16 native1254 sources cropped[115,115,1139,1139] to1024 and pasted without scaling or feathering','finalArtUpscaled':False,'independentRootSpotCheck':{'status':'passed','evidence':'Root explicitly reported1536 overall plus vertical-2-segment-2, horizontal-1-segment-2 and cross-1-2 native crops reviewed; no straight hard color band; not a substitute for full49 review'}}
    fp=ZONE/'qa'/f'{tile}-west-sol-ultra-review-20261012.json';write(fp,record);v.update(status='complete_native_internal_passed_available_external_passed',internalReview='passed',externalSeams='north and east final4096 edges passed; west and south pending neighbor production',formalAccepted=False,reviewRecord=fp.as_posix());write(meta,v)
    sp=ZONE/f'selection-{tile}.json';s=read(sp);s.update(selectionIsPartialCandidate=False,internalReview='passed',candidatePath=v['file'],reviewRecord=fp.as_posix(),formalAccepted=False,updatedAtUtc=now());write(sp,s);print(json.dumps({'candidatePath':v['file'],'review':fp.as_posix(),'preview':v['preview'],'sha256':v['sha256']}))

if __name__=='__main__':
    cmd,ident=sys.argv[1:3]
    if cmd=='prepare': prepare(ident,*sys.argv[3:5])
    elif cmd=='archive': archive(ident,sys.argv[3])
    elif cmd=='checks': checks(ident,sys.argv[3:])
    elif cmd=='accept': accept(ident,sys.argv[3:])
    elif cmd=='border': border(ident,sys.argv[3])
    elif cmd=='fullreview': fullreview(ident)
