from pathlib import Path
from datetime import datetime, timezone
import sys, json, hashlib, shutil
from PIL import Image
B=Path(__file__).resolve().parent.parent
action,tile,patch,attempt,*args=sys.argv[1:]
assert tile in {f'r{r:02d}_c{c:02d}' for r in range(9,17) for c in (7,8)}
T=B/tile
P=T/'pipeline'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    assert not p.exists(),p
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=P/'prompts'/f'{patch}.{attempt}.request.json'
sub=P/'prompts'/f'{patch}.{attempt}.submitted.request.json'
final=P/'prompts'/f'{patch}.{attempt}.final.request.json'
receipt=P/'receipts'/f'{patch}.{attempt}.receipt.json'
if action=='refine':
    source=sub if sub.exists() else base
    d=read(source)
    d['prompt']='CRITICAL EXACT GEOMETRY: '+args[0]+'\n\n'+d['prompt']
    prompt=P/'prompts'/f'{patch}.{attempt}.final.prompt.txt'
    assert not prompt.exists()
    prompt.write_text(d['prompt'],encoding='utf-8')
    d.update({'promptFile':str(prompt),'promptSha256':sha(prompt),'parentSubmittedRequest':str(source),'parentSubmittedRequestSha256':sha(source),'preparedAtUtc':datetime.now(timezone.utc).isoformat()})
    write(final,d)
    print(json.dumps({'finalRequest':str(final),'refCount':len(d['references'])}))
elif action=='enhance':
    d=read(base)
    q=B/'pipeline-tools'/'local-continuation-audit-20261011'/'r12-firstrow'/'ref-stone-context.png'
    assert q.is_file() and len(d['references'])==4
    d['references'].append({'file':str(q),'sha256':sha(q),'role':'quiet natural stone surface only; no geometry, grout or pattern transfer'})
    d['referenced_image_paths'].append(str(q))
    prefix='IMAGE 5 IS ONLY A MATERIAL FINISH SAMPLE. New interior stone faces should match its broad calm tonal variation, sparse painterly marks and smooth clean surface. Remove cell-like, tessellated, scaly, woven or cracked microtexture in the reconstructed interior. Do not copy its geometry or grout. Keep Image 1 exact magnification, clipped content, all structural line positions and native top/left halo tangent. Do not zoom out or add a complete symbol.\n\n'
    d['prompt']=prefix+d['prompt']
    prompt=P/'prompts'/f'{patch}.{attempt}.submitted.prompt.txt'
    assert not prompt.exists()
    prompt.write_text(d['prompt'],encoding='utf-8')
    d.update({'promptFile':str(prompt),'promptSha256':sha(prompt),'preparedRequest':str(base),'preparedRequestSha256':sha(base),'preparedAtUtc':datetime.now(timezone.utc).isoformat()})
    write(sub,d)
    print(json.dumps({'submittedRequest':str(sub),'refCount':len(d['references'])}))
elif action=='save':
    source=Path(args[0])
    started=args[1]
    request=final if final.exists() else sub if sub.exists() else base
    assert source.is_file() and request.is_file()
    raw=P/'returned-originals'/f'{patch}.{attempt}.png'
    assert not raw.exists()
    raw.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,raw)
    assert sha(raw)==sha(source)
    with Image.open(raw) as im:
        pixels,mode,fmt=list(im.size),im.mode,im.format
        opaque=im.mode!='RGBA' or im.getextrema()[3]==(255,255)
    record={'tool':'image_gen.imagegen','status':'returned_image','startedAtUtc':started,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'sourceOutputPath':str(source),'sourceOutputSha256':sha(source),'savedUnmodifiedOriginal':str(raw),'savedUnmodifiedOriginalSha256':sha(raw),'nativePixels':pixels,'format':fmt,'mode':mode,'opaque':opaque,'request':str(request),'requestSha256':sha(request),'apiUsed':False,'actualModel':None,'actualQuality':None,'visualDisposition':'pending_visual_inspection'}
    write(receipt,record)
    print(json.dumps({'receipt':str(receipt),'original':str(raw),'pixels':pixels,'sha256':sha(raw)}))
elif action=='inspect':
    assert not (T/'native'/f'{patch}.png.generation.json').exists()
    d=read(receipt)
    assert d['visualDisposition']=='pending_visual_inspection'
    d['visualDisposition']=args[0]
    d['visuallyInspectedAtUtc']=datetime.now(timezone.utc).isoformat()
    if args[0].startswith('REJECTED'):
        d['explicitlyRejected']=True
    receipt.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'receipt':str(receipt),'visualDisposition':d['visualDisposition']}))
else:
    raise ValueError(action)
