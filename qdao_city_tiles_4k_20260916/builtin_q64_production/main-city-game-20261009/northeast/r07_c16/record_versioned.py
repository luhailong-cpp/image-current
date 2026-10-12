"""Update only this tile's version selection/progress after real native ingest."""
from pathlib import Path
import json, sys, hashlib
from datetime import datetime, timezone

TILE=Path(__file__).resolve().parent
def read(p, default=None):
    return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else default
def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
mode, version=sys.argv[1:3]
patch=version.split('-')[0]
assert len(patch)==3 and patch[0]=='p' and patch[1] in '1234' and patch[2] in '1234'
assert version.startswith(patch+'-v20261012')
progress=read(TILE/'tile-progress.json',{})
if mode=='pending':
    assert not (TILE/'native'/f'{version}.png').exists()
    assert (TILE/'prompts'/f'{version}.request.json').exists()
    progress.update(status='native_patch_generation',inflightRequests=[version],nextStep='Await current built-in output, immediately preserve receipt and ingest, then inspect and continue actual neighbors.')
elif mode=='select':
    image=TILE/'native'/f'{version}.png'
    record=read(Path(str(image)+'.generation.json'))
    assert image.exists() and sha(image)==record['sha256']
    assert record['nativeSize']==[1254,1254] and not record['resized']
    assert (TILE/'receipts'/f'{version}.receipt.json').exists()
    selection=read(TILE/'selected-native.json',{})
    selection[patch]=image.name
    save(TILE/'selected-native.json',selection)
    progress.update(status='native_patch_production',selectedCoreCount=len(selection),inflightRequests=[],lastCompletedPatch=patch,lastCompletedNative=str(image),lastCompletedSha256=record['sha256'],nextStep='Continue missing versioned cores using actual north/west dependencies, then native seam QA and limited P2 repair.')
    if not progress.get('firstResumedNative'):progress['firstResumedNative']={'file':str(image),'sha256':record['sha256'],'sourceOutputPath':record['sourceOutputPath']}
else:raise ValueError(mode)
progress['generatedNativeCount']=len(list((TILE/'native').glob('*.generation.json')))
progress['updatedAt']=datetime.now(timezone.utc).isoformat()
progress['unsavedSuccessfulOutputs']=[]
save(TILE/'tile-progress.json',progress)
print(json.dumps(progress,ensure_ascii=False))
