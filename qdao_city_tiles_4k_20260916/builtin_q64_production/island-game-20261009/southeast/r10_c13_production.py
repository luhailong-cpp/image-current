"""r10_c13-only guide, request and native evidence helpers. No image synthesis."""
from pathlib import Path
from PIL import Image
from workflow import ROOT,read,write,sha,now,context,patch
import sys,json,shutil,subprocess,os,runpy,workflow
TID='r10_c13'; prog=ROOT/f'progress-{TID}.json'
mode=sys.argv[1]
if mode=='prepare':
    plan=next(x for x in read(ROOT/'coordinate-plan.json')['tiles'] if x['id']==TID)
    ref=read(ROOT/'references.json')[0]
    with Image.open(ref['file']) as im:
        for p in plan['patches']:
            out=ROOT/'guides'/f"{p['id']}.layout-only.png"
            if out.exists():continue
            im.transform((1254,1254),Image.Transform.EXTENT,tuple(p['layoutReferenceBox']),Image.Resampling.BICUBIC).save(out)
            write(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'operation':'fractional-coordinate overview crop enlargement, guide ONLY; never final pixels','derivedFrom':[ref],'sourceCropBox':p['layoutReferenceBox'],'globalBox':p['nativeGlobalBox'],'usableAsFinalArt':False})
    if not prog.exists():
        d=read(ROOT/'progress-r09_c13.json');d.update({'status':'guides_prepared','generatedNativeCount':0,'usableNativeCount':0,'complete4kCount':0,'formalAcceptedCount':0,'currentTile':TID,'currentPatch':None,'updatedAt':now(),'nextStep':'Generate from existing top and left native neighbors; inspect each seam.'});write(prog,d)
    print(json.dumps({'tile':TID,'guides':16,'nativeCount':len(list((ROOT/'native').glob(TID+'*.png')))}))
elif mode=='request':
    pid,ver,description=sys.argv[2:5];neighbors=sys.argv[5:];assert pid.startswith(TID)
    assert not (ROOT/'prompts'/f'{pid}_{ver}.request.json').exists()
    context(pid,neighbors,ver)
    def local_progress(**changes):
        d=read(prog);d.update(changes);d['updatedAt']=now()
        pending=prog.with_suffix('.pending.json');write(pending,d);os.replace(pending,prog)
    workflow.progress=local_progress
    sys.argv=[str(ROOT/'request.py'),pid,ver,description]
    runpy.run_path(str(ROOT/'request.py'),run_name='__main__')
elif mode=='ingest':
    pid,ver,source=sys.argv[2:5];assert pid.startswith(TID)
    name=f'{pid}_{ver}';out=ROOT/'native'/f'{name}.png';assert not out.exists()
    req=read(ROOT/'prompts'/f'{name}.request.json');receipt=read(ROOT/'receipts'/f'{name}.json');prompt=Path(req['promptPath'])
    assert receipt['submittedArguments']['prompt'].replace('\r\n','\n')==prompt.read_text(encoding='utf-8')
    assert receipt['submittedArguments']['referenced_image_paths']==[x['file'] for x in req['references']]
    src=Path(source)
    with Image.open(src) as im: size=list(im.size);fmt=im.format;imode=im.mode
    assert size==[1254,1254]
    shutil.copy2(src,out)
    info={'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':size[0],'height':size[1],'format':fmt,'mode':imode,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'configSnapshot':read(prog)['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin host-managed; no model/quality selectors or values disclosed.','prompt':str(prompt),'promptSha256':sha(prompt),'references':req['references'],'evidence':{'toolReceipt':f'receipts/{name}.json','returnedFields':['image_url','output_hint']},'coordinate':patch(pid),'resizedAfterGeneration':False,'status':'candidate_pending_visual_review'}
    write(Path(str(out)+'.generation.json'),info)
    d=read(prog);d.update({'status':'native_received','generatedNativeCount':len(list((ROOT/'native').glob(TID+'*.png'))),'currentPatch':pid,'updatedAt':now()})
    pending=prog.with_suffix('.pending.json');write(pending,d);os.replace(pending,prog)
    print(json.dumps({'file':str(out),'sha256':sha(out),'pixels':size}))
