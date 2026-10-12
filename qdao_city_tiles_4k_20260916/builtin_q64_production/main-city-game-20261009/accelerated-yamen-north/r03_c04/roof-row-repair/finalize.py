from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):
 p=Path(p);v={'file':str(p),'sha256':sha(p)}
 if p.suffix=='.png':
  with Image.open(p) as im:v.update(width=im.width,height=im.height,mode=im.mode,format=im.format)
 return v
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rgb(p):return np.array(Image.open(p).convert('RGB'))
prep=read(O/'preparation.json')
receipts=[]
for side,versions in [('left',range(1,5)),('right',[1])]:
 for v in versions:
  d=O/side;rf=d/f'receipt-v{v}.json';r=read(rf);raw=d/f'raw-v{v}.png';host=Path(r['hostSourceFile']);params=Path(r['parametersFile']);args=read(params)
  assert raw.read_bytes()==host.read_bytes()
  r.update(raw=ref(raw),hostRaw=ref(host),parameters=ref(params),references=[ref(f) for f in args['referenced_image_paths']],
   nativePixels=[1254,1254],hostBytesUnmodified=True,actualModel=None,actualQuality=None,
   contextTileBox=prep[0 if side=='left' else 1]['contextTileBox'],contextWorldBox=prep[0 if side=='left' else 1]['contextWorldBox'])
  dump(rf,r);receipts.append(ref(rf))

d=O/'right';B=rgb(d/'context-native.png');R=rgb(d/'raw-v1.png')
x=np.arange(1254)[None,:]+.5;y=np.arange(1254)[:,None]+.5
def s(v,a,b):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
w=s(x,0,64)*(1-s(x,1000,1020))*s(y,470,530)*(1-s(y,700,760))
gold=(B[:,:,0]>B[:,:,2]) & (x>=985)
w=w*(~gold)
A=np.floor(w*255+.5).astype(np.uint32)
D=((B.astype(np.uint32)*(255-A[:,:,None])+R.astype(np.uint32)*A[:,:,None]+127)//255).astype(np.uint8)
Image.fromarray(A.astype('uint8')).save(d/'alpha.png')
Image.fromarray(((A>0)*255).astype('uint8')).save(d/'support-positive-mask.png')
Image.fromarray(D).save(d/'derived-context.png')
Image.fromarray(D[430:810]).save(d/'qa-repair-strip-native.png')
Image.fromarray(B[430:810]).save(d/'qa-before-strip-native.png')
assert np.array_equal(D[A==0],B[A==0]);assert np.array_equal(D[gold],B[gold])
source=Path(prep[1]['source']);assert sha(source)==prep[1]['sourceSha256']
tile=rgb(source);base=tile.copy();tile[493:1747,1433:2687]=D
Image.fromarray(tile).save(O/'candidate-right-only-native.png')
Image.fromarray(tile[900:1320,1370:2520]).save(O/'qa-right-join-native.png')
Image.fromarray(tile[864:1184,1024:2048]).save(O/'qa-internal-y1024-segment02-native.png')
Image.fromarray(tile[864:1184,2048:3072]).save(O/'qa-internal-y1024-segment03-native.png')
ys,xs=np.where(A>0)
manifest={'schemaVersion':1,'kind':'native_multi_source_alpha_derivation','tile':'r03_c04','repair':'roof-row-right',
 'status':'context_candidate_pending_final_view','formalAccepted':False,'contextTileBox':prep[1]['contextTileBox'],'contextWorldBox':prep[1]['contextWorldBox'],
 'base':ref(source),'baseContext':ref(d/'context-native.png'),'raw':ref(d/'raw-v1.png'),'receipt':ref(d/'receipt-v1.json'),
 'alphaFile':str(d/'alpha.png'),'alphaHash':sha(d/'alpha.png'),'supportPositiveMaskFile':str(d/'support-positive-mask.png'),'supportPositiveMaskHash':sha(d/'support-positive-mask.png'),
 'derivedFile':str(d/'derived-context.png'),'derivedHash':sha(d/'derived-context.png'),'width':1254,'height':1254,
 'alphaFormula':'s(x,0,64)*(1-s(x,1000,1020))*s(y,470,530)*(1-s(y,700,760)), set to zero wherever x>=985 AND baseRed>baseBlue to preserve the actual gold ornament. x,y are pixel centers.',
 'smoothstep':'s(v,a,b)=t*t*(3-2*t), t=clip((v-a)/(b-a),0,1)','alphaScale':255,'alphaQuantization':'floor(255*w+0.5)',
 'blendFormula':'per-channel (base*(255-alpha)+raw*alpha+127)//255',
 'positiveSupportContextBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
 'sameWorldCoordinateOnly':True,'resizedAfterGeneration':False,'finalArtUpscaled':False,'spatialBlur':False,
 'verifiedOutsideSupportUnchanged':True,'verifiedGoldPixelsUnchanged':True,
 'operation':'Copy this already-composited derived context only where support-positive-mask is nonzero. Do not apply alpha a second time. Or reconstruct from raw/base/alpha using the formula.',
 'limits':'Right section only. Left section remains unresolved and must not be replaced with rejected left trial.',
 'visualVerdict':'Initial native context inspection PASS; final left support edge still under review.'}
dump(d/'manifest.json',manifest)

left=O/'left';bad=rgb(left/'derived-context-v4.png');Image.fromarray(bad[450:850]).save(left/'qa-rejected-strip-native.png')
al=np.array(Image.open(left/'alpha-v4.png'));Image.fromarray(((al>0)*255).astype('uint8')).save(left/'support-positive-mask-v4.png')
failed={'status':'FAIL_DO_NOT_APPLY','contextTileBox':prep[0]['contextTileBox'],'contextWorldBox':prep[0]['contextWorldBox'],
 'attempts':4,'rawCandidates':[ref(left/f'raw-v{k}.png') for k in range(1,5)],'lastDerived':ref(left/'derived-context-v4.png'),
 'lastAlpha':ref(left/'alpha-v4.png'),'lastSupportPositiveMask':ref(left/'support-positive-mask-v4.png'),
 'evidence':ref(left/'qa-rejected-strip-native.png'),
 'finding':'All four left generations remove triangles but shift the original lower tile columns; restoring immutable outside pixels causes double gutters/blur-like alpha overlap near local y700..760. This is a geometric drift, not a tonal mismatch, so narrower alpha cannot truthfully fix it.',
 'actualViewPerformed':True,'furtherGenerationStopped':True,'reason':'Bounded four attempts and explicit no-endless-generation constraint.'}
dump(left/'failure-manifest.json',failed)
handoff={'status':'PARTIAL_RIGHT_CONTEXT_AVAILABLE_LEFT_BLOCKED','base':ref(source),'rightManifest':str(d/'manifest.json'),
 'leftFailureManifest':str(left/'failure-manifest.json'),'generationReceipts':receipts,
 'noSelectionOrProgressChanges':True,'noPatchLevelExports':True,'writesConfinedTo':str(O),
 'candidateForQA':ref(O/'candidate-right-only-native.png'),'qaRightJoin':ref(O/'qa-right-join-native.png'),
 'overallBandAccepted':False}
dump(O/'handoff.json',handoff)
print(json.dumps({'rightManifest':str(d/'manifest.json'),'rightDerivedHash':manifest['derivedHash'],'rightAlphaHash':manifest['alphaHash'],'handoff':str(O/'handoff.json')},ensure_ascii=False))
