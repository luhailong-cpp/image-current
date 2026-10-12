import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists(): raise RuntimeError(f'Preserving existing file: {p}')
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=argparse.ArgumentParser()
p.add_argument('tile'); p.add_argument('patch'); p.add_argument('attempt'); p.add_argument('source'); p.add_argument('observation')
a=p.parse_args(); lane=ROOT/a.tile/'pipeline'; req=lane/'prompts'/f'{a.patch}.{a.attempt}.request.json'
r=json.loads(req.read_text(encoding='utf-8-sig')); src=Path(a.source)
dest=lane/'returns'/f'{a.patch}.{a.attempt}.png'; dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists(): raise RuntimeError(f'Preserving existing native: {dest}')
shutil.copy2(src,dest)
assert sha(src)==sha(dest)
with Image.open(src) as im:
    size=list(im.size); mode=im.mode; fmt=im.format
    opaque=mode!='RGBA' or im.getextrema()[3]==(255,255)
receipt=lane/'receipts'/f'{a.patch}.{a.attempt}.receipt.json'
write(receipt, {'tool':'image_gen.imagegen','status':'returned_image','recordedAtUtc':datetime.now(timezone.utc).isoformat(),
    'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'native':{'file':str(dest),'sha256':sha(dest),'pixels':size,'mode':mode,'format':fmt,'opaque':opaque},
    'request':{'file':str(req),'sha256':sha(req)},'prompt':{'file':r['promptFile'],'sha256':r['promptSha256']},
    'references':r['references'],'actualModel':None,'actualQuality':None,
    'submittedParameters':{'model':None,'quality':None,'transparent_background':False},
    'nativePixelsPreserved':True,'resizedAfterGeneration':False,'visualObservation':a.observation,
    'internalAccepted':False,'formalAccepted':False,
    'toolOutputMetadata':{'output_hint':f'Generated image is saved at `{src}`.'}})
print(json.dumps({'receipt':str(receipt),'nativeOriginal':str(dest),'pixels':size,'sha256':sha(src),'formalAccepted':False}))
