import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=ROOT/'finish-20261012';OUT=HERE/'d1-merged-v1';OUT.mkdir(exist_ok=True)
basefile=ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png';base=np.array(Image.open(basefile).convert('RGB'))[430:1684,:2354]
files=[HERE/'d1-left-v1/raw-native.png',HERE/'d1-right-v1/raw-native.png'];a,b=[np.array(Image.open(f).convert('RGB')) for f in files]
gen=base.copy();gen[:,:1254]=a;gen[:,1100:]=b;sid=np.ones((1254,2354),np.uint8);sid[:,1100:]=2
path=p.minimum_seam(a[240:870,1100:],b[240:870,:154]);path=np.pad(path,(240,384),mode='edge')
for row in range(1254):
 k=1100+path[row];gen[row,1100:k]=a[row,1100:k];sid[row,1100:k]=1
top=p.minimum_seam(base[215:280].transpose(1,0,2),gen[215:280].transpose(1,0,2))+215
bottom=p.minimum_seam(base[850:935].transpose(1,0,2),gen[850:935].transpose(1,0,2))+850
y,x=np.indices((1254,2354))
def s(v,a,b):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
w=s(y,top[None,:]-16,top[None,:]+16)*(1-s(y,bottom[None,:]-16,bottom[None,:]+16))
# Keep formal west-edge pixels fixed while previewing the central repair.
w*=s(x,0,90)*(1-s(x,2180,2260))
# Existing gold and wood structures are protected at identical native coordinates.
protected=(base[:,:,0]>base[:,:,2]*1.28)&(base[:,:,0]>75)
w[protected]=0
alpha=np.rint(w*255).astype('uint8');derived=((base.astype('uint32')*(255-alpha[...,None])+gen.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
p.save_png(OUT/'derived-strip.png',Image.fromarray(derived));p.save_png(OUT/'alpha.png',Image.fromarray(alpha));p.save_png(OUT/'source-index.png',Image.fromarray(sid))
p.put_json(OUT/'derivation.json',{'base':{'file':str(basefile),'sha256':p.sha(basefile)},'tileBox':[0,430,2354,1684],'sources':[p.reference(f,'generated source1' if i==0 else 'generated source2,originx1100') for i,f in enumerate(files)],'sourceIndex':p.reference(OUT/'source-index.png','same-coordinate source ID'),'alpha':p.reference(OUT/'alpha.png','recorded material alpha'),'topPath':top.tolist(),'bottomPath':bottom.tolist(),'leftPath':path.tolist(),'blendFormula':'(base*(255-alpha)+gen*alpha+127)//255','alphaFormula':'32px smoothstep native return, x0..90 ramp and x2180..2260 ramp; original gold/wood pixels protected','resampled':False,'spatialBlur':False,'formalAccepted':False})
for i,(l,r) in enumerate([(0,800),(750,1550),(1500,2354)],1):
 for tag,t,bo in [('middle',345,650),('top',160,370),('bottom',800,995)]:
  p.save_png(OUT/f'qa-{tag}-{i}.png',Image.fromarray(derived).crop((l,t,r,bo)))
p.save_png(OUT/'qa-source-join.png',Image.fromarray(derived).crop((1000,270,1370,1000)))
print(OUT)

