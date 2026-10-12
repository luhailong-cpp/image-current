from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, datetime, shutil, sys

ZONE = Path(__file__).resolve().parent
PROJECT = ZONE.parent
REPO = Path('D:/work/image')
CONTRACT = json.loads((PROJECT/'production-contract.json').read_text(encoding='utf-8-sig'))
CONFIG = json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig'))
PYTHON = 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))

def init():
    tile=ZONE/'r05_c04'
    for d in ('layout-only','native','prompts','receipts','qa','candidate'): (tile/d).mkdir(parents=True,exist_ok=True)
    layout=Image.open(CONTRACT['layoutReference']).convert('RGB')
    x,y=12288,16384
    coords={'tile':'r05_c04','tileWorldBox':[x,y,x+4096,y+4096],'canvas':[65536,65536],'patches':[]}
    for sr in range(1,5):
        for sc in range(1,5):
            px,py=x+(sc-1)*1024-115,y+(sr-1)*1024-115
            box=[px,py,px+1254,py+1254]
            guide=layout.transform((1254,1254),Image.Transform.EXTENT,tuple(v*layout.width/65536 for v in box),Image.Resampling.BICUBIC)
            f=tile/'layout-only'/f's{sr:02d}_{sc:02d}.layout-only.png'
            guide.save(f)
            write(f.with_suffix('.png.derivation.json'),{'file':str(f),'role':'layout-only; not game artwork or native detail','derivedFrom':{'file':CONTRACT['layoutReference'],'sha256':sha(CONTRACT['layoutReference']),'nativeSize':list(layout.size)},'worldBox':box,'operation':'crop with bicubic enlargement solely for geometric layout reference','size':list(guide.size)})
            coords['patches'].append({'id':f's{sr:02d}_{sc:02d}','worldBoxWithHalo':box,'coreWorldBox':[px+115,py+115,px+1139,py+1139],'coreCrop':[115,115,1139,1139]})
    tileguide=layout.transform((1024,1024),Image.Transform.EXTENT,(x*layout.width/65536,y*layout.height/65536,(x+4096)*layout.width/65536,(y+4096)*layout.height/65536),Image.Resampling.BICUBIC)
    tileguide.save(tile/'layout-only'/'tile.layout-only.png')
    mark=layout.copy(); draw=ImageDraw.Draw(mark); draw.rectangle((x*layout.width/65536,y*layout.height/65536,(x+4096)*layout.width/65536,(y+4096)*layout.height/65536),outline=(255,0,255),width=3)
    mark.save(tile/'layout-only'/'location.layout-only.png')
    write(tile/'coordinates.json',coords)
    write(ZONE/'batch-evidence.json',{'checkedAt':now(),'configurationSnapshot':CONFIG,'officialSources':['https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','https://developers.openai.com/api/reference/resources/images/methods/generate'],'finding':'Official model and image API pages list gpt-image-2.5-sunburst and max; current built-in tool has no model or quality selector. Actual execution model and quality remain unverified.','sharedConfigurationModified':False,'references':[{'file':CONTRACT[k],'sha256':sha(CONTRACT[k]),'role':k} for k in ('layoutReference','detailStyleReference','primaryStyleReference')]})
    progress('First native patch ready for generation')

def progress(next_step):
    records=list(ZONE.glob('r*/native/*.generation.json'))
    native=[read(p) for p in records]
    p={'zone':'northwest','updatedAt':now(),'status':'in_progress','tileRows':[1,8],'tileColumns':[1,8],'firstTile':'r05_c04','generatedNativeCount':len(native),'complete4kCandidateCount':0,'formalAcceptedCount':0,'activeTile':'r05_c04','nativeFiles':[r['file'] for r in native],'nextStep':next_step,'clientMappingValidated':False,'capacity5000Validated':False,'artCanvasPixels':[65536,65536],'nativeCorePixels':1024,'haloPixels':115}
    p['selectedNativeCount']=len(list(ZONE.glob('r*/native/s??_??.png')))
    p['generatedNativeCountIncludesRevisions']=True
    p['complete4kCandidateCount']=len({f.parent.parent for f in ZONE.glob('r*/candidate/*-candidate-*.png')})
    p['candidateCountMeansPixelCoverageNotAcceptance']=True
    write(ZONE/'progress.json',p)

def prepare(sr,sc,suffix=''):
    tile=ZONE/'r05_c04'; pid=f's{sr:02d}_{sc:02d}'
    base=Image.open(tile/'layout-only'/f'{pid}.layout-only.png').convert('RGB')
    refs=[]
    # Paint already-generated overlap into the guide at exact world coordinates, never resize native pixels.
    px,py=(sc-1)*1024-115,(sr-1)*1024-115
    selection=read(tile/'selection.json') if (tile/'selection.json').exists() else {}
    for default_path in sorted((tile/'native').glob('s??_??.png')):
        nr,nc=map(int,default_path.stem[1:].split('_'))
        if nr==sr and nc==sc: continue
        p=Path(selection.get(default_path.stem,str(default_path)))
        nx,ny=(nc-1)*1024-115,(nr-1)*1024-115
        sx,sy=max(px,nx),max(py,ny); ex,ey=min(px+1254,nx+1254),min(py+1254,ny+1254)
        if ex>sx and ey>sy:
            n=Image.open(p).convert('RGB')
            assert n.size==(1254,1254), n.size
            base.paste(n.crop((sx-nx,sy-ny,ex-nx,ey-ny)),(sx-px,sy-py))
            refs.append({'file':str(p),'sha256':sha(p),'role':'native adjacent overlap anchor','sourceBox':[sx-nx,sy-ny,ex-nx,ey-ny],'targetBox':[sx-px,sy-py,ex-px,ey-py]})
    guide_id=pid+('_'+suffix if suffix else '')
    guide=tile/'layout-only'/f'{guide_id}.continuation-guide.png';base.save(guide)
    write(guide.with_suffix('.png.derivation.json'),{'file':str(guide),'role':'mixed native overlap and layout-only guide, never final artwork','nativeNeighbors':refs,'layoutSource':str(tile/'layout-only'/f'{pid}.layout-only.png'),'operation':'exact unscaled pasting of native overlap into layout-only guide','worldBox':[12288+px,16384+py,12288+px+1254,16384+py+1254]})
    return guide,refs

def ingest(pid,source,receipt):
    tile=ZONE/'r05_c04'; dest=tile/'native'/f'{pid}.png'
    assert not dest.exists(), str(dest)
    shutil.copy2(source,dest)
    with Image.open(dest) as im: dimensions=im.size; fmt=im.format; info={k:str(v)[:1000] for k,v in im.info.items()}
    request=read(tile/'receipts'/f'{pid}.request.json')
    for ref in request['references']: ref['sha256']=sha(ref['file'])
    rec={'file':str(dest),'sha256':sha(dest),'generatedAt':now(),'width':dimensions[0],'height':dimensions[1],'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':CONFIG,'submittedParameters':{'model':None,'quality':None,**request['parameters']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具未开放 model/quality 选择器，返回未披露可核实型号与质量。','prompt':str(tile/'prompts'/f'{pid}.txt'),'references':request['references'],'evidence':{'receipt':str(tile/'receipts'/f'{pid}.result.json'),'pngInfo':info,'hostOutputPath':source},'coreCrop':[115,115,1139,1139],'nativeDimensionsMatchPlan':dimensions==(1254,1254),'status':'native_candidate_pending_seam_review'}
    write(tile/'receipts'/f'{pid}.result.json',read(Path(receipt)))
    write(dest.with_suffix('.png.generation.json'),rec)
    progress('Continue from '+pid+' using exact native overlap anchors; inspect every output before continuing')
    print(json.dumps({'file':str(dest),'size':dimensions,'sha256':rec['sha256']},ensure_ascii=False))

if __name__=='__main__':
    if sys.argv[1]=='init': init()
    elif sys.argv[1]=='prepare': print(prepare(int(sys.argv[2]),int(sys.argv[3]),sys.argv[4] if len(sys.argv)>4 else '')[0])
    elif sys.argv[1]=='ingest': ingest(*sys.argv[2:])
