"""Unscaled native repair provenance and local compositing, southeast r13_c13 only."""
from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib,datetime,shutil,sys
B=Path(__file__).resolve().parent;T=B/'r13_c13';R=T/'repairs'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def ingest(i,source):
    source=Path(source);dst=R/f'{i}-native.png';im=Image.open(source);im.load()
    assert im.size==(1254,1254) and im.format=='PNG' and not dst.exists()
    shutil.copy2(source,dst);req=read(R/f'{i}.request.json');target=read(R/f'{i}.target.json')
    for ref in target['references']:assert sha(ref['path'])==ref['sha256']
    write(R/f'{i}-native.png.generation.json',{'id':i,'file':str(dst),'sha256':sha(dst),'generatedAt':now(),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(B/'model-verification.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':req['referenced_image_paths']},'actualModel':None,'actualQuality':None,'backendModelVerified':False,'unverifiedReason':'Builtin tool exposes no model or quality selectors or metadata.','evidence':{'receipt':str(R/f'{i}.receipt.json'),'request':str(R/f'{i}.request.json'),'originalOutputPath':str(source),'originalSha256':sha(source)},'prompt':str(R/f'{i}.prompt.txt'),'promptSha256':sha(R/f'{i}.prompt.txt'),'references':target['references'],'targetMetadata':target,'resizedAfterGeneration':False,'finalArtUpscaled':False,'status':'native_repair_pending_composition_qa'})
    print(json.dumps({'native':str(dst),'size':im.size,'sha256':sha(dst)}))
def apply(i):
    meta=read(R/f'{i}.target.json');original=Path(meta['source']);rect=meta['cropBoxIn4096'];native=R/f'{i}-native.png'
    current_source_sha=sha(original)
    a=Image.open(original).convert('RGB');p=Image.open(native).convert('RGB');assert p.size==(1254,1254)
    assert np.array_equal(np.asarray(a.crop(rect)),np.asarray(Image.open(meta['target']).convert('RGB'))), 'Repair target crop changed; prepare again from current pixels.'
    # Preserve 24px source perimeter, interpolate only the next24px. Entire inner1206 square uses new native pixels.
    yy,xx=np.mgrid[:1254,:1254];dist=np.minimum.reduce([yy,xx,1253-yy,1253-xx])
    alpha=np.uint8(np.clip((dist-24)/24,0,1)*255);mask=Image.fromarray(alpha);maskpath=R/f'{i}-composition-alpha.png';mask.save(maskpath)
    before=np.asarray(a).copy();a.paste(Image.composite(p,a.crop(rect),mask),(rect[0],rect[1]))
    outside=np.ones((4096,4096),bool);outside[rect[1]:rect[3],rect[0]:rect[2]]=False
    assert np.array_equal(np.asarray(a)[outside],before[outside])
    out=T/'candidate'/'r13_c13-4k-candidate-repaired.png'
    temp=out.with_name('repair-writing.png');a.save(temp);saved=Image.open(temp);saved.load();assert saved.size==(4096,4096);temp.replace(out)
    history=read(R/'composition-history.json') if (R/'composition-history.json').exists() else {'steps':[]}
    history['steps'].append({'id':i,'appliedAt':now(),'source':str(original),'sourceSha256':current_source_sha,'targetCreationSourceSha256':meta['sourceSha256'],'native':str(native),'nativeSha256':sha(native),'placement':rect,'mask':str(maskpath),'maskSha256':sha(maskpath),'maskRule':'24px unchanged perimeter, next24px linear alpha, inner pixels100% native repair; no image resampling','output':str(out),'outputSha256':sha(out),'outsideRepairUnchanged':True,'formalAccepted':False})
    write(R/'composition-history.json',history)
    a.resize((1024,1024),Image.Resampling.LANCZOS).save(T/'review'/'overview-repaired-preview-only.png')
    pr=read(B/'progress.json');pr.update(updatedAt=now(),candidateFile=str(out),candidateSha256=sha(out),nativeRepairCount=len(list(R.glob('*-native.png.generation.json'))),internalQaPassed=False);write(B/'progress.json',pr)
    print(json.dumps(history['steps'][-1]))
if __name__=='__main__':
    if sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='apply':apply(sys.argv[2])

