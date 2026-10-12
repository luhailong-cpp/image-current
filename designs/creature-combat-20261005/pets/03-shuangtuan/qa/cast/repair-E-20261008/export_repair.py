import json, hashlib, shutil, sys
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

BASE=Path('D:/work/image/designs/creature-combat-20261005/pets/03-shuangtuan')
SRC=BASE/'source/cast/E/repair-20261008'
REC=BASE/'records/cast/E'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n, native_path, attempt=1):
    f=f'{int(n):02d}'
    SRC.mkdir(parents=True,exist_ok=True)
    runtime=BASE/f'runtime/cast/E/{f}.png'
    oldrec=REC/f'{f}.generation.json'
    historical=REC/f'{f}.before-repair-20261008.generation.json'
    if not historical.exists():
        shutil.copy2(oldrec,historical)
    native=SRC/f'{f}-a{attempt}.png'
    shutil.copy2(native_path,native)
    im=Image.open(native).convert('RGBA')
    assert im.width==im.height, im.size
    request=json.loads((REC/f'{f}.repair-20261008-a{attempt}.request.json').read_text(encoding='utf-8'))
    candidate=SRC/f'{f}-a{attempt}-1024.png'
    im.resize((1024,1024),Image.Resampling.LANCZOS).save(candidate)
    record={
        'file':candidate.relative_to(BASE).as_posix(),'sha256':sha(candidate),
        'generatedAt':datetime.now(timezone.utc).isoformat(), 'width':1024,'height':1024,'format':'PNG',
        'tool':'image_gen.imagegen','route':'builtin',
        'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),
        'submittedParameters':{'model':None,'quality':None,**{k:v for k,v in request.items() if k!='prompt'}},
        'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露model/quality；目标值不等于实际提交值。',
        'prompt':f'prompts/cast/E/{f}.repair-20261008-a{attempt}.txt',
        'references':[{'path':p,'sha256':sha(p),'purpose':['edit target','continuity/support reference','E identity','W identity','primary approved style'][i]} for i,p in enumerate(request['referenced_image_paths'])],
        'evidence':{'receipt':f'records/cast/E/{f}.repair-20261008-a{attempt}.receipt.json'},
        'native':{'width':im.width,'height':im.height,'format':'PNG','mode':'RGBA'},
        'derivedFrom':{'file':native.relative_to(BASE).as_posix(),'sha256':sha(native)},
        'editHistory':{'previousGenerationRecord':historical.relative_to(BASE).as_posix(),'previousRuntimeSha256':sha(runtime)},
        'operation':'Uniform whole-canvas Lanczos resize to 1024; no pose synthesis, crop, flip, translation, interpolation or foot alignment.',
        'direction':'E','action':'cast','frame':int(n),'durationMs':45,'pivot':[0.5,0.08],'event':'cast-release' if int(n)==11 else None,
        'visualStatus':'candidate awaiting actual image inspection'
    }
    (REC/f'{f}.repair-20261008-a{attempt}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'candidate':str(candidate),'native':str(native),'nativeSize':im.size,'sha256':sha(candidate)}))
def accept(n,attempt=1):
    f=f'{int(n):02d}'
    rp=REC/f'{f}.repair-20261008-a{attempt}.generation.json'
    r=json.loads(rp.read_text(encoding='utf-8'))
    candidate=BASE/r['file']; runtime=BASE/f'runtime/cast/E/{f}.png'
    assert sha(candidate)==r['sha256']
    shutil.copy2(candidate,runtime)
    r['file']=runtime.relative_to(BASE).as_posix()
    r['visualStatus']='actual full-frame inspection passed: both hind feet connected to haunch and kept beneath pelvis; original front-paw phase, identity, direction and accessories retained; final sequence review pending'
    rp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    (REC/f'{f}.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print('accepted '+f+' '+sha(runtime))
if __name__=='__main__':
    if sys.argv[1]=='save': save(sys.argv[2],sys.argv[3],int(sys.argv[4]) if len(sys.argv)>4 else 1)
    elif sys.argv[1]=='accept': accept(sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 1)
