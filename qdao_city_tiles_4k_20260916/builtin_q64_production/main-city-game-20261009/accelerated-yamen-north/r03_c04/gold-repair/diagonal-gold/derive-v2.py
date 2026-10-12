import json,sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parents[2]));import pipeline as p
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
old=np.array(Image.open(D/'derived-v1.png').convert('RGB'));new=np.array(Image.open(D/'raw-v2.png').convert('RGB'))
assert new.shape==(1254,1254,3)
L,T,R,B,W=125,530,420,855,64
yy,xx=np.indices((1254,1254))
xl=p.minimum_seam(old[:,L:L+W],new[:,L:L+W])+L;xr=p.minimum_seam(old[:,R-W:R],new[:,R-W:R])+R-W
yt=p.minimum_seam(old[T:T+W].transpose(1,0,2),new[T:T+W].transpose(1,0,2))+T
yb=p.minimum_seam(old[B-W:B].transpose(1,0,2),new[B-W:B].transpose(1,0,2))+B-W
dist=np.minimum.reduce([xx-xl[:,None],xr[:,None]-xx,yy-yt[None,:],yb[None,:]-yy])
t=np.clip(dist/16,0,1);alpha=np.rint(t*t*(3-2*t)*255).astype(np.uint8)
out=np.rint((old.astype(float)*(255-alpha[...,None])+new.astype(float)*alpha[...,None])/255).astype(np.uint8)
Image.fromarray(alpha).save(D/'alpha-v2.png');Image.fromarray(out).save(D/'derived-v2.png')
combined=np.maximum(np.array(Image.open(D/'alpha-v1.png')),alpha)
Image.fromarray(combined).save(D/'support-v2.png')
record={'id':'diagonal-gold-v2','contextTileBox':[1653,1421,2907,2675],'contextWorldBox':[13941,9613,15195,10867],'baseFile':str(D/'derived-v1.png'),'baseSha256':sha(D/'derived-v1.png'),'baseDerivation':str(D/'derivation-v1.json'),'rawFile':str(D/'raw-v2.png'),'rawSha256':sha(D/'raw-v2.png'),'rawNativePixels':[1254,1254],'alphaFile':str(D/'alpha-v2.png'),'alphaSha256':sha(D/'alpha-v2.png'),'derivedFile':str(D/'derived-v2.png'),'derivedSha256':sha(D/'derived-v2.png'),'supportFile':str(D/'support-v2.png'),'supportMeaning':'union of positive alpha support from the two recorded sequential composites; copy derived bytes where support>0, do not apply alpha again','submittedParameters':json.loads((D/'parameters-v2.json').read_text()),'receipt':str(D/'tool-result-v2.json'),'actualModel':None,'actualQuality':None,'resizedAfterGeneration':False,'nativeToolOutput':False,'formalAccepted':False,'maskFormula':'Minimum-error boundary in rectangle125,530,420,855 four64px strips;16px inward smoothstep'}
(D/'derivation-v2.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
Image.fromarray(out).crop((100,500,500,880)).save(D/'qa-small-v2.png')

