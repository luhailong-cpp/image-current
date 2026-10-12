"""Coordinate guides, records and lossless crops only. No AI/API calls or art drawing."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, argparse, shutil, os, time, uuid
from PIL import Image

ROOT=Path(__file__).resolve().parent
REPO=Path('D:/work/image')
CONTRACT=json.loads((ROOT.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
CONFIG_PATH=REPO/'config/image-generation.json'
CONFIG_EVIDENCE='current project config'
if CONFIG_PATH.exists():
    CONFIG=json.loads(CONFIG_PATH.read_text(encoding='utf-8-sig'))
else:
    # Recording already-returned images must remain possible if shared config is moved.
    # This is the historical batch target, not a newly verified active configuration.
    CONFIG=json.loads((ROOT/'reference-audit.json').read_text(encoding='utf-8-sig'))['configSnapshot']
    CONFIG_EVIDENCE='historical batch reference-audit snapshot; shared config missing at ingest'
REFS=[(CONTRACT['layoutReference'],'sole full-map coordinate/layout reference'),(CONTRACT['detailStyleReference'],'independent close-up material/style reference, NOT a coordinate crop'),(CONTRACT['primaryStyleReference'],'primary approved Daoist Q painterly style; no UI/night scene transfer')]

def now(): return datetime.now(timezone.utc).isoformat()
def hashfile(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    # A reader or file watcher may briefly hold a Windows JSON file open.
    # Stage a complete sibling file so a failed replacement cannot truncate state.
    staged=path.with_name(path.name+'.writing-'+uuid.uuid4().hex+'.tmp')
    staged.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for attempt in range(6):
        try:
            os.replace(staged,path)
            return
        except OSError:
            if attempt==5:
                raise
            time.sleep(0.1*(attempt+1))
def load(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def metadata(path,role):
    p=Path(path)
    with Image.open(p) as im: size=list(im.size)
    return {'path':p.as_posix(),'role':role,'sha256':hashfile(p),'dimensions':size}
def update(**fields):
    p=ROOT/'progress.json'; state=load(p) if p.exists() else {}
    state.update(fields); state['updatedAtUtc']=now(); dump(p,state)
def coords(r,c,sr,sc):
    x=(c-1)*4096+(sc-1)*1024; y=(r-1)*4096+(sr-1)*1024
    box=[x-115,y-115,x+1139,y+1139]
    return {'tile':f'r{r:02}_c{c:02}','subrow':sr,'subcolumn':sc,'coreGlobalBox':[x,y,x+1024,y+1024],'nativeGlobalBox':box,'overviewFloatBox':[v*1254/57344 for v in box],'coreCrop':[115,115,1139,1139],'expectedNativeDimensions':[1254,1254]}
def init():
    for d in ['guides','native','prompts','receipts','qa','output']: (ROOT/d).mkdir(parents=True,exist_ok=True)
    refs=[metadata(*r) for r in REFS]
    assert refs[0]['sha256']==CONTRACT['layoutSha256']
    assert refs[1]['sha256']==CONTRACT['detailSha256']
    dump(ROOT/'reference-audit.json',{'checkedAtUtc':now(),'references':refs,'contractSha256':hashfile(ROOT.parent/'production-contract.json'),'configSnapshot':CONFIG,'officialVerification':{'date':'2026-10-09','modelPage':'https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','qualityPage':'https://developers.openai.com/api/reference/resources/images/methods/generate','result':'Official pages fetched: Sunburst model and max supported. Same authorized batch config retained. Actual builtin selectors unavailable; actual output model/quality unconfirmed.'}})
    tiles=[]
    for r in range(8,15):
        for c in range(1,8):
            tiles.append({'id':f'r{r:02}_c{c:02}','origin':[(c-1)*4096,(r-1)*4096],'status':'not_started','patches':[coords(r,c,sr,sc) for sr in range(1,5) for sc in range(1,5)]})
    dump(ROOT/'coordinate-plan.json',{'halfOpenBoxes':True,'nativeSpacing':1024,'nativeOverlap':230,'tiles':tiles,'crossZoneEdges':{'north':28672,'east':28672},'worldAreaRatioToMain':0.75,'worldSize':None,'capacity5000Validated':False})
    if not (ROOT/'progress.json').exists(): update(status='preparing_first_native_patch',generatedNativeCount=0,usableNativeCount=0,complete4kCount=0,formalAcceptedCount=0,currentTile='r09_c03',currentPatch='s01_01',nextStep='Generate coordinate-correct first native patch with builtin image_gen',errors=[],totalTiles=49)
def prepare(r,c,sr,sc,attempt):
    co=coords(r,c,sr,sc); stem=f"{co['tile']}_s{sr:02}_{sc:02}_v{attempt:02}"
    p=ROOT/'guides'/f'{stem}.layout-only.png'
    with Image.open(REFS[0][0]) as im: im.transform((1254,1254),Image.Transform.EXTENT,co['overviewFloatBox'],Image.Resampling.BICUBIC).save(p)
    dump(str(p)+'.derivation.json',{'file':p.as_posix(),'sha256':hashfile(p),'operation':'Bicubic EXTENT resampling of overview float coordinates; LAYOUT-ONLY, not native detail or final contribution','derivedFrom':metadata(*REFS[0]),**co})
    dump(ROOT/'prompts'/f'{stem}.coordinates.json',co)
    update(status='guide_ready',currentTile=co['tile'],currentPatch=f's{sr:02}_{sc:02}',nextStep=f'Inspect guide and generate {stem}')
    print(json.dumps({'guide':p.as_posix(),'stem':stem,**co}))
def ingest(stem,source):
    source=Path(source); dest=ROOT/'native'/f'{stem}.png'
    if dest.exists(): raise RuntimeError('Never overwrite a recorded output')
    shutil.copy2(source,dest)
    with Image.open(dest) as im: im.load(); size=im.size; fmt=im.format
    req=load(ROOT/'prompts'/f'{stem}.request.json')
    receipt=ROOT/'receipts'/f'{stem}.tool.json'
    rec={'file':dest.as_posix(),'sha256':hashfile(dest),'generatedAt':now(),'width':size[0],'height':size[1],'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':CONFIG,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具无model/quality选择器，返回未披露可核实型号和质量。','prompt':(ROOT/'prompts'/f'{stem}.prompt.txt').as_posix(),'references':req['references'],'sourceToolPath':source.as_posix(),'evidence':[{'path':receipt.as_posix(),'type':'tool receipt; raw image/base64 omitted'}],'coordinates':load(ROOT/'prompts'/f'{stem}.coordinates.json'),'status':'awaiting_visual_QA','nativeSizeMatchesPlan':list(size)==[1254,1254]}
    rec['configEvidenceAtIngest']=CONFIG_EVIDENCE
    dump(str(dest)+'.generation.json',rec)
    state=load(ROOT/'progress.json'); update(generatedNativeCount=state['generatedNativeCount']+1,status='native_awaiting_QA',nextStep=f'Inspect {stem} at native resolution; do not extend before coordinate QA')
    print(json.dumps({'file':dest.as_posix(),'size':size,'sha256':rec['sha256']}))

def overlap_guide(stem,neighbors):
    co=load(ROOT/'prompts'/f'{stem}.coordinates.json'); box=co['nativeGlobalBox']
    layout=ROOT/'guides'/f'{stem}.layout-only.png'
    with Image.open(layout) as im: canvas=im.convert('RGB')
    sources=[metadata(layout,'layout-only base, never final contribution')]
    for neighbor in neighbors:
        p=ROOT/'native'/f'{neighbor}.png'; rec=load(str(p)+'.generation.json'); nb=rec['coordinates']['nativeGlobalBox']
        if rec['width']!=1254 or rec['height']!=1254: raise RuntimeError('Recalculate coordinates for nonstandard native size')
        intersection=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
        if intersection[2]<=intersection[0] or intersection[3]<=intersection[1]: raise RuntimeError('No overlap')
        crop=[intersection[0]-nb[0],intersection[1]-nb[1],intersection[2]-nb[0],intersection[3]-nb[1]]
        dest=[intersection[0]-box[0],intersection[1]-box[1]]
        with Image.open(p) as im: canvas.paste(im.crop(crop),dest)
        sources.append({**metadata(p,'adjacent native constraint, cropped at original size'), 'sourceCrop':crop,'destinationTopLeft':dest,'generationRecord':str(p)+'.generation.json'})
    out=ROOT/'guides'/f'{stem}.native-overlap-guide.png'; canvas.save(out)
    dump(str(out)+'.derivation.json',{'file':out.as_posix(),'sha256':hashfile(out),'operation':'mechanical crop/paste native overlap over layout-only base; no drawing, blending, or native resampling','derivedFrom':sources,'coordinates':co,'finalArt':False})
    print(out.as_posix())

def seamcheck(a,b,direction,name):
    pa=ROOT/'native'/f'{a}.png'; pb=ROOT/'native'/f'{b}.png'
    ra=load(str(pa)+'.generation.json'); rb=load(str(pb)+'.generation.json')
    ba=ra['coordinates']['nativeGlobalBox']; bb=rb['coordinates']['nativeGlobalBox']
    delta=(bb[0]-ba[0],bb[1]-ba[1])
    if direction not in ('horizontal','vertical'): raise ValueError('Unknown direction')
    if delta != ((1024,0) if direction=='horizontal' else (0,1024)): raise ValueError('Not adjacent regular grid patches')
    with Image.open(pa) as ia, Image.open(pb) as ib:
        if ia.size!=(1254,1254) or ib.size!=(1254,1254): raise ValueError('Recompute nonstandard native coverage before seamcheck')
        if direction=='horizontal':
            boxes=[[839,0,1139,1254],[115,0,415,1254]]; size=(600,1254); dest=(300,0)
        else:
            boxes=[[0,839,1254,1139],[0,115,1254,415]]; size=(1254,600); dest=(0,300)
        im=Image.new('RGB',size); im.paste(ia.crop(boxes[0]),(0,0)); im.paste(ib.crop(boxes[1]),dest)
    out=ROOT/'qa'/f'{name}.png'; im.save(out)
    dump(str(out)+'.derivation.json',{'file':str(out),'sha256':hashfile(out),'operation':'native hard crop/paste; no resampling or feather','derivedFrom':[metadata(pa,'first native'),metadata(pb,'second native')],'sourceCrops':boxes,'seamAt':300,'direction':direction,'status':'awaiting_visual_QA'})
    print(str(out))

def save_request(stem,neighbor):
    guide=ROOT/'guides'/f'{stem}.native-overlap-guide.png'
    refs=[metadata(guide,'edit target: recorded adjacent native overlaps at 1:1; remainder layout-only'),metadata(ROOT/'native'/f'{neighbor}.png','adjacent native context; exact overlap coordinates in guide derivation')]+[metadata(*r) for r in REFS]
    dump(ROOT/'prompts'/f'{stem}.request.json',{'tool':'image_gen.imagegen','references':refs,'embeddedNeighborDerivation':str(guide)+'.derivation.json','submittedParameters':{'model':None,'quality':None,'transparent_background':False}})
    update(status='generating',nextStep='Await builtin '+stem)

def resolvepair(a,b,repair,outa,outb):
    paths=[ROOT/'native'/f'{s}.png' for s in (a,b,repair)]
    records=[load(str(p)+'.generation.json') for p in paths]
    boxes=[r['coordinates']['nativeGlobalBox'] for r in records]
    assert boxes[1][0]-boxes[0][0]==1024 and boxes[0][1]==boxes[1][1]
    offset=boxes[2][0]-boxes[0][0]
    assert 0<=offset<=1024 and boxes[2][1]==boxes[0][1]
    ims=[Image.open(p).convert('RGB') for p in paths]
    assert all(im.size==(1254,1254) for im in ims)
    canvas=Image.new('RGB',(2278,1254)); canvas.paste(ims[0].crop((0,0,1139,1254)),(0,0));canvas.paste(ims[1].crop((115,0,1254,1254)),(1139,0));canvas.paste(ims[2],(offset,0))
    qa=ROOT/'qa'/f'{repair}-assembled.png';canvas.save(qa)
    sources=[{**metadata(p,'native contribution'),'generationRecord':str(p)+'.generation.json'} for p in paths]
    dump(str(qa)+'.derivation.json',{'operation':'hard native crop/paste, no resampling or feather','derivedFrom':sources,'sourceCrops':[[0,0,1139,1254],[115,0,1254,1254],[0,0,1254,1254]],'destinationTopLeft':[[0,0],[1139,0],[offset,0]],'globalBox':[boxes[0][0],boxes[0][1],boxes[1][2],boxes[1][3]]})
    for i,(name,x) in enumerate(((outa,0),(outb,1024))):
        dest=ROOT/'native'/f'{name}.png'
        if dest.exists(): raise RuntimeError('Do not overwrite derived sources')
        canvas.crop((x,0,x+1254,1254)).save(dest)
        dump(str(dest)+'.generation.json',{'file':str(dest),'sha256':hashfile(dest),'width':1254,'height':1254,'tool':'mechanical_crop','route':'derived','derivedFrom':sources,'assembly':str(qa),'assemblyCrop':[x,0,x+1254,1254],'coordinates':records[i]['coordinates'],'actualModel':None,'actualQuality':None,'status':'candidate'})
    for name,box in [('left',(max(0,offset-250),0,offset+250,1254)),('right',(offset+1004,0,min(2278,offset+1504),1254))]:
        canvas.crop(box).save(ROOT/'qa'/f'{repair}-{name}100.png')
    print(str(qa))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
    sp.add_parser('init')
    p=sp.add_parser('prepare'); p.add_argument('r',type=int); p.add_argument('c',type=int); p.add_argument('sr',type=int); p.add_argument('sc',type=int); p.add_argument('--attempt',type=int,default=1)
    p=sp.add_parser('ingest'); p.add_argument('stem'); p.add_argument('source')
    p=sp.add_parser('overlap'); p.add_argument('stem'); p.add_argument('neighbors',nargs='+')
    p=sp.add_parser('seamcheck'); p.add_argument('a'); p.add_argument('b'); p.add_argument('direction'); p.add_argument('name')
    p=sp.add_parser('request'); p.add_argument('stem'); p.add_argument('neighbor')
    p=sp.add_parser('resolvepair'); p.add_argument('a');p.add_argument('b');p.add_argument('repair');p.add_argument('outa');p.add_argument('outb')
    a=ap.parse_args()
    if a.cmd=='init': init()
    elif a.cmd=='prepare': prepare(a.r,a.c,a.sr,a.sc,a.attempt)
    elif a.cmd=='ingest': ingest(a.stem,a.source)
    elif a.cmd=='overlap': overlap_guide(a.stem,a.neighbors)
    elif a.cmd=='seamcheck': seamcheck(a.a,a.b,a.direction,a.name)
    elif a.cmd=='request': save_request(a.stem,a.neighbor)
    elif a.cmd=='resolvepair': resolvepair(a.a,a.b,a.repair,a.outa,a.outb)
