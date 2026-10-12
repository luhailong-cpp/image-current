from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
O=Path(__file__).resolve().parent
V=O/sys.argv[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prep=json.loads((V/'preparation.json').read_text())
B=np.array(Image.open(V/'context-native.png').convert('RGB'));R=np.array(Image.open(V/'raw-native.png').convert('RGB'))
assert B.shape==R.shape==(1254,1254,3)
l,t,r,b=prep['repairContextBox']
x=np.arange(1254)[None,:]+.5;y=np.arange(1254)[:,None]+.5
def s(z,a,b):
 z=np.clip((z-a)/(b-a),0,1);return z*z*(3-2*z)
A=np.floor(255*s(x,l,l+8)*(1-s(x,r-8,r))*s(y,t,t+8)*(1-s(y,b-8,b))+.5).astype('uint32')
D=((B.astype('uint32')*(255-A[:,:,None])+R.astype('uint32')*A[:,:,None]+127)//255).astype('uint8')
assert np.array_equal(B[A==0],D[A==0])
Image.fromarray(A.astype('uint8')).save(V/'alpha.png')
Image.fromarray(((A>0)*255).astype('uint8')).save(V/'support.png')
Image.fromarray(D).save(V/'derived-context.png')
bb=[max(l-60,0),max(t-60,0),min(r+60,1254),min(b+60,1254)]
Image.fromarray(B).crop(bb).save(V/'before-local-qa.png')
Image.fromarray(R).crop(bb).save(V/'raw-local-qa.png')
Image.fromarray(D).crop(bb).save(V/'derived-local-qa.png')
info={'pixels':[1254,1254],'rawSha256':sha(V/'raw-native.png'),'contextSha256':sha(V/'context-native.png'),'derivedSha256':sha(V/'derived-context.png'),'supportSha256':sha(V/'support.png'),'alphaSha256':sha(V/'alpha.png'),'positiveSupportContextBox':[l,t,r,b],'localQACropBox':bb,'formula':'(base*(255-alpha)+raw*alpha+127)//255 per channel','alpha':'8px smoothstep inner edge; see compose_trial.py','changedPixels':int(np.any(D!=B,axis=2).sum()),'outsideSupportUnchanged':True,'resampled':False,'actualModel':None,'actualQuality':None,'visualVerdict':'PENDING'}
(V/'derivation-pending.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
print(json.dumps(info))
