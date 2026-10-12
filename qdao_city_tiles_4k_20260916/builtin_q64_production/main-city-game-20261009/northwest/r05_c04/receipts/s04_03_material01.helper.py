from pathlib import Path
from PIL import Image
import hashlib,json,datetime,shutil,sys
BASE=Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
if sys.argv[1]=='guide':
    pid=sys.argv[2]; col=int(pid[4:6])
    target=BASE/'native'/f's04_{col:02d}_fix01.png'
    im=Image.open(target).convert('RGB')
    refs=[{'file':str(target),'sha256':sha(target),'operation':'unchanged base edit target'}]
    north=BASE/'native'/f's03_{col:02d}.png'
    im.paste(Image.open(north).convert('RGB').crop((0,1024,1254,1254)),(0,0))
    refs.append({'file':str(north),'sha256':sha(north),'sourceBox':[0,1024,1254,1254],'targetBox':[0,0,1254,230]})
    if col==4:
        west=BASE/'native'/'s04_03_material01.png'
        im.paste(Image.open(west).convert('RGB').crop((1024,0,1254,1254)),(0,0))
        refs.append({'file':str(west),'sha256':sha(west),'sourceBox':[1024,0,1254,1254],'targetBox':[0,0,230,1254]})
    guide=BASE/'layout-only'/f'{pid}.material-guide.png'
    assert not guide.exists()
    im.save(guide)
    write(guide.with_suffix('.png.derivation.json'),{'file':str(guide),'role':'exact native overlap guide; not game asset','operation':'paste native neighbor overlap without resize, warp, blending or filtering','size':list(im.size),'derivedFrom':refs})
    print(str(guide))
elif sys.argv[1]=='ingest':
    pid,source=sys.argv[2:4]
    dest=BASE/'native'/f'{pid}.png'; assert not dest.exists()
    shutil.copy2(source,dest)
    with Image.open(dest) as im: dimensions=im.size; fmt=im.format; info={k:str(v)[:1000] for k,v in im.info.items()}
    request=read(BASE/'receipts'/f'{pid}.request.json')
    for ref in request['references']: ref['sha256']=sha(ref['file'])
    cfg=read(Path('D:/work/image/config/image-generation.json'))
    target=request['references'][0]['file']
    record={'file':str(dest),'sha256':sha(dest),'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'width':dimensions[0],'height':dimensions[1],'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':cfg,'submittedParameters':{'model':None,'quality':None,**request['parameters']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具未开放 model/quality 选择器，返回未披露可核实型号与质量。','prompt':str(BASE/'prompts'/f'{pid}.txt'),'references':request['references'],'editedFrom':{'file':target,'sha256':sha(target),'generationRecord':target+'.generation.json'},'evidence':{'request':str(BASE/'receipts'/f'{pid}.request.json'),'receipt':str(BASE/'receipts'/f'{pid}.result.json'),'pngInfo':info,'hostOutputPath':source},'coreCrop':[115,115,1139,1139],'nativeDimensionsMatchPlan':dimensions==(1254,1254),'status':'native_candidate_pending_seam_review'}
    write(dest.with_suffix('.png.generation.json'),record)
    print(json.dumps({'file':str(dest),'size':dimensions,'sha256':record['sha256']},ensure_ascii=False))

