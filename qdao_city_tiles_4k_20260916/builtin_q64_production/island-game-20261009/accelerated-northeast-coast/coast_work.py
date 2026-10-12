"""Mechanical layout guides, native-image records and unscaled core assembly only."""
from pathlib import Path
from PIL import Image
import json, hashlib, re, sys, shutil, time, uuid
from datetime import datetime, timezone

ZONE=Path(__file__).resolve().parent
MAP=ZONE.parent
def now(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    p=Path(p); tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
    for attempt in range(5):
        try: tmp.replace(p); return
        except OSError:
            if attempt==4: raise
            time.sleep(.25)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p,role):
    p=Path(p)
    with Image.open(p) as im: size=list(im.size)
    return {'file':p.as_posix(),'sha256':sha(p),'size':size,'role':role,'readAtUtc':now()}
def geometry(ident):
    r,c,pr,pc=map(int,re.fullmatch(r'r(\d+)_c(\d+)_p(\d+)_(\d+)(?:_v\d+)?',ident).groups())
    assert (r,c) in [(1,13),(1,14),(2,13),(2,14)]
    x=(c-1)*4096+(pc-1)*1024; y=(r-1)*4096+(pr-1)*1024
    return {'id':ident,'coreWorldBox':[x,y,x+1024,y+1024],'nativeWorldBox':[x-115,y-115,x+1139,y+1139],'coreCrop':[115,115,1139,1139]}
def progress(**kwargs):
    p=ZONE/'progress.json'; d=read(p) if p.exists() else {'assignment':['r02_c13','r02_c14','r01_c13','r01_c14'],'formalAcceptedCount':0,'candidateTiles':[],'builtinOnly':True,'paidApiAllowed':False}
    d.update(kwargs); d['updatedAtUtc']=now(); write(p,d)
def latest(folder,ident):
    files=list(Path(folder).glob(ident+'*.png'))
    files=[f for f in files if re.fullmatch(re.escape(ident)+r'(?:_v\d+)?\.png',f.name)]
    return max(files,key=lambda f:int(re.search(r'_v(\d+)',f.stem).group(1)) if '_v' in f.stem else 1) if files else None
def auto(ident):
    r,c,pr,pc=map(int,re.fullmatch(r'r(\d+)_c(\d+)_p(\d+)_(\d+)',ident).groups()); ns=[]
    south=f'r{r+(pr==4):02}_c{c:02}_p{1 if pr==4 else pr+1:02}_{pc:02}'
    for folder in [ZONE/'native',MAP/'northeast/native']:
        f=latest(folder,south)
        if f: ns.append(str(f)); break
    west=f'r{r:02}_c{c-(pc==1):02}_p{pr:02}_{4 if pc==1 else pc-1:02}'
    for folder in [ZONE/'native',MAP/'northeast/native']:
        f=latest(folder,west)
        if f: ns.append(str(f)); break
    prepare(ident,ns)
def prepare(ident,neighbors,base=None):
    for d in ['guides','prompts','native','receipts','candidates','qa']: (ZONE/d).mkdir(exist_ok=True)
    contract=read(MAP/'production-contract.json'); p=geometry(ident); a=p['nativeWorldBox']
    layout=Image.open(contract['layoutReference']).convert('RGB')
    guide=Image.open(base).convert('RGB') if base else layout.transform((1254,1254),Image.Transform.EXTENT,[v*1254/57344 for v in a],Image.Resampling.BICUBIC)
    # Map-edge halo repeats nearest layout coordinate as guidance only; never final pixels.
    if a[1]<0: guide.paste(guide.crop((0,115,1254,116)).resize((1254,115)),(0,0))
    if a[2]>57344: guide.paste(guide.crop((1138,0,1139,1254)).resize((115,1254)),(1139,0))
    anchors=[]
    for path in neighbors:
        src=Path(path); rec=read(src.with_suffix('.png.generation.json')); b=rec['nativeWorldBox']; im=Image.open(src).convert('RGB')
        assert im.size==(1254,1254)
        box=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
        assert box[0]<box[2] and box[1]<box[3]
        crop=[box[0]-b[0],box[1]-b[1],box[2]-b[0],box[3]-b[1]]; at=[box[0]-a[0],box[1]-a[1]]
        guide.paste(im.crop(crop),tuple(at)); anchors.append({**ref(src,'adjacent native anchor'),'overlapWorldBox':box,'sourceCrop':crop,'targetPaste':at})
    dest=ZONE/'guides'/f'{ident}.anchored-layout-only.png'; guide.save(dest)
    write(dest.with_suffix('.png.derivation.json'),{'operation':'exact layout coordinate crop plus unscaled adjacent native overlap; guide only, never final artwork','geometry':p,'anchors':anchors})
    refs=[ref(dest,'edit target: blurry pixels are layout-only; sharp overlap strips are native anchors')]
    if len(anchors)==1: refs.append(anchors[0])
    elif anchors:
        plate=Image.new('RGB',(1254*len(anchors),1254))
        for i,anchor in enumerate(anchors): plate.paste(Image.open(anchor['file']).convert('RGB'),(i*1254,0))
        platepath=ZONE/'guides'/f'{ident}.native-neighbors.png'; plate.save(platepath)
        refs.append({**ref(platepath,'unscaled native neighbors: left=SOUTH, right=WEST'),'sources':anchors})
    refs.extend([ref(contract['layoutReference'],'sole approved map layout authority'),ref(contract['detailStyleReference'],'material style only, NOT coordinate crop'),ref(contract['primaryStyleReference'],'rounded Daoist painterly style only; no UI/night/characters')])
    write(ZONE/'prompts'/f'{ident}.inputs.json',refs); write(ZONE/'guides'/f'{ident}.geometry.json',p)
    progress(status='preparing_native_generation',currentTile=ident[:7],currentPatch=ident,nextStep='Read every submitted reference; generate native1254 square; inspect unscaled core and overlaps.')
    print(json.dumps({'geometry':p,'references':refs},ensure_ascii=False))
def ingest(ident,source):
    source=Path(source); dest=ZONE/'native'/f'{ident}.png'; assert not dest.exists()
    shutil.copy2(source,dest)
    with Image.open(dest) as im: size=list(im.size); mode=im.mode
    p=geometry(ident); rec={**p,**ref(dest,'native builtin generated candidate'),'sourcePath':source.as_posix(),'tool':'image_gen.imagegen','route':'builtin','nativeWidth':size[0],'nativeHeight':size[1],'mode':mode,'prompt':(ZONE/'prompts'/f'{ident}.prompt.txt').as_posix(),'promptSha256':sha(ZONE/'prompts'/f'{ident}.prompt.txt'),'references':read(ZONE/'prompts'/f'{ident}.inputs.json'),'receipt':(ZONE/'receipts'/f'{ident}.tool.json').as_posix(),'actualModel':'unknown','actualQuality':'unknown','unverifiedReason':'Built-in tool does not disclose model/quality metadata.','submittedParameters':{'transparent_background':False,'model':None,'quality':None},'resizedAfterGeneration':False,'status':'candidate_unreviewed','generatedAtUtc':now()}
    write(dest.with_suffix('.png.generation.json'),rec)
    progress(status='native_inspection',currentPatch=ident,generatedNativeCount=len(list((ZONE/'native').glob('*.png'))),nextStep='Inspect native image and seams; then prepare next adjacent patch.')
    print(json.dumps({'file':str(dest),'size':size,'sha256':rec['sha256']}))
def assemble(tile):
    assert tile in ['r02_c13','r02_c14','r01_c13','r01_c14']
    im=Image.new('RGB',(4096,4096)); sources=[]; grid=[]
    for r in range(1,5):
        row=[]
        for c in range(1,5):
            src=latest(ZONE/'native',f'{tile}_p{r:02}_{c:02}'); assert src, (r,c)
            rec=read(src.with_suffix('.png.generation.json')); part=Image.open(src).convert('RGB'); assert part.size==(1254,1254)
            assert sha(src)==rec['sha256']
            crop=[115,115,1139,1139]; at=[(c-1)*1024,(r-1)*1024]; im.paste(part.crop(crop),tuple(at)); row.append(src.stem)
            sources.append({'file':src.as_posix(),'sha256':sha(src),'nativeSize':list(part.size),'sourceCrop':crop,'pasteAt':at,'generationRecord':src.with_suffix('.png.generation.json').as_posix()})
        grid.append(row)
    dest=ZONE/'candidates'/f'{tile}.4096-candidate.png'; assert not dest.exists()
    im.save(dest)
    rec={'tileId':tile,'file':dest.as_posix(),'sha256':sha(dest),'dimensions':[4096,4096],'method':'4x4 exact unscaled1024 cores cropped from measured1254 natives','sources':sources,'selectedCores':grid,'resizedFinalPixels':False,'status':'candidate_awaiting_full_review','formalAccepted':False,'externalEdges':'south/native available; other adjoining tiles require coordinated review','generatedAtUtc':now()}
    write(dest.with_suffix('.png.assembly.json'),rec)
    im.resize((1024,1024),Image.Resampling.LANCZOS).save(ZONE/'qa'/f'{tile}.preview-only1024.png')
    progress(status='tile_candidate_full_review',currentTile=tile,currentPatch=None,candidateTiles=[p.stem for p in (ZONE/'candidates').glob('*.png')],generatedNativeCount=len(list((ZONE/'native').glob('*.png'))),nextStep='Inspect all native seam evidence and full candidate; continue next tile in assignment order.')
    print(json.dumps({'candidate':dest.as_posix(),'dimensions':[4096,4096],'sha256':rec['sha256']}))
if __name__=='__main__':
    action,*args=sys.argv[1:]
    if action=='prepare': prepare(args[0],args[1:])
    elif action=='auto': auto(args[0])
    elif action=='repair': prepare(args[0],args[2:],args[1])
    elif action=='ingest': ingest(*args)
    elif action=='assemble': assemble(args[0])
