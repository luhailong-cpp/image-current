from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent
SW=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southwest")
SOURCE=Path(r"C:\Users\luyua\.codex\generated_images\01a12568-32a5-7300-bfbe-f5de662c1aa1\exec-f1f82212-dc37-4092-8d66-470b2992b954.png")
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def jsave(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def saveim(name,a):
 p=D/'qa'/name;Image.fromarray(a).save(p,optimize=True)
 return {'path':str(p),'sha256':sha(p),'pixels':[a.shape[1],a.shape[0]]}
req=json.loads((D/'request.json').read_text(encoding='utf-8'))
for ref in req['references']: assert sha(ref['path'])==ref['sha256']
assert sha(req['promptPath'])==req['promptSha256']
native=D/'native/p04_02-joint-v1.png'
assert sha(native)==sha(SOURCE)
im=Image.open(native);assert im.size==(1254,1254)
A=np.array(Image.open(req['references'][0]['path']).convert('RGB'))
B=np.array(im.convert('RGB'))
delta=np.any(A!=B,axis=2)
edgecounts={'north':int(delta[:230].sum()),'south':int(delta[-230:].sum()),'west':int(delta[:,:230].sum()),'east':int(delta[:,-230:].sum())}
align=[]
for x in [0,100,200,230,250,280,300,350]:
 a=int(800+np.argmin(A[800:1200,x].mean(1)))
 b=int(800+np.argmin(B[800:1200,x].mean(1)))
 align.append({'x':x,'originalJointDarkestY':a,'generatedJointDarkestY':b,'generatedMinusOriginalY':b-a})
record={'id':req['id'],'status':'native-generated-rejected-for-compositing','file':str(native),'sha256':sha(native),'sourceOutput':str(SOURCE),'sourceOutputSha256':sha(SOURCE),'width':im.width,'height':im.height,'mode':im.mode,'format':im.format,'nativePixelsPreserved':True,'resizedAfterGeneration':False,'tool':'image_gen.imagegen','route':'builtin','apiUsed':False,'actualModel':None,'actualQuality':None,'prompt':req['promptPath'],'promptSha256':req['promptSha256'],'references':req['references'],'request':str(D/'request.json'),'requestSha256':sha(D/'request.json'),'receipt':str(D/'receipts/p04_02-joint-v1.receipt.json'),'receiptSha256':sha(D/'receipts/p04_02-joint-v1.receipt.json'),'generatedAtUtc':datetime.now(timezone.utc).isoformat()}
jsave(D/'native/p04_02-joint-v1.png.generation.json',record)
# A diagnostic hard bounded crop demonstrates why this source cannot be accepted.
# It is never listed as a usable patch or production candidate.
box=[240,460,890,1014];x0,y0,x1,y1=box
test=A.copy();test[y0:y1,x0:x1]=B[y0:y1,x0:x1]
qa={
 'incomingBefore':saveim('incoming-before.png',A[820:1040,220:460]),
 'incomingGenerated':saveim('incoming-generated.png',B[820:1040,220:460]),
 'lockedBoundaryDiagnostic':saveim('rejected-bounded-composite-diagnostic.png',test),
 'localComparison':saveim('incoming-before-generated-side-by-side.png',np.concatenate([A[820:1040,200:460],B[820:1040,200:460]],axis=1)),
 'junctionGenerated':saveim('junction-generated.png',B[450:640,680:900])
}
review={'status':'REJECT','formalAccepted':False,'recommendedForUse':False,'reason':'Generated continuation forms a complete T-junction, but the preexisting incoming groove was displaced upward by about 39 px. Preserving the original four outer 230 px then inserting this output causes a geometric discontinuity. No usable repair patch is supplied.','originalSourceUnchanged':True,'originalSourceSha256':sha(req['references'][0]['path']),'generatedOuter230ChangedPixels':edgecounts,'incomingJointEvidence':align,'diagnosticNativeBox':box,'diagnosticIsNotUsablePatch':True,'nativeFullContextOrigin':[1024,3072],'nativeWorldOrigin':[17293,43917],'nativeTileCoreOrigin':[909,2957],'images':qa,'generationAttempts':1,'generationSuccesses':1,'toolErrors':0,'modelQualityActualNull':True,'quotaError':None,'nextAction':'Requires a further separately authorized imagegen attempt retaining the exact existing incoming groove; do not merge this output.','reviewedAtUtc':datetime.now(timezone.utc).isoformat()}
jsave(D/'qa/final-review.json',review)
result={'status':'attempt-complete-no-usable-repair','formalAccepted':False,'newNative':record,'review':str(D/'qa/final-review.json'),'reviewSha256':sha(D/'qa/final-review.json'),'writesLimitedTo':str(D),'nativeSelectionRecordsProgressModified':False,'r10Modified':False,'usablePatch':None,'generationAttempts':1,'generationSuccesses':1,'toolErrors':0,'actualModel':None,'actualQuality':None,'script':str(Path(__file__)),'scriptSha256':sha(Path(__file__))}
jsave(D/'production-result.json',result)
print(json.dumps({'status':result['status'],'native':record['file'],'sha256':record['sha256'],'changedOuterEdges':edgecounts,'jointAlignment':align,'review':result['review']},indent=2))

