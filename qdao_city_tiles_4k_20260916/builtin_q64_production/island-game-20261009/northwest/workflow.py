"""Only mechanical crop/paste, save, hashes and state. All painting is image_gen."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json,hashlib,shutil,argparse
ROOT=Path(__file__).resolve().parent
PROJECT=Path('D:/work/image')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def state(**kw):
    p=read(ROOT/'progress.json');p.update(kw,updatedAtUtc=now());write(ROOT/'progress.json',p)
def prepare(sr,sc,attempt='a01'):
    stem=f'r03_c03_s{sr:02d}_{sc:02d}'
    x=8192+(sc-1)*1024;y=8192+(sr-1)*1024
    box=[x-115,y-115,x+1139,y+1139]
    refs=read(ROOT/'references.json'); im=Image.open(refs[0]['path']).convert('RGB')
    rb=[v*1254/57344 for v in box]
    guide=im.transform((1254,1254),Image.Transform.EXTENT,rb,Image.Resampling.BICUBIC)
    neighbor=[]
    for nr,nc,which in [(sr,sc-1,'left'),(sr-1,sc,'top')]:
        if nr<1 or nc<1: continue
        candidates=sorted((ROOT/'native').glob(f'r03_c03_s{nr:02d}_{nc:02d}_a*.png'))
        if not candidates: continue
        p=candidates[-1];src=Image.open(p).convert('RGB')
        if src.size!=(1254,1254): raise ValueError('Measured native differs from plan; recalculate before extension.')
        if which=='left': crop=[1024,0,1254,1254];dest=[0,0]
        else: crop=[0,1024,1254,1254];dest=[0,0]
        guide.paste(src.crop(crop),tuple(dest))
        neighbor.append(dict(path=p.as_posix(),sha256=sha(p),role=f'{which} adjacent native with 230px overlap; exact continuity constraint',sourceCrop=crop,destination=dest))
    guide_id=stem+'_'+attempt
    path=ROOT/'guides'/f'{guide_id}.layout-with-native.png'
    if path.exists(): raise ValueError('Refuse overwrite of recorded guide')
    guide.save(path)
    inputs=[dict(path=path.as_posix(),sha256=sha(path),role='target layout-only enlargement with exact native neighbor strips',size=[1254,1254])]+refs+neighbor
    rec=dict(stem=stem,globalBox=box,coreBox=[x,y,x+1024,y+1024],referenceBox=rb,inputs=inputs,neighbor=neighbor,layoutPixelsForbiddenInFinal=True,operation='floating extent guide plus unresampled neighbor overlap paste')
    write(ROOT/'guides'/f'{guide_id}.input.json',rec)
    state(status='preparing_native',currentPatch=stem,nextStep='Inspect coordinate guide and generate with attached original native neighbor.')
    print(json.dumps(rec,ensure_ascii=False))
def ingest(stem,src,prompt,refsfile,update_progress=True):
    src=Path(src); dst=ROOT/'native'/f'{stem}.png'
    if dst.exists(): raise ValueError('Refuse overwrite')
    shutil.copy2(src,dst); im=Image.open(dst);im.load()
    refs=read(refsfile)
    if isinstance(refs,dict): refs=refs['inputs']
    for ref in refs:
        ref['sha256']=sha(ref['path'])
        ref['nativeSize']=list(Image.open(ref['path']).size)
    config_path=PROJECT/'config/image-generation.json'
    config=read(config_path) if config_path.is_file() else None
    rec=dict(file=dst.as_posix(),sha256=sha(dst),generatedAt=now(),nativeWidth=im.width,nativeHeight=im.height,format=im.format,sourceOutputPath=src.as_posix(),sourceOutputSha256=sha(src),tool='image_gen.imagegen',route='builtin',configSnapshot=config,submittedParameters=dict(model=None,quality=None,transparent_background=False),actualModel=None,actualQuality=None,unverifiedReason='宿主管理，工具未披露型号和质量；配置目标不等于实际调用参数',prompt=str(prompt),promptSha256=sha(prompt),references=refs,evidence=dict(receipt=(ROOT/'receipts'/f'{stem}.receipt.json').as_posix()),resizedAfterGeneration=False,finalArtUpscaled=False,status='candidate_pending_native_visual_and_seam_QA')
    if config is None:
        rec['configSnapshotAvailability']={'status':'missing_at_ingest','path':config_path.as_posix(),'actualModelAndQualityStillUndisclosed':True,'builtinReceiptPreserved':True}
    write(dst.with_suffix('.png.generation.json'),rec)
    if update_progress:
        p=read(ROOT/'progress.json')
        state(status='native_saved_pending_QA',generatedNativeCount=p['generatedNativeCount']+1,currentPatch=stem,nextStep='Check native image and geometric overlap before continuing.')
    print(json.dumps(dict(file=str(dst),size=list(im.size),sha256=sha(dst)),ensure_ascii=False))
ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','ingest']);ap.add_argument('--row',type=int);ap.add_argument('--col',type=int);ap.add_argument('--stem');ap.add_argument('--source');ap.add_argument('--prompt');ap.add_argument('--refs');ap.add_argument('--no-progress',action='store_true');a=ap.parse_args()
if a.action=='prepare':prepare(a.row,a.col,a.stem or 'a01')
else:ingest(a.stem,a.source,a.prompt,a.refs,not a.no_progress)
