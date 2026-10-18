"""Immutable native seam crop/overlay helper. No scaling, blending, or painting."""
import argparse, json, hashlib, shutil, sys
from pathlib import Path
from PIL import Image, ImageChops
import native_batch as n
import receipt_register as rr

B = Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def outdir(version):
    p=(B/'versions'/version).resolve()
    assert p.is_relative_to(B/'versions') and not p.exists(), 'Unsafe or existing output version'
    p.mkdir(parents=True)
    return p
def js(p,d):
    assert p.resolve().is_relative_to(B) and not p.exists()
    with p.open('x',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False,indent=2)
def png(p,im):
    assert p.resolve().is_relative_to(B) and not p.exists()
    with p.open('xb') as f: im.save(f,format='PNG')
def artifact(p): return {'file':str(p),'sha256':sha(p)}
def rgb(p,size):
    im=Image.open(p); im.load()
    assert im.size==size and im.mode in ('RGB','RGBA'), 'Wrong native size/mode'
    if im.mode=='RGBA': assert im.getchannel('A').getextrema()==(255,255)
    return im.convert('RGB')
def prepare(a):
    n.verify_contracts()
    baseline=Path(a.baseline).resolve()
    assert baseline.is_relative_to(B), 'Foreign candidate'
    assert a.tile in ('r03_c13','r03_c14','r04_c13','r04_c14')
    im=rgb(baseline,(4096,4096)); x,y=a.xy
    assert 115<=x<=2957 and 115<=y<=2957, 'This helper only supports interior context'
    d=outdir(a.version); box=[x-115,y-115,x+1139,y+1139]
    crop=d/'repair-input.png'; png(crop,im.crop(box))
    metadata={'schemaVersion':1,'createdAtUtc':n.now(),'tile':a.tile,'baseline':artifact(baseline),
        'input':artifact(crop),'contextTileXYXY':box,'editTileXYXY':[x,y,x+1024,y+1024],
        'nativeOutputPixels':[1254,1254],'sourceCoreXYXY':[115,115,1139,1139],
        'operations':['integer crop only'],'resized':False,'formalAcceptedCount':0}
    js(d/'prepare.json',metadata); print(json.dumps(metadata,ensure_ascii=False))
def integrate(a):
    n.verify_contracts()
    prep=read(a.prepare); req=read(a.request); prompt=Path(a.prompt)
    assert prompt.read_text(encoding='utf-8')==req['prompt'], 'Prompt mismatch'
    baseline=Path(prep['baseline']['file']); inp=Path(prep['input']['file'])
    assert sha(baseline)==prep['baseline']['sha256'] and sha(inp)==prep['input']['sha256']
    assert str(inp) in req['referenced_image_paths'], 'Prepared source not attached'
    refs=[artifact(Path(p)) for p in req['referenced_image_paths']]
    source,receipt,digest=rr.completed_event(Path(a.session_log),a.event_id)
    native=rgb(source,(1254,1254)); before=rgb(baseline,(4096,4096))
    x,y,x1,y1=prep['editTileXYXY']; assert x1-x==1024 and y1-y==1024
    after=before.copy(); after.paste(native.crop((115,115,1139,1139)),(x,y))
    outside=ImageChops.difference(before,after); outside.paste((0,0,0),(x,y,x1,y1))
    assert outside.getbbox() is None, 'Pixels changed outside declared edit'
    d=outdir(a.version); nativep=d/'native-repair.png'; shutil.copyfile(source,nativep)
    assert sha(nativep)==digest
    candidate=d/(prep['tile']+'-candidate.png'); png(candidate,after)
    evidence=[]
    for name,box in [('north',[x-115,y-115,x1+115,y+115]),('south',[x-115,y1-115,x1+115,y1+115]),
                     ('west',[x-115,y-115,x+115,y1+115]),('east',[x1-115,y-115,x1+115,y1+115])]:
        p=d/(name+'-perimeter-100pct.png'); png(p,after.crop(box));evidence.append({**artifact(p),'crop':box})
    corrected=d/'repaired-context-100pct.png';png(corrected,after.crop(prep['contextTileXYXY']))
    js(d/'receipt.json',receipt)
    record={**prep,'createdAtUtc':n.now(),'previousCandidate':artifact(baseline),
       'candidate':artifact(candidate),'nativeRepair':artifact(nativep),'inputPrepare':artifact(Path(a.prepare)),
       'submittedRequest':artifact(Path(a.request)),'exactPrompt':artifact(prompt),'references':refs,
       'receipt':artifact(d/'receipt.json'),'actualModel':None,'actualModelEvidence':'未返回',
       'operations':['integer native core crop [115,115,1139,1139)','opaque integer paste into new 4096 candidate'],
       'noResize':True,'noWarp':True,'noBlend':True,'unchangedOutsideEditVerified':True,
       'nativeEventBytesMatch':True,'perimeterEvidence':evidence,'contextEvidence':artifact(corrected),
       'visualQa':'pending; formalAcceptedCount=0'}
    js(d/'integration.json',record);print(json.dumps({'record':str(d/'integration.json'),'candidate':str(candidate),'formalAcceptedCount':0}))
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('prepare');q.add_argument('--baseline',required=True);q.add_argument('--tile',required=True);q.add_argument('--xy',nargs=2,type=int,required=True);q.add_argument('--version',required=True)
    q=sub.add_parser('integrate');q.add_argument('--prepare',required=True);q.add_argument('--request',required=True);q.add_argument('--prompt',required=True);q.add_argument('--event-id',required=True);q.add_argument('--version',required=True);q.add_argument('--session-log',default=str(rr.DEFAULT_LOG))
    a=p.parse_args();{'prepare':prepare,'integrate':integrate}[a.action](a)
if __name__=='__main__': main()
