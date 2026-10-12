from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib
from PIL import Image

BASE = Path(__file__).resolve().parent.parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def tile_dir(tile):
    assert tile in {f'r{r:02d}_c{c:02d}' for r in range(9,17) for c in (7,8)}
    return BASE / tile
def write(p, value):
    p = Path(p); assert not p.exists(), str(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def submit(tile, patch, attempt, prefix):
    t=tile_dir(tile); original=t/'pipeline/prompts'/f'{patch}.{attempt}.request.json'
    r=read(original)
    for q in r['references']:
        assert sha(q['file'])==q['sha256']
    pp=original.with_name(f'{patch}.{attempt}.submitted.prompt.txt')
    rp=original.with_name(f'{patch}.{attempt}.submitted.request.json')
    assert not pp.exists() and not rp.exists()
    prompt=prefix+'\n\n'+r['prompt']
    pp.write_text(prompt,encoding='utf-8')
    policies=[]
    for policy in (Path('D:/work/image/AGENTS.md'),Path('D:/work/image/docs/IMAGE_MODEL_REQUIREMENT.md')):
        body=policy.read_text(encoding='utf-8-sig')
        assert '2026-10-13' in body and ('回退' in body or 'explicitly allows' in body)
        policies.append({'file':str(policy),'sha256':sha(policy),'fullyReadAtUtc':now(),'meaning':'free/included2.5 preferred when available; existing builtin authorized; no paid API; actual model undisclosed'})
    r.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),preparedRequest=str(original),preparedRequestSha256=sha(original),preparedAtUtc=now(),activeModelPolicyEvidence=policies,actualModel=None,actualQuality=None)
    write(rp,r);print(str(rp))
def disposition(tile, patch, attempt, note):
    t=tile_dir(tile); receipt=t/'pipeline/receipts'/f'{patch}.{attempt}.receipt.json'
    r=read(receipt); raw=Path(r['savedUnmodifiedOriginal'])
    assert sha(raw)==r['sourceOutputSha256']
    with Image.open(raw) as im:
        im.load(); pixels=list(im.size); mode=im.mode; fmt=im.format
        opaque=mode!='RGBA' or im.getextrema()[3]==(255,255)
    write(receipt.with_name(f'{patch}.{attempt}.disposition.json'),{'toolReceipt':str(receipt),'toolReceiptSha256':sha(receipt),'source':str(raw),'sha256':sha(raw),'pixels':pixels,'mode':mode,'format':fmt,'opaque':opaque,'actualModel':None,'actualQuality':None,'visuallyInspectedAtUtc':now(),'visualDisposition':note,'provisionallyUsableNativeSource':pixels==[1254,1254] and opaque,'formalAccepted':False,'sourceResampling':False})
    print(json.dumps({'source':str(raw),'pixels':pixels,'sha256':sha(raw),'formalAccepted':False}))
def edit(tile, patch, base_attempt, attempt, source, supporting, prompt):
    t=tile_dir(tile); prior=t/'pipeline/prompts'/f'{patch}.{base_attempt}.request.json';r=read(prior)
    source=Path(source); supporting=Path(supporting)
    pp=t/'pipeline/prompts'/f'{patch}.{attempt}.prompt.txt';rp=pp.with_name(f'{patch}.{attempt}.request.json')
    assert not pp.exists() and not rp.exists()
    pp.write_text(prompt,encoding='utf-8')
    refs=r['references'][:4]
    refs[0]={'file':str(source),'sha256':sha(source),'role':'actual builtin native edit target; narrow local continuity correction'}
    refs.append({'file':str(supporting),'sha256':sha(supporting),'role':'supporting coordinate guide with exact approved top and left native neighbor strips; do not render coarse guide pixels'})
    r.update(prompt=prompt,promptFile=str(pp),promptSha256=sha(pp),references=refs,referenced_image_paths=[q['file'] for q in refs],priorRequest=str(prior),priorRequestSha256=sha(prior),preparedAtUtc=now(),nativeEditOperation='scoped native geometry correction, no spatial resampling')
    write(rp,r);print(str(rp))
def reject(tile, patch, attempt, reason):
    t=tile_dir(tile);receipt=t/'pipeline/receipts'/f'{patch}.{attempt}.receipt.json';r=read(receipt)
    write(receipt.with_name(f'{patch}.{attempt}.rejection.json'),{'toolReceipt':str(receipt),'toolReceiptSha256':sha(receipt),'source':r['savedUnmodifiedOriginal'],'sha256':r['sourceOutputSha256'],'status':'returned_native_rejected','explicitlyRejected':True,'selected':False,'formalAccepted':False,'actualModel':None,'actualQuality':None,'reason':reason,'reviewedAtUtc':now()})
    print('Rejected native preserved: '+r['savedUnmodifiedOriginal'])
def state(tile, patch, assembly=''):
    t=tile_dir(tile);p=t/'pipeline/right-lane-state-20261013.json'
    r=read(p) if p.exists() else {'lane':'right','assignedRows':[9,16],'assignedColumns':[7,8],'events':[]}
    r.update(updatedAtUtc=now(),activeTile=tile,nextPatch=patch,actualModel=None,actualQuality=None,formalAcceptedCount=0,builtinOnly=True,apiUsed=False)
    r['events'].append({'atUtc':now(),'nextPatch':patch,'assembly':assembly or None})
    q=p.with_suffix('.new.json');q.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');q.replace(p)
    print(str(p))
def panels(tile, assembly):
    t=tile_dir(tile);a=Path(assembly);m=read(a);p=Path(m['output']['file']);assert sha(p)==m['output']['sha256']
    dest=t/'pipeline/qa'/a.parent.name/'native-review-20261013';assert not dest.exists();dest.mkdir(parents=True)
    out=[]
    with Image.open(p) as src:
        assert src.size==(4096,4096)
        boxes={}
        for axis in ('x','y'):
            for edge in (1024,2048,3072):
                for seg in range(4):
                    if axis=='x': box=[edge-192,seg*1024,edge+192,(seg+1)*1024]
                    else: box=[seg*1024,edge-192,(seg+1)*1024,edge+192]
                    boxes[f'{axis}{edge}-segment{seg+1}']=box
        boxes['red-cap-halo-cut']=[0,890,1254,1460]
        boxes['ground-seam-deadends']=[1000,2100,1700,2700]
        boxes['blue-joint-deadend']=[3050,2170,3640,2670]
        boxes['lower-cloud-fork']=[1850,3150,2590,3770]
        boxes['lower-rim-fork']=[3280,3140,3970,3800]
        for name,box in boxes.items():
            f=dest/(name+'.png');src.crop(box).save(f,format='PNG')
            out.append({'file':str(f),'sha256':sha(f),'boxInCore':box,'sourceResampling':False})
    write(dest/'derivation.json',{'assembly':str(a),'assemblySha256':sha(a),'source':str(p),'sourceSha256':sha(p),'operation':'exact native pixel crops only; no resizing/recolor/warp/blur','crops':out})
    print(json.dumps({'directory':str(dest),'cropCount':len(out)}))
def anchor(tile, side, assembly, name):
    t=tile_dir(tile);a=Path(assembly);m=read(a)
    ctx=m['contextOutput'];p=Path(ctx['file']);assert sha(p)==ctx['sha256']
    box=[0,4096,4326,4326] if side=='top' else [4096,0,4326,4326]
    f=t/'pipeline/anchors'/f'{name}.png';assert not f.exists();f.parent.mkdir(parents=True,exist_ok=True)
    with Image.open(p) as im:
        assert im.size==(4326,4326);im.crop(box).save(f,format='PNG')
    write(Path(str(f)+'.derivation.json'),{'operation':'exact native context border crop','sourceAssembly':str(a),'sourceAssemblySha256':sha(a),'sourceContext':str(p),'sourceContextSha256':sha(p),'sourceCrop':box,'output':str(f),'outputSha256':sha(f),'pixels':[4326,230] if side=='top' else [230,4326],'sourceResampling':False,'formalAccepted':False,'upstreamStatus':'provisional native source with open geometry/material/external QA','createdAtUtc':now()})
    print(json.dumps({'anchor':str(f),'sha256':sha(f)}))
if __name__=='__main__':
    action=sys.argv[1]
    if action=='submit': submit(*sys.argv[2:])
    elif action=='disposition': disposition(*sys.argv[2:])
    elif action=='edit': edit(*sys.argv[2:])
    elif action=='reject': reject(*sys.argv[2:])
    elif action=='state': state(*sys.argv[2:])
    elif action=='panels': panels(*sys.argv[2:])
    elif action=='anchor': anchor(*sys.argv[2:])
