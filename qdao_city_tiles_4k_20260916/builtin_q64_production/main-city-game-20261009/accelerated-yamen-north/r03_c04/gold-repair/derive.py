import json,sys,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]))
import pipeline as p
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(f,d):f.write_text(json.dumps(d,indent=2),encoding='utf-8')
def soft(v,w=16):
 t=np.clip(v/w,0,1);return t*t*(3-2*t)
for name,rect,width in [('diagonal-gold',[210,210,1140,1040],128),('finial-joint',[600,450,805,640],32)]:
 d=HERE/name;prep=json.loads((d/'preparation.json').read_text())
 old=np.array(Image.open(d/'context-native.png').convert('RGB'))
 new=np.array(Image.open(d/'raw-v1.png').convert('RGB'))
 assert old.shape==new.shape==(1254,1254,3)
 L,T,R,B=rect;yy,xx=np.indices((1254,1254))
 sxL=p.minimum_seam(old[:,L:L+width],new[:,L:L+width])+L
 sxR=p.minimum_seam(old[:,R-width:R],new[:,R-width:R])+R-width
 syT=p.minimum_seam(old[T:T+width].transpose(1,0,2),new[T:T+width].transpose(1,0,2))+T
 syB=p.minimum_seam(old[B-width:B].transpose(1,0,2),new[B-width:B].transpose(1,0,2))+B-width
 dist=np.minimum.reduce([xx-sxL[:,None],sxR[:,None]-xx,yy-syT[None,:],syB[None,:]-yy])
 alpha=np.rint(soft(dist,16)*255).astype(np.uint8)
 out=np.rint((old.astype(float)*(255-alpha[...,None])+new.astype(float)*alpha[...,None])/255).astype(np.uint8)
 Image.fromarray(alpha).save(d/'alpha-v1.png');Image.fromarray(out).save(d/'derived-v1.png')
 receipt=json.loads((d/'tool-result-v1.json').read_text())
 host=receipt['output_hint'].split(' as ',1)[1].split(' by default')[0]
 record={'id':name,**prep,'rawFile':str(d/'raw-v1.png'),'rawSHA256':sha(d/'raw-v1.png'),'rawNativePixels':[1254,1254],'rawHostSource':host,'actualModel':None,'actualQuality':None,'submittedParameters':json.loads((d/'parameters-v1.json').read_text()),'receipt':str(d/'tool-result-v1.json'),'derivedFile':str(d/'derived-v1.png'),'derivedSHA256':sha(d/'derived-v1.png'),'alphaFile':str(d/'alpha-v1.png'),'alphaSHA256':sha(d/'alpha-v1.png'),'maskFormula':'minimum-error boundary in four strips; 16px inward smoothstep alpha; exact same world coordinates; rounded weighted RGB sum','maskSearchRect':rect,'maskSearchWidth':width,'resizedAfterGeneration':False,'formalAccepted':False,'nativeToolOutput':False}
 write(d/'derivation-v1.json',record)
 print(json.dumps({'id':name,'derived':record['derivedFile'],'alphaPixels':int((alpha>0).sum())}))

