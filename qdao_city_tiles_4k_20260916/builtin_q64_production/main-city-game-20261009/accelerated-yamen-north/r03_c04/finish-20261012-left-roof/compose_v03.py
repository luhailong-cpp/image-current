from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;V=O/'v03'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prep=json.loads((V/'preparation.json').read_text())
B=np.array(Image.open(V/'context-native.png').convert('RGB'));R=np.array(Image.open(V/'raw-native.png').convert('RGB'))
assert B.shape==R.shape==(1254,1254,3)
x=np.arange(1254)[None,:]+.5;y=np.arange(1254)[:,None]+.5
def s(z,a,b):
 z=np.clip((z-a)/(b-a),0,1);return z*z*(3-2*z)
w=np.zeros((1254,1254),dtype='float64')
for l,t,r,b in prep['repairSubBoxes']:
 w=np.maximum(w,s(x,l,l+8)*(1-s(x,r-8,r))*s(y,t,t+8)*(1-s(y,b-8,b)))
A=np.floor(255*w+.5).astype('uint32')
D=((B.astype('uint32')*(255-A[:,:,None])+R.astype('uint32')*A[:,:,None]+127)//255).astype('uint8')
assert np.array_equal(B[A==0],D[A==0])
Image.fromarray(A.astype('uint8')).save(V/'alpha.png');Image.fromarray(((A>0)*255).astype('uint8')).save(V/'support.png');Image.fromarray(D).save(V/'derived-context.png')
for label,bb in [('all',[70,455,885,785]),('roi1',[90,475,530,785]),('roi2',[410,475,875,785]),('joint1',[315,578,470,727]),('joint2',[455,515,855,715])]:
 Image.fromarray(D).crop(bb).save(V/(label+'-derived-qa.png'))
 Image.fromarray(R).crop(bb).save(V/(label+'-raw-qa.png'))
orig=np.array(Image.open(O/'v01/context-native.png').convert('RGB'))
A2=np.array(Image.open(O/'v02/alpha.png'))
support=np.maximum(A2>0,A>0)
assert np.array_equal(orig[~support],D[~support])
Image.fromarray((support*255).astype('uint8')).save(V/'combined-support.png')
weights=np.stack([(1-A2/255)*(1-A/255),(A2/255)*(1-A/255),A/255],axis=2)
np.savez_compressed(V/'source-weights.npz',base=weights[:,:,0],v02=weights[:,:,1],v03=weights[:,:,2],alpha_v02=A2,alpha_v03=A.astype('uint8'))
(V/'derivation-pending.json').write_text(json.dumps({'nativePixels':[1254,1254],'contextTileBox':prep['contextTileBox'],'contextWorldBox':prep['contextWorldBox'],'rawSha256':sha(V/'raw-native.png'),'derivedSha256':sha(V/'derived-context.png'),'combinedSupportSha256':sha(V/'combined-support.png'),'weightsSha256':sha(V/'source-weights.npz'),'outsideCombinedSupportByteIdenticalToOriginalBase':True,'changedPixels':int(np.any(D!=orig,axis=2).sum()),'visualVerdict':'PENDING','resampled':False,'alpha':'8px smoothstep per hole; exact compose_v03.py','formula':'D2=roundRGB(base*(1-A2)+v02raw*A2); D3=roundRGB(D2*(1-A3)+v03raw*A3); integer round=(x+127)//255','actualModel':None,'actualQuality':None},indent=2),encoding='utf-8')
print('Saved multi-source derived context, support, weights, and native QA.')
