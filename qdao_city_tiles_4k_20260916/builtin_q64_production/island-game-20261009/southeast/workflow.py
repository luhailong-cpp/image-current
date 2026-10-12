"""Native result audit and deterministic crop/paste context preparation. No painting."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, argparse, shutil, os, time
from PIL import Image
ROOT=Path(__file__).resolve().parent
PROGRESS_FILE=ROOT/os.environ.get('ISLAND_PROGRESS_FILE','progress.json')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    payload=json.dumps(v,ensure_ascii=False,indent=2)+'\n'
    for attempt in range(8):
        try:
            p.write_text(payload,encoding='utf-8')
            return
        except OSError:
            if attempt==7:raise
            time.sleep(0.25)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def patch(pid):
    for tile in read(ROOT/'coordinate-plan.json')['tiles']:
        for p in tile['patches']:
            if p['id']==pid:return p
    raise ValueError(pid)
def progress(**kw):
    d=read(PROGRESS_FILE);d.update(kw);d['updatedAt']=now();write(PROGRESS_FILE,d)
    return d
def ingest(pid,version,source,receipt):
    src=Path(source);out=ROOT/'native'/f'{pid}_{version}.png'
    shutil.copy2(src,out)
    with Image.open(out) as im:
        im.load(); size=list(im.size); fmt=im.format; mode=im.mode
    request=read(ROOT/'prompts'/f'{pid}_{version}.request.json')
    info={'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'width':size[0],'height':size[1],'format':fmt,'mode':mode,'tool':'image_gen.imagegen','route':'builtin','sourceOutputPath':src.as_posix(),'sourceOutputSha256':sha(src),'configSnapshot':read(ROOT/'progress.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin; tool does not disclose model or quality.','evidence':{'toolReceipt':receipt,'returnedFields':['image_url','output_hint'],'largeImageDataLogged':False},'prompt':request['promptPath'],'promptSha256':sha(Path(request['promptPath'])),'references':request['references'],'coordinate':patch(pid),'resizedAfterGeneration':False,'status':'candidate_pending_visual_and_seam_review'}
    write(Path(str(out)+'.generation.json'),info)
    d=read(PROGRESS_FILE)
    count=len(list((ROOT/'native').glob('*.png'))) if PROGRESS_FILE==ROOT/'progress.json' else d['generatedNativeCount']+1
    progress(status='native_received',generatedNativeCount=count,currentPatch=pid,nextStep='Inspect native dimensions and content; verify joins before any acceptance')
    print(json.dumps({'file':out.as_posix(),'sha256':info['sha256'],'nativePixels':size}))
def context(pid,neighbors,version=None):
    p=patch(pid);box=p['nativeGlobalBox']; base=ROOT/'guides'/f'{pid}.layout-only.png'
    img=Image.open(base).convert('RGB'); sources=[{'file':base.as_posix(),'sha256':sha(base),'role':'layout-only coordinate crop, not final pixels'}]; placements=[]
    for neighbor in neighbors:
        np=ROOT/'native'/neighbor; rec=read(Path(str(np)+'.generation.json'));nb=rec['coordinate']['nativeGlobalBox'];im=Image.open(np).convert('RGB')
        if list(im.size)!=[1254,1254]:raise ValueError('Unexpected native dimensions: replan required')
        inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
        if inter[2]<=inter[0] or inter[3]<=inter[1]:raise ValueError('No overlap')
        crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]]
        img.paste(im.crop(crop),tuple(dest));placements.append({'source':np.as_posix(),'sourceCrop':crop,'destination':dest,'globalIntersection':inter})
        sources.append({'file':np.as_posix(),'sha256':sha(np),'role':'adjacent native result; preserve identical overlap geometry and detail'})
    suffix=f'-{version}' if version else ''
    out=ROOT/'guides'/f'{pid}.native-context{suffix}.png'
    if out.exists():raise ValueError('Guide already exists; use unique version to preserve input hashes')
    img.save(out)
    write(Path(str(out)+'.generation.json'),{'file':out.as_posix(),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'format':'PNG','operation':'mechanical paste of unscaled adjacent native overlap onto layout-only crop; reference guide only','derivedFrom':sources,'placements':placements,'usableAsFinalArt':False})
    print(json.dumps({'file':out.as_posix(),'placements':placements}))
if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action');parser.add_argument('pid');parser.add_argument('--version',default='v01');parser.add_argument('--source');parser.add_argument('--receipt');parser.add_argument('--neighbor',action='append',default=[]);a=parser.parse_args()
    if a.action=='ingest':ingest(a.pid,a.version,a.source,a.receipt)
    elif a.action=='context':context(a.pid,a.neighbor,a.version if a.version!='v01' else None)
