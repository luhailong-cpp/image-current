from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys
from PIL import Image

ZONE = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
def now(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def tile_path(tile):
    assert tile[0]=='r' and int(tile[1:3]) in range(1,9) and tile[4]=='c' and int(tile[5:7]) in (9,10), 'Outside left worker ownership'
    p = (ZONE/tile).resolve(); assert p.parent == ZONE.resolve(); return p
def progress(tile, next_patch=None):
    selection = read(tile/'selected-native.json') if (tile/'selected-native.json').exists() else {}
    sources = [{'patch':p,'file':str(tile/'native'/f),'sha256':sha(tile/'native'/f)} for p,f in sorted(selection.items())]
    previous = read(tile/'tile-progress.json') if (tile/'tile-progress.json').exists() else {}
    previous.update({'tile':tile.name,'status':'native_patch_production','updatedAt':now(),'nativeCount':len(list((tile/'native').glob('*.png'))),'selectedCoreCount':len(selection),'remainingCoreCount':16-len(selection),'nativeSources':sources,'completeCandidateCount':0,'internalPassed4kCount':0,'formalAcceptedCount':0,'nextPatch':next_patch,'inflightGeneration':None,'actualModel':None,'actualQuality':None,'nextStep':'Continue bottom-up/right-left native cores; missing outside-zone neighbors remain shared QA pending.'})
    write(tile/'tile-progress.json', previous)
def save_result(tile_id, version, source, next_patch=None):
    tile=tile_path(tile_id); source=Path(source)
    with Image.open(source) as im:
        im.load(); assert im.size==(1254,1254) and im.format=='PNG', 'Native source dimension/format mismatch; no resampling allowed'
    receipt=tile/'receipts'/f'{version}.receipt.json'
    assert not receipt.exists(), 'Never overwrite receipt'
    write(receipt, {'tool':'image_gen','route':'builtin','status':'success','savedAt':now(),'sourceOutputPath':str(source),'sourceOutputSha256':sha(source),'measuredNativePixels':[1254,1254],'actualModel':None,'actualQuality':None,'returnedResultKeys':['image_url','output_hint'],'toolOutputHint':'Generated PNG saved to '+str(source)+'; original retained.','sourceKept':True})
    subprocess.run([PYTHON,str(ZONE/'tile_worker.py'),'--tile',tile_id,'ingest',version,str(source)],check=True)
    selection=read(tile/'selected-native.json') if (tile/'selected-native.json').exists() else {}
    selection[version.split('-')[0]]=version+'.png';write(tile/'selected-native.json',selection)
    progress(tile,next_patch)
    print(json.dumps({'tile':tile_id,'selectedCoreCount':len(selection),'selected':version,'sha256':sha(tile/'native'/f'{version}.png')}))
if __name__=='__main__':
    if sys.argv[1]=='save':save_result(*sys.argv[2:])
    elif sys.argv[1]=='progress':progress(tile_path(sys.argv[2]),sys.argv[3] if len(sys.argv)>3 else None)
