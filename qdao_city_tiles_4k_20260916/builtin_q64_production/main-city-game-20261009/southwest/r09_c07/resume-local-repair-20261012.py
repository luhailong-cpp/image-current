from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, shutil, importlib.util
import numpy as np
from PIL import Image

B=Path(__file__).resolve().parent.parent
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('native_local_quilting',B/'local_repairs.py')
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):
    p=Path(p);assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def png(p,a):
    p=Path(p);assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(a).save(p)
    assert np.array_equal(np.array(Image.open(p)),a)
    return {'file':str(p),'sha256':sha(p),'width':a.shape[1],'height':a.shape[0],'mode':'RGB','format':'PNG','sourceResampling':False}
def prepare(tile,name,assembly_name,l,t,prompt_name):
    assert tile in {f'r{r:02d}_c{c:02d}' for r in range(9,17) for c in (7,8)}
    l,t=int(l),int(t);assert 0<=l<=2957 and 0<=t<=2957
    a=read(assembly_name);assert a['tile']==tile
    d=B/tile/'repairs-resume-20261012'/name;assert not d.exists();d.mkdir(parents=True)
    src=a['contextOutput']['file'];assert sha(src)==a['contextOutput']['sha256']
    arr=np.array(Image.open(src).convert('RGB'));assert arr.shape==(4326,4326,3)
    crop=arr[t+115:t+1369,l+115:l+1369].copy();target=png(d/'input.png',crop)
    contract=read(B.parent/'production-contract.json')
    refs=[{'file':target['file'],'sha256':target['sha256'],'role':'edit target: exact native 1254 crop of assembled candidate, no resampling'}]
    for key in ('layoutReference','detailStyleReference','primaryStyleReference'):
        p=contract[key];refs.append({'file':p,'sha256':sha(p),'role':key})
    p=B/'pipeline-tools/local-continuation-audit-20261011/r12-firstrow/ref-stone-context.png'
    refs.append({'file':str(p),'sha256':sha(p),'role':'quiet natural stone finish only; copy no geometry, seams or red scraps'})
    prefix=Path(prompt_name).read_text(encoding='utf-8-sig')
    prompt=prefix+'\n\nUse case: precise-object-edit. EDIT IMAGE 1 ONLY. Output one opaque native 1254x1254 PNG at exactly this framing, no resizing, zoom, crop change, recentering or scene expansion. Images 2, 3 and 4 are mandatory approved city geometry, daylight natural-grey materials and polished Q Daoist painting style only; copy no complete scene, UI, text, people, moon or props. Image 5 is quiet smooth natural stone surface finish only; copy no geometry, seams or red paper. Preserve all original geometry and all outer border pixels except the explicitly described defect. Keep existing partial decorations at original huge scale; no added complete motifs or new grout network.\n'
    pp=d/'prompt.txt';pp.write_text(prompt,encoding='utf-8')
    ox,oy=a['selectedCoreWorldBox'][:2]
    r={'tile':tile,'name':name,'prompt':prompt,'promptFile':str(pp),'promptSha256':sha(pp),'referenced_image_paths':[v['file'] for v in refs],'references':refs,'transparent_background':False,'inputAssembly':str(Path(assembly_name)),'inputAssemblySha256':sha(assembly_name),'inputContext':src,'inputContextSha256':sha(src),'inputCandidate':a['output']['file'],'inputCandidateSha256':a['output']['sha256'],'candidateBox':[l,t,l+1254,t+1254],'contextBox':[l+115,t+115,l+1369,t+1369],'coordinates':{'contextWorldBox':[ox+l,oy+t,ox+l+1254,oy+t+1254],'nativeCoreBox':[115,115,1139,1139]},'requestedNativePixels':[1254,1254],'sourceResampling':False,'preparedAtUtc':now(),'actualModel':None,'actualQuality':None,'productionResumeEvidence':{'file':'D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json','sha256':sha('D:/work/image/docs/MAP_PRODUCTION_RESUME_20261012.json')}}
    write(d/'request.json',r);print(json.dumps({'request':str(d/'request.json'),'target':str(d/'input.png')}))
def ingest(tile,name,source,started):
    d=B/tile/'repairs-resume-20261012'/name;r=read(d/'request.json');source=Path(source)
    dest=d/'native.png';assert not dest.exists();shutil.copy2(source,dest);assert sha(dest)==sha(source)
    with Image.open(dest) as im:pixels=list(im.size);mode=im.mode;fmt=im.format;opaque=mode!='RGBA' or im.getextrema()[3]==(255,255)
    receipt={'tool':'image_gen.imagegen','status':'returned_image','sourceOutputPath':str(source),'sourceOutputSha256':sha(source),'savedUnmodifiedOriginal':str(dest),'nativePixels':pixels,'mode':mode,'format':fmt,'startedAtUtc':started,'recordedAtUtc':now(),'actualModel':None,'actualQuality':None,'apiUsed':False,'visualDisposition':'pending_visual_review','request':str(d/'request.json'),'output_hint':f'Generated images are saved to {source.parent} as {source} by default.'}
    write(d/'tool-result.json',receipt)
    if pixels!=[1254,1254] or fmt!='PNG' or not opaque:raise ValueError('Saved unchanged returned original, wrong native dimensions/format/alpha; not selected')
    g={**r,'file':str(dest),'sha256':sha(dest),'width':1254,'height':1254,'mode':mode,'format':fmt,'route':'builtin','tool':'image_gen.imagegen','sourceOutputPath':str(source),'sourceOutputSha256':sha(source),'nativePixelsPreserved':True,'resizedAfterGeneration':False,'evidence':{'toolReceipt':str(d/'tool-result.json'),'toolReceiptSha256':sha(d/'tool-result.json')},'actualModel':None,'actualQuality':None,'formalAccepted':False,'generatedAt':now()}
    write(d/'generation.json',g);print(json.dumps({'native':str(dest),'sha256':sha(dest),'pixels':pixels}))
def apply(tile,name,*window):
    d=B/tile/'repairs-resume-20261012'/name;g=read(d/'generation.json')
    for ref in g['references']:assert sha(ref['file'])==ref['sha256']
    assert sha(g['inputAssembly'])==g['inputAssemblySha256'] and sha(g['inputContext'])==g['inputContextSha256']
    a=read(g['inputAssembly']);ctx=np.array(Image.open(g['inputContext']).convert('RGB'));original=ctx.copy()
    l,t,rr,bb=g['contextBox'];old=ctx[t:bb,l:rr].copy();new=np.array(Image.open(g['file']).convert('RGB'));assert old.shape==new.shape==(1254,1254,3)
    if window:
        ml,mt,mr,mb=map(int,window);assert 0<=ml<mr<=1254 and 0<=mt<mb<=1254
        h,w=mb-mt,mr-ml;assert min(h,w)>4
        yy,xx=np.indices((h,w));dist=np.minimum(np.minimum(yy,h-1-yy),np.minimum(xx,w-1-xx))
        section_alpha=np.minimum(dist,2).astype(np.uint32)*255//2
        alpha=np.zeros((1254,1254),np.uint8);alpha[mt:mb,ml:mr]=section_alpha.astype(np.uint8)
        weight=alpha.astype(np.uint32)[...,None]
        mixed=((old.astype(np.uint32)*(255-weight)+new.astype(np.uint32)*weight+127)//255).astype(np.uint8)
        assert np.array_equal(mixed[alpha==0],old[alpha==0]) and np.array_equal(mixed[alpha==255],new[alpha==255])
        details={'method':'explicit native rectangle crop with bounded edge feather','maskWindowInPatch':[ml,mt,mr,mb],'maximumFeatherRadiusPixels':2,'outsideRepairMaskPixelsPreserved':True,'selectedNativeInteriorPixelsPreservedExactly':True,'alphaSha256Uint8RowMajor':hashlib.sha256(alpha.tobytes()).hexdigest(),'sourceResampling':False,'blur':False,'geometryWarping':False,'colorAdjustment':False}
    else:
        mixed,details=q.quilt(old,new,2)
    ctx[t:bb,l:rr]=mixed
    assert np.array_equal(ctx[:t],original[:t]) and np.array_equal(ctx[bb:],original[bb:]) and np.array_equal(ctx[t:bb,:l],original[t:bb,:l]) and np.array_equal(ctx[t:bb,rr:],original[t:bb,rr:])
    out=d/('integrated-masked-20261012-v02' if window else 'integrated');context=png(out/(tile+'.candidate.context.png'),ctx);core=png(out/(tile+'.candidate.png'),ctx[115:4211,115:4211].copy())
    step={'name':name,'generationRecord':str(d/'generation.json'),'generationRecordSha256':sha(d/'generation.json'),'candidateBox':g['candidateBox'],'contextBox':g['contextBox'],'native':g['file'],'nativeSha256':g['sha256'],'actualNativePixels':[1254,1254],'inputAssembly':g['inputAssembly'],'inputAssemblySha256':g['inputAssemblySha256'],'inputContextSha256':g['inputContextSha256'],'outputContextSha256':context['sha256'],'outputCandidateSha256':core['sha256'],'outsideRepairBoxPixelsPreserved':True,'quilting':details,'actualModel':None,'actualQuality':None,'visualQa':'pending'}
    a.update(createdAtUtc=now(),contextOutput=context,output=core,status='repaired_candidate_pending_visual_and_external_QA',formalAccepted=False,actualModel=None,actualQuality=None,sourceResampling=False)
    a['localNativeRepairs']=a.get('localNativeRepairs',[])+[step]
    a['visualQa']={'status':'pending','internalGeometryReviewed':False,'externalTileSeamsReviewed':False}
    a['baseNativeAssembly']=a.get('baseNativeAssembly',{'file':g['inputAssembly'],'sha256':g['inputAssemblySha256']})
    a['repairComposition']={'method':'bounded native local crop quilting','sourceResampling':False,'maximumFeatherRadiusPixels':2,'colorAdjustment':False,'blur':False,'geometryWarping':False,'outsideRepairBoxPixelsPreserved':True,'coreEqualsContextCrop':True}
    if window:png(out/'alpha.png',alpha)
    write(out/'assembly.json',a);write(d/('repair-assembly-masked.json' if window else 'repair-assembly.json'),step)
    print(json.dumps({'assembly':str(out/'assembly.json'),'candidate':core,'context':context,'formalAccepted':False}))
if __name__=='__main__':
    {'prepare':prepare,'ingest':ingest,'apply':apply}[sys.argv[1]](*sys.argv[2:])
