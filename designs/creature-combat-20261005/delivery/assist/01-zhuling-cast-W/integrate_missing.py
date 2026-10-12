"""Import only absent final frames; retain all model/source evidence and never replace existing PNGs."""
from pathlib import Path
from PIL import Image
import hashlib, io, json, os, sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
SRC=Path(__file__).resolve().parent
PET=SRC.parents[2]/'pets'/'01-zhuling'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def exclusive_json(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x',encoding='utf-8') as f: json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
results=[]
for n in [13,15,16]:
    dest=PET/'runtime/cast/W'/f'{n:02}.png'
    if dest.exists():
        results.append({'frame':n,'status':'skipped-existing','sha256':sha(dest)});continue
    native=SRC/f'{n:02}.png'
    evidence=json.loads((SRC/f'{n:02}.png.generation.json').read_text(encoding='utf-8-sig'))
    assert sha(native)==evidence['sha256']
    im=Image.open(native)
    assert im.size==(1254,1254) and im.mode=='RGBA'
    out=Image.new('RGBA',(1024,1024),(0,0,0,0))
    out.alpha_composite(im.resize((820,820),Image.Resampling.LANCZOS),(102,102))
    buf=io.BytesIO();out.save(buf,format='PNG');payload=buf.getvalue()
    final_sha=hashlib.sha256(payload).hexdigest()
    # A hard link installs a fully written PNG atomically, and cannot overwrite another writer.
    temp=SRC/f'{n:02}.export-in-progress.tmp'
    with temp.open('xb') as f: f.write(payload)
    try:
        os.link(temp,dest)
    except FileExistsError:
        results.append({'frame':n,'status':'skipped-concurrent-existing','sha256':sha(dest)});continue
    finally:
        temp.unlink()
    source_copy=PET/'records/cast/W'/f'{n:02}.root-assist-native-20261008.json'
    prompt_copy=PET/'prompts/cast/W'/f'{n:02}.root-assist-20261008.txt'
    receipt_copy=PET/'records/cast/W'/f'{n:02}.root-assist-receipt-20261008.json'
    prompt_copy.parent.mkdir(parents=True,exist_ok=True)
    with prompt_copy.open('x',encoding='utf-8') as f:f.write((SRC/'prompts'/f'{n:02}.txt').read_text(encoding='utf-8'))
    exclusive_json(receipt_copy,json.loads((SRC/'receipts'/f'{n:02}.json').read_text(encoding='utf-8-sig')))
    exclusive_json(source_copy,evidence)
    record={**evidence,'file':dest.relative_to(PET).as_posix(),'sha256':final_sha,'width':1024,'height':1024,
       'frame':n,'action':'cast','direction':'W','durationMs':45,'pivot':[0.5,0.08],'event':None,
       'prompt':prompt_copy.relative_to(PET).as_posix(),'receipt':receipt_copy.relative_to(PET).as_posix(),
       'derivedFrom':{'file':str(native),'sha256':evidence['sha256'],'record':source_copy.relative_to(PET).as_posix(),
                      'width':1254,'height':1254},
       'evidence':{**evidence.get('evidence',{}),'receipt':receipt_copy.relative_to(PET).as_posix()},
       'exportedAt':datetime.now(timezone.utc).isoformat(),
       'exportTransform':{'nativeCanvasResize':[820,820],'canvas':[1024,1024],'offset':[102,102]},
       'operation':'whole 1254 canvas resized once to 820 with Lanczos and composited at [102,102] on 1024 RGBA; no per-frame alignment',
       'alphaExtrema':list(out.getchannel('A').getextrema()),'alphaBBox':out.getchannel('A').getbbox(),
       'visualStatus':'static candidate inspected; final full-sequence playback pending original owner review'}
    exclusive_json(dest.with_suffix('.png.generation.json'),record)
    results.append({'frame':n,'status':'imported-missing-only','sha256':final_sha,'sourceSha256':evidence['sha256']})
exclusive_json(SRC/'integration-result.json',{'atUTC':datetime.now(timezone.utc).isoformat(),'results':results,'manifestChanged':False})
print(json.dumps(results,ensure_ascii=False))
