from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib,datetime,shutil,sys
T=Path(__file__).resolve().parent; R=T/'repairs'; R.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    p=Path(p);assert not p.exists(),str(p)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def latest():
    f=R/'latest-composition.json'
    if f.exists():return Path(read(f)['output'])
    return Path(read(T/'candidate'/'latest-assembly.json')['candidate']['path'])
def prepare(i,x,y,instruction):
    x,y=int(x),int(y); source=latest(); rect=[x,y,x+1254,y+1254]
    assert 0<=x<=2842 and 0<=y<=2842
    target=R/(i+'-target.png');assert not target.exists()
    Image.open(source).convert('RGB').crop(rect).save(target)
    contract=read(T.parent.parent/'production-contract.json')
    refs=[]
    for key in ['layoutReference','detailStyleReference','primaryStyleReference']:
        p=Path(contract[key]);im=Image.open(p)
        refs.append(dict(path=str(p),sha256=sha(p),dimensions=list(im.size),role=key+' reference ONLY'))
    refs.append(dict(path=str(target),sha256=sha(target),dimensions=[1254,1254],role='LAST IMAGE: only native repair edit target'))
    text=Path(instruction).read_text(encoding='utf-8')
    prompt='''Use case: precise-object-edit. Edit ONLY the LAST image, a native 1254x1254 detailed crop of our Taoist chibi game map. The first three images are approved layout/material/style references only. Preserve this exact crop, scale, daylight, natural grey stone colours, warm wood and existing objects. Do not zoom, pan, add architecture, furniture, leaves or new blue borders.
Repair the broken geometry described below. This is a full local object-and-connection repair: reconstruct each affected stone slab as one coherent outlined shape, with continuous matching grout connecting proper slab corners. No dangling lines, offsets, duplicated parallel seams or L-shaped fragments left from compositing. Do not hide defects with blur or decoration.
Keep all image perimeter pixels and the outer 60px strip unchanged, continue their incoming lines smoothly into the corrected interior. Keep existing wooden silhouettes and foliage unchanged. Use identical native crisp detail density, no resizing. Output ONE opaque native 1254x1254 PNG.
SPECIFIC REPAIR:
'''+text
    pp=R/(i+'.prompt.txt');pp.write_text(prompt,encoding='utf-8')
    req=dict(prompt=prompt,referenced_image_paths=[p['path'] for p in refs],transparent_background=False)
    write(R/(i+'.request.json'),req)
    meta=dict(id=i,createdAt=now(),tile='r14_c13',source=str(source),sourceSha256=sha(source),cropBoxIn4096=rect,target=str(target),targetSha256=sha(target),references=refs,requestSha256=sha(R/(i+'.request.json')),promptSha256=sha(pp),actualModel=None,actualQuality=None,operation='integer native crop only; no resizing')
    write(R/(i+'.target.json'),meta)
    print(json.dumps(dict(id=i,request=str(R/(i+'.request.json')),target=str(target))))
def ingest(i,source):
    source=Path(source);dst=R/(i+'-native.png');im=Image.open(source);im.load()
    assert im.size==(1254,1254) and im.format=='PNG' and not dst.exists()
    meta=read(R/(i+'.target.json'));req=read(R/(i+'.request.json'));receipt=R/(i+'.receipt.json')
    assert receipt.exists()
    for ref in meta['references']:assert sha(ref['path'])==ref['sha256']
    shutil.copy2(source,dst)
    write(str(dst)+'.generation.json',dict(id=i,file=str(dst),sha256=sha(dst),generatedAt=read(receipt)['generatedAt'],width=1254,height=1254,format='PNG',mode=im.mode,tool='image_gen.imagegen',route='builtin',actualModel=None,actualQuality=None,configTarget=read(T.parent.parent.parent.parent.parent/'config'/'image-generation.json'),submittedParameters=dict(model=None,quality=None,**req),evidence=dict(receipt=str(receipt),receiptSha256=sha(receipt),originalOutputPath=str(source),originalSha256=sha(source)),preparation=meta,resizedAfterGeneration=False,finalArtUpscaled=False,status='native_repair_pending_composition_qa'))
    print(json.dumps(dict(id=i,native=str(dst),sha256=sha(dst))))
def apply(i,regions_path=None):
    meta=read(R/(i+'.target.json'));source=latest();rect=meta['cropBoxIn4096']
    a=Image.open(source).convert('RGB');target=Image.open(meta['target']).convert('RGB')
    assert np.array_equal(np.asarray(a.crop(rect)),np.asarray(target)),'Target changed due overlapping repair, prepare fresh'
    p=Image.open(R/(i+'-native.png')).convert('RGB')
    yy,xx=np.mgrid[:1254,:1254];d=np.minimum.reduce([yy,xx,1253-yy,1253-xx])
    alpha=np.uint8(np.clip((d-60)/8,0,1)*255)
    rule='60px source perimeter then 8px linear blend; remainder native replacement; NO resizing or blur'
    if regions_path:
        regions=read(regions_path); limited=np.zeros((1254,1254),dtype=np.float32)
        for region in regions:
            cx,cy,radius,feather=region
            distance=np.sqrt((xx-cx)**2+(yy-cy)**2)
            limited=np.maximum(limited,np.clip((radius-distance)/feather,0,1))
        alpha=np.minimum(alpha,np.uint8(limited*255))
        rule='Native repair limited to recorded circular composition regions '+json.dumps(regions)+'; each [cx,cy,radius,linearAlphaTransition] in native pixels; no resizing or blur; all other source pixels unchanged'
    mask=Image.fromarray(alpha);mp=R/(i+'-alpha.png');mask.save(mp)
    before=np.asarray(a).copy();a.paste(Image.composite(p,target,mask),(rect[0],rect[1]))
    out=T/'candidate'/('r14_c13-4k-'+i+'.png');assert not out.exists();a.save(out)
    outside=np.ones((4096,4096),bool);outside[rect[1]:rect[3],rect[0]:rect[2]]=False
    assert np.array_equal(before[outside],np.asarray(a)[outside])
    entry=dict(id=i,createdAt=now(),source=str(source),sourceSha256=sha(source),native=str(R/(i+'-native.png')),nativeSha256=sha(R/(i+'-native.png')),placement=rect,alpha=str(mp),alphaSha256=sha(mp),maskRule=rule,output=str(out),outputSha256=sha(out),outsideRepairUnchanged=True,formalAccepted=False)
    write(R/(i+'.composition.json'),entry)
    (R/'latest-composition.json').write_text(json.dumps(entry,indent=2),encoding='utf-8')
    a.resize((1024,1024),Image.Resampling.LANCZOS).save(T/'review'/('overview-'+i+'-preview-only.png'))
    print(json.dumps(entry))
if __name__=='__main__':globals()[sys.argv[1]](*sys.argv[2:])

