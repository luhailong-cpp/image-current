from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parent.parent;O=D/'lower-v2'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(O/'joint-assembly.json');sr={s['jointSourceId']:s for s in m['sources']};arrays={s:np.asarray(Image.open(q['file']).convert('RGB')) for s,q in sr.items()}
checks=[];total=0
for out in m['artifacts']:
 p=Path(out['file']);assert sha(p)==out['sha256'];assert sha(out['sourceIdMap']['file'])==out['sourceIdMap']['sha256']
 im=np.asarray(Image.open(p).convert('RGB'));ids=np.asarray(Image.open(out['sourceIdMap']['file']));bx,by,xx,yy=out['globalBox']
 assert im.shape==(yy-by,xx-bx,3) and ids.shape==im.shape[:2] and (ids>0).all()
 counts=[]
 for sid in np.unique(ids):
  y,x=np.nonzero(ids==sid);s=sr[int(sid)];bb=s['globalNativeBox'];sx=x+bx-bb[0];sy=y+by-bb[1]
  assert ((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254)).all();assert np.array_equal(im[y,x],arrays[sid][sy,sx]);counts.append({'sourceId':int(sid),'pixels':len(x)})
 total+=ids.size;checks.append({'file':str(p),'pixels':ids.size,'sourceCount':len(counts),'sourceCounts':counts,'mismatchedPixels':0})
assert total==37748736
base=read(R/'work-r04_c04/tiles/r04_c04.repair-v2.assembly.json')
oldids=np.asarray(Image.open(base['sourceIdMap']));newids=np.asarray(Image.open(O/'r04_c04.source-id.png'));old=np.asarray(Image.open(base['candidate']));new=np.asarray(Image.open(O/'r04_c04.joint-proposal.png'))
sel=oldids==17;changed=np.any(old!=new,axis=2)&sel
ys,xs=np.nonzero(changed)
support={'originalSource17PixelCount':int(sel.sum()),'changedPixelCount':int(changed.sum()),'changedBBoxGlobal':[int(xs.min()+12288),int(ys.min()+12288),int(xs.max()+12289),int(ys.max()+12289)] if len(xs) else None,'corePreserved':m['supportBridgeCorePreserved'],'note':'Original support bridge core protected; only overlap-halo ownership can differ under shared blue-corner bridge.'}
jn=R/'work-r04_c03/joint-north/r04_c03.joint-proposal.png';assert np.array_equal(np.asarray(Image.open(O/'r04_c03.joint-proposal.png'))[:115],np.asarray(Image.open(jn))[:115])
result={'status':'pass-native-pixel-provenance','declaredFinalPixelsVerified':total,'mismatchedPixels':0,'uncoveredFinalPixels':0,'resampledPixels':0,'blendedPixels':0,'guidePixelsInFinal':0,'outputChecks':checks,'supportBridge':support,'jointNorth115ExactlyPreserved':True,'sourceRegistrySha256':sha(O/'joint-assembly.json'),'actualModelAndQualityUnconfirmed':True}
(O/'mechanical-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'proofSha256':sha(O/'mechanical-check.json'),'verified':total,'support':support}))

