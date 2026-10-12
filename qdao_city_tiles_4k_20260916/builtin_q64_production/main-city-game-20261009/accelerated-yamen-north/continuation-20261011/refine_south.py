import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=ROOT/'continuation-20261011';OLD=HERE/'merged-south-v1';OUT=HERE/'merged-south-v2';OUT.mkdir(exist_ok=True)
d=p.read(OLD/'strip-derivation.json');base=np.array(Image.open(d['base']['file']).convert('RGB'));src=np.array(Image.open(OLD/'source-index.png'));old=np.array(Image.open(OLD/'derived-strip-native.png').convert('RGB'))
gen=old.copy()
for rec in d['sources']:
 L=rec['contextStripBox'][0];a=np.array(Image.open(rec['file']).convert('RGB'));idx=rec['index'];mask=src[:,L:L+1254]==idx;gen[:,L:L+1254][mask]=a[mask]
# Rebuild raw source field below the old bottom path using the last source ID above it.
for x in range(4096):
 sid=int(src[1000,x]);r=d['sources'][sid-1];a=np.array(Image.open(r['file']).convert('RGB')) if x==0 or sid!=previous_sid else a
 gen[1000:,x]=a[1000:,x-r['contextStripBox'][0]];previous_sid=sid
yy,xx=np.indices((1254,4096));bottom=np.array(d['bottomSeamPath']);top=np.array(d['topSeamPath']);t=np.clip((yy-(bottom[None,:]-64))/128,0,1);w=1-t*t*(3-2*t);w[yy<top[None,:]]=0
# Preserve edge sharpness: use binary selection near strong native gradients.
def edge(a):
 a=a.astype(float);gx=np.max(np.abs(a[:,2:]-a[:,:-2]),2);gy=np.max(np.abs(a[2:]-a[:-2]),2);z=np.zeros(a.shape[:2]);z[:,1:-1]=gx;z[1:-1]=np.maximum(z[1:-1],gy);return z
strong=np.maximum(edge(base),edge(gen))>65
for dy in range(-2,3):
 for dx in range(-2,3):strong|=np.roll(np.roll(strong,dy,0),dx,1)
w[strong]=(yy<bottom[None,:])[strong];w[yy<top[None,:]]=0
alpha=np.rint(w*255).astype('uint8');final=((base.astype('uint32')*(255-alpha[...,None])+gen.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
# Apply recorded generated timber seam repair only in its native ROI.
context=np.array(Image.open(HERE/'bottom-return01/context-native.png').convert('RGB'));new=np.array(Image.open(HERE/'bottom-return01/raw-v1.png').convert('RGB'));y,x=np.indices((1254,1254))
def s(v,a,b):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
rw=s(x,85,110)*(1-s(x,390,403))*s(y,400,490)*(1-s(y,710,805));ra=np.rint(rw*255).astype('uint8')
repair=((context.astype('uint32')*(255-ra[...,None])+new.astype('uint32')*ra[...,None]+127)//255).astype('uint8')
# Context origin strip y=513; only its rows through740 lie inside the1254 strip.
mask=ra[:741]>0;final[513:,:1254][mask]=repair[:741][mask]
p.save_png(OUT/'derived-strip-native.png',Image.fromarray(final));p.save_png(OUT/'material-alpha.png',Image.fromarray(alpha));p.save_png(OUT/'timber-repair-alpha.png',Image.fromarray(ra));p.save_png(OUT/'timber-derived-context.png',Image.fromarray(repair))
p.put_json(OUT/'derivation.json',{'baseDerivation':str(OLD/'strip-derivation.json'),'baseDerivationSHA256':p.sha(OLD/'strip-derivation.json'),'materialAlpha':str(OUT/'material-alpha.png'),'alphaSHA256':p.sha(OUT/'material-alpha.png'),'formula':'round weighted RGB at exact coordinates,128px smoothstep at bottom return; strong gradients protected by binary source choice','timberRaw':str(HERE/'bottom-return01/raw-v1.png'),'timberRawSHA256':p.sha(HERE/'bottom-return01/raw-v1.png'),'timberAlpha':str(OUT/'timber-repair-alpha.png'),'timberAlphaFormula':'255*s(x,85,110)*(1-s(x,390,403))*s(y,400,490)*(1-s(y,710,805))','resampled':False,'spatialBlur':False,'formalAccepted':False})
for row in [912,1140]:
 for i in range(4):p.save_png(OUT/f'qa-y{row}-segment{i+1:02d}.png',Image.fromarray(final[max(0,row-110):min(1254,row+110),i*1024:(i+1)*1024]))
p.save_png(OUT/'qa-timber-native.png',Image.fromarray(repair).crop((50,350,445,870)))
print(OUT)
