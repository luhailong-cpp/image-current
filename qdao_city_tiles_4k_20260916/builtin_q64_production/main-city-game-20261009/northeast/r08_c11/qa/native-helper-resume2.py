from pathlib import Path
import sys,json,hashlib,importlib.util
from datetime import datetime,timezone
ZONE=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('worker',ZONE/'tile_worker.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
tile,cmd,patch=sys.argv[1:4]
assert int(tile[5:7]) in (11,12) and 1<=int(tile[1:3])<=8
w.setup(tile);p=ZONE/tile;ver=patch+'-v20261013-r2'
if cmd=='save' and len(sys.argv)>5:
    ver=sys.argv[5];assert ver.startswith(patch+'-') and Path(ver).name==ver
if cmd=='request':
    assert not (p/'native'/f'{ver}.png').exists()
    if not (p/'coordinates.json').exists():w.p.prepare()
    target=p/'layout-only'/f'{patch}-mixed-context.png'
    if not target.exists():w.context(patch,[],False)
    desc=sys.argv[4]
    prompt='Use case: precise-object-edit. Produce exactly 1254x1254 opaque PNG native game-map painting. Image 1 is the edit target: sharp border strips are actual neighboring art to align continuously; the blurred area only specifies existing geometry. Images 2/3/4 are approved geography, daytime material detail, primary Daoist Q hand-painted style respectively. Preserve camera, fixed crop, object scale and layout. '+desc+' Replace all blurred pixels by crisp new native hand-painted detail. Match natural pale gray and blue-gray stone, rounded fine bevels, soft upper-left daylight, restrained mineral texture. Continue each slab joint exactly at its position and angle across any actual border strip; no straight rectangular guide boundary may remain. Do not import UI, characters, text or night lighting from references. No extra tree, pot, island, prop, building, new road stripe, frame, watermark, grid, blur, enlargement or perspective change.'
    base=ZONE.parents[1]/'parallel_20261005/daylight-only-20261009'
    refs=[str(target),str(base/'tianyong/tianyong-spring-natural-stone-v9.png'),str(base/'tianyong/tianyong-natural-stone-detail-v1.png'),str(base/'user-references-20261009/mail-daoist-style.jpg')]
    req={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'referenceRoles':['edit target: actual native overlaps and layout-only blur','approved map geography','approved near-view materials and daylight','primary Daoist Q style']}
    for suffix,content in [('prompt.txt',prompt),('request.json',json.dumps(req,ensure_ascii=False,indent=2))]:
        out=p/'prompts'/f'{ver}.{suffix}';assert not out.exists();out.write_text(content,encoding='utf-8')
    print(json.dumps(req,ensure_ascii=False))
elif cmd=='save':
    src=Path(sys.argv[4]);receipt=p/'receipts'/f'{ver}.receipt.json';assert not receipt.exists()
    save(receipt,{'tool':'image_gen','route':'builtin','receivedAt':datetime.now(timezone.utc).isoformat(),'sourceOutputPath':str(src),'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed builtin output returned no actual model metadata.'})
    w.p.ingest(ver,str(src))
    select=p/'selected-native.json';selection=json.loads(select.read_text(encoding='utf-8-sig')) if select.exists() else {};selection[patch]=ver+'.png';save(select,selection)
    count=sum((p/'native'/v).exists() for v in selection.values())
    progress=p/'tile-progress.json';v=json.loads(progress.read_text(encoding='utf-8-sig')) if progress.exists() else {}
    v.update(tile=tile,status='native_patch_production',selectedCoreCount=count,nativePatchCount=count,remainingCoreCount=16-count,completeCandidateCount=0,internalPassed4kCount=0,externalPassed4kCount=0,formalAcceptedCount=0,actualModel=None,actualQuality=None,lastSavedNative=ver+'.png',inflightGeneration=None,successfulUnsavedOutputCount=0,generationStopped=False,updatedAt=datetime.now(timezone.utc).isoformat());save(progress,v)
