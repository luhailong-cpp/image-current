"""Tile-local requests and truthful progress; no writes to shared zone state."""
from pathlib import Path
from PIL import Image
import json, argparse, hashlib
from datetime import datetime, timezone
HERE=Path(__file__).resolve().parent
ZONE=HERE.parent

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o): Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()

def progress(note=''):
    natives=[]
    for source in sorted((HERE/'native').glob('p[1-4][1-4].png')):
        record=read(str(source)+'.generation.json')
        assert sha(source)==record['sha256'] and record['nativeSize']==[1254,1254]
        natives.append({'patch':source.stem,'file':str(source),'sha256':record['sha256']})
    path=HERE/'tile-progress.json'
    data=read(path) if path.exists() else {'tile':HERE.name,'completeCandidateCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0,'formalAcceptedCount':0,'actualModel':None,'actualQuality':None}
    data.update({'status':'native-patch-production' if natives else 'prepared-awaiting-actual-north-native','updatedAt':now(),'nativePatchCount':len(natives),'remainingCoreCount':16-len(natives),'nativeSources':natives,'nextStep':note,'inflightGeneration':None})
    save(path,data)
    print(json.dumps({'tile':HERE.name,'nativePatchCount':len(natives),'remainingCoreCount':16-len(natives)}))

def request(patch,note):
    assert len(patch)==3 and patch[0]=='p' and patch[1] in '1234' and patch[2] in '1234'
    context=HERE/'layout-only'/f'{patch}-mixed-context.png'
    meta=read(str(context)+'.generation.json')
    assert sha(context)==meta['sha256']
    for item in meta['derivedFrom']: assert sha(item['file'])==item['sha256']
    dirs={item.get('role') for item in meta['derivedFrom']}
    assert 'actual north native context' in dirs
    assert patch[2]=='1' or 'actual west native context' in dirs
    west='actual west native context' in dirs
    bands='TOP230 and LEFT230' if west else 'TOP230 only; the lower left edge has no native western neighbor'
    preserved='topmost115 and leftmost115 pixels' if west else 'topmost115 pixels'
    prompt=f'''Use case: precise-object-edit. Produce the exact native1254x1254 opaque map crop {HERE.name}/{patch}.
Image1 is the mixed edit target. Its crisp {bands} are real native neighbor art with recorded coordinates; any repaired neighbor candidate core is authoritative. The other blurry areas are geometry guidance only and must be freshly painted. Images2/3/4 supply approved full-city layout, close material/daylight treatment and Daoist Mail illustration style, not output framing.
{note}
Preserve {preserved} exactly. Continue inherited shapes naturally through x115..300 and y115..300 with no hard boundary at x230/y230. Match established positions, perspective, object sizes and paving courses. Complete an existing object instead of duplicating it. No extra eave, beam, ridge, lantern, pedestal or prop. Use clean coherent construction and crisp real native detail; rounded polished Daoist Q illustration, broad restrained painted highlights, natural grey stone, red wood and golden trim only in indicated objects. Upper-left soft daylight. No blurry enlarged-layout pixels, defocus, bokeh, smear, sharpening filter or photographic grain. Keep exact1254x1254 framing; no crop, rescale, warp, zoom, camera shift, text, letters, UI, frame, grid, watermark or transparency.'''
    contract=read(ZONE.parent/'production-contract.json')
    refs=[str(context),contract['layoutReference'],contract['detailStyleReference'],contract['primaryStyleReference']]
    target=HERE/'prompts'/f'{patch}.request.json'
    textfile=HERE/'prompts'/f'{patch}.prompt.txt'
    assert not target.exists() and not textfile.exists()
    textfile.write_text(prompt,encoding='utf-8')
    save(target,{'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False,'referenceRoles':['exact mixed native/candidate context with layout to repaint','approved full city geography','approved material/daylight detail','primary Daoist Mail illustration style']})
    progress_path=HERE/'tile-progress.json'
    state=read(progress_path)
    state.update({'updatedAt':now(),'inflightGeneration':{'patch':patch,'request':str(target),'requestSha256':sha(target),'status':'request-saved-awaiting-builtin-result'},'nextStep':f'Complete {patch} from saved request and retain tool receipt before ingestion.'})
    save(progress_path,state)
    print(target)

def prepare_audit():
    plan=read(HERE/'coordinates.json')
    assert len(plan['patches'])==16 and plan['coreWorldBox']==[49152,28672,53248,32768]
    for item in plan['patches']:
        assert sha(item['guide'])==item['guideSha256']
        with Image.open(item['guide']) as im: assert im.size==(1254,1254)
    contract=read(ZONE.parent/'production-contract.json')
    refs=[{'file':contract[k],'sha256':sha(contract[k]),'role':k} for k in ['layoutReference','detailStyleReference','primaryStyleReference']]
    save(HERE/'qa/preparation-audit.json',{'tile':HERE.name,'guideCount':16,'guideSize':[1254,1254],'worldBox':plan['coreWorldBox'],'referencesViewed':refs,'overviewViewed':str(HERE/'layout-only/tile-grid-layout-only.png'),'assetRole':'layout only, never candidate art','northPolicy':'Each first-row patch waits for its corresponding selected r07_c13 p4x native and sidecar; all later patches require actual north, plus west when column > 1.','formalAcceptedCount':0,'actualModel':None,'actualQuality':None})
    progress('Await root notification of selected r07_c13 p41 before first generation; prepare must not repeat.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['request','progress','prepare-audit']);p.add_argument('patch',nargs='?',default='');p.add_argument('note',nargs='?',default='');a=p.parse_args()
    if a.mode=='request': request(a.patch,a.note)
    elif a.mode=='prepare-audit': prepare_audit()
    else: progress(a.note or a.patch)
