from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime,sys,shutil
T=Path(__file__).resolve().parent;R=T/'repairs-north-20261011';R.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,v):
    assert not Path(p).exists(),p
    Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def prepare(i,x,instruction,source_override=None):
    x=int(x);latest=read(T/'candidate/latest-assembly.json');source=Path(source_override) if source_override else Path(latest['candidate']['path'])
    if source_override:assert source.resolve().is_relative_to((T/'candidate').resolve()) and source.is_file()
    else:assert sha(source)==latest['candidate']['sha256']
    north=T.parent/'r13_c13/candidate/r13_c13-4k-candidate-repaired.png'; old=Image.open(north).convert('RGB');current=Image.open(source).convert('RGB')
    assert old.size==current.size==(4096,4096)
    target=Image.new('RGB',(1254,1254));target.paste(old.crop((x,3696,x+1254,4096)),(0,0));target.paste(current.crop((x,0,x+1254,854)),(0,400))
    tp=R/(i+'-target.png');assert not tp.exists();target.save(tp)
    contract=read(T.parent.parent/'production-contract.json');refs=[]
    for k in ['layoutReference','detailStyleReference','primaryStyleReference']:
        p=Path(contract[k]);refs.append({'path':str(p),'sha256':sha(p),'dimensions':list(Image.open(p).size),'role':k+' reference ONLY'})
    refs.append({'path':str(tp),'sha256':sha(tp),'dimensions':[1254,1254],'role':'LAST IMAGE: exact native seam repair target; top400 rows immutable north anchor'})
    prompt='''Edit only the LAST attached native 1254x1254 image of our Taoist chibi game map; first three images are approved style/layout/material references only. This target contains two vertically adjacent real map crops, with their boundary at y=400: upper rows y=0..399 are the IMMUTABLE existing north map; lower rows y=400..1253 are the new south map. Repair the visual connection using ONLY the lower portion. Keep the upper 400 rows exactly unchanged. At y=400 every leaf, twig, stone slab and grout line must continue from its existing exact upper endpoints. Never hide the boundary with blur, a new border, added decor or a horizontal line. Keep the scale, crop, camera, colours and all already correct geometry unchanged. Preserve the lower 250 rows unchanged to connect back to the existing southern map. Output one opaque native1254x1254 PNG, no resizing or zoom. Reconstruct coherent objects across the join, not just texture.
SPECIFIC REPAIR:
'''+Path(instruction).read_text(encoding='utf-8')
    pp=R/(i+'.prompt.txt');pp.write_text(prompt,encoding='utf-8');req={'prompt':prompt,'referenced_image_paths':[r['path'] for r in refs],'transparent_background':False}
    rq=R/(i+'.request.json');write(rq,req)
    write(R/(i+'.target.json'),{'id':i,'createdAt':now(),'tile':'r14_c13','source':str(source),'sourceSha256':sha(source),'northSource':str(north),'northSourceSha256':sha(north),'northCropBox':[x,3696,x+1254,4096],'southCropBox':[x,0,x+1254,854],'target':str(tp),'targetSha256':sha(tp),'requestSha256':sha(rq),'promptSha256':sha(pp),'references':refs,'resampled':False,'actualModel':None,'actualQuality':None})
    print(json.dumps({'request':str(rq),'target':str(tp)}))
def ingest(i,original):
    src=Path(original);im=Image.open(src);im.load();assert im.format=='PNG' and im.size==(1254,1254)
    dst=R/(i+'-native.png');assert not dst.exists();meta=read(R/(i+'.target.json'));req=read(R/(i+'.request.json'));receipt=R/(i+'.receipt.json');rr=read(receipt)
    for p in meta['references']:assert sha(p['path'])==p['sha256']
    assert sha(meta['source'])==meta['sourceSha256'] and sha(meta['northSource'])==meta['northSourceSha256']
    shutil.copy2(src,dst)
    write(str(dst)+'.generation.json',{'id':i,'file':str(dst),'sha256':sha(dst),'width':1254,'height':1254,'format':'PNG','mode':im.mode,'route':'builtin','tool':'image_gen.imagegen','generatedAt':rr['generatedAt'],'actualModel':None,'actualQuality':None,'submittedParameters':dict(model=None,quality=None,**req),'preparation':meta,'evidence':{'receipt':str(receipt),'receiptSha256':sha(receipt),'originalOutputPath':str(src),'originalSha256':sha(src)},'resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'native_north_repair_pending_composition_qa'})
    print(json.dumps({'native':str(dst),'sha256':sha(dst)}))
if __name__=='__main__':globals()[sys.argv[1]](*sys.argv[2:])
