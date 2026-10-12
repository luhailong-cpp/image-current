from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib,datetime
B=Path(__file__).resolve().parent;T=B/'r13_c13';R=T/'repairs';id='umbrella-edge-context-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
meta=read(R/f'{id}.target.json');source=Path(meta['source']);assert sha(source)==meta['sourceSha256']
im=Image.open(source).convert('RGB');box=meta['cropBoxInSource4326'];target=Image.open(meta['target'])
assert np.array_equal(np.asarray(im.crop(box)),np.asarray(target))
native=R/f'{id}-native.png';patch=Image.open(native).convert('RGB');assert patch.size==(1254,1254)
yy,xx=np.mgrid[:1254,:1254];dist=np.minimum.reduce([yy,xx,1253-yy,1253-xx]);mask=Image.fromarray(np.uint8(np.clip((dist-24)/24,0,1)*255))
maskpath=R/f'{id}-composition-alpha.png';mask.save(maskpath)
before=np.asarray(im).copy();im.paste(Image.composite(patch,im.crop(box),mask),(box[0],box[1]));outside=np.ones((4326,4326),bool);outside[box[1]:box[3],box[0]:box[2]]=False
assert np.array_equal(np.asarray(im)[outside],before[outside])
ctx=T/'candidate'/'r13_c13-context-4326-repaired.png';im.save(ctx)
core=im.crop((115,115,4211,4211));out=T/'candidate'/'r13_c13-4k-candidate-repaired.png';core.save(out)
assert Image.open(ctx).size==(4326,4326) and Image.open(out).size==(4096,4096)
core.resize((1024,1024),Image.Resampling.LANCZOS).save(T/'review'/'overview-repaired-preview-only.png')
record={'id':id,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source),'sourceSha256':sha(source),'sourceDerivation':meta['sourceDerivation'],'native':str(native),'nativeSha256':sha(native),'generationRecord':str(R/f'{id}-native.png.generation.json'),'placementIn4326':box,'placementInTileCoordinates':meta['cropBoxIn4096'],'mask':str(maskpath),'maskSha256':sha(maskpath),'maskRule':'24px unchanged perimeter, next24px linear alpha; formal rightedge is inside repair, corrected native pixels extend into halo','sourceResampling':False,'outsideRepairUnchanged':True,'outputContext':str(ctx),'outputContextSha256':sha(ctx),'outputCore':str(out),'outputCoreSha256':sha(out),'finalCropBox':[115,115,4211,4211],'formalAccepted':False,'externalSeamsVerified':False}
write(R/'context-composition.json',record)
pr=read(B/'progress.json');pr.update(updatedAt=record['at'],status='candidate_context_edge_review',generatedNativeCount=29,nativeRepairCount=7,candidateSha256=sha(out),candidateContextFile=str(ctx),candidateContextSha256=sha(ctx),internalQaPassed=False,exactReplayVerified=False,nextStep='Check repaired rightedge in4096 and corrected halo at100%; rerun source-to-final exact replay.')
write(B/'progress.json',pr)
print(json.dumps({'candidate':str(out),'candidateSha256':sha(out),'context':str(ctx),'contextSha256':sha(ctx),'formalAccepted':False}))

