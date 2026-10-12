import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';O=H/'lower-merged-v3';O.mkdir(exist_ok=True);S=H/'lower-merged-v1'
def s(v,l,r):
 t=np.clip((v-l)/(r-l),0,1);return t*t*(3-2*t)
base=np.array(Image.open(S/'d4-derived.png').convert('RGB'));fa=H/'d4-left-return-v1/raw-native.png';fb=H/'d4-right-return-v1/raw-native.png';a,b=[np.array(Image.open(f).convert('RGB')) for f in (fa,fb)]
gen=base.copy();gen[:,:1254]=a;gen[:,1147:]=b
path=p.minimum_seam(a[590:765,1147:],b[590:765,:107]);path=np.pad(path,(590,489),mode='edge');sid=np.ones((1254,2401),np.uint8);sid[:,1147:]=2
for row in range(1254):
 k=1147+path[row];gen[row,1147:k]=a[row,1147:k];sid[row,1147:k]=1
weights=np.zeros((1254,107),np.uint8)
for row in range(1254):
 weight=np.rint(s(np.arange(107),path[row]-6,path[row]+6)*255).astype('uint8');weights[row]=weight
 gen[row,1147:1254]=((a[row,1147:].astype('uint32')*(255-weight[:,None])+b[row,:107].astype('uint32')*weight[:,None]+127)//255).astype('uint8')
p.save_png(O/'d4-source2-overlap-weight.png',Image.fromarray(weights))
y,x=np.indices((1254,2401));w=s(y,540,570)*(1-s(y,748,780))*s(x,160,220)
protected=(base[:,:,0]>base[:,:,2]*1.28)&(base[:,:,0]>75);w[protected]=0
alpha=np.rint(w*255).astype('uint8');d=((base.astype('uint32')*(255-alpha[...,None])+gen.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
p.save_png(O/'d4-derived.png',Image.fromarray(d));p.save_png(O/'d4-alpha.png',Image.fromarray(alpha));p.save_png(O/'d4-source-index.png',Image.fromarray(sid))
support=(np.array(Image.open(S/'d4-alpha.png'))>0)|(alpha>0);p.save_png(O/'d4-support.png',Image.fromarray(support.astype('uint8')*255))
p.put_json(O/'d4-derivation.json',{'tileBox':[1695,2380,4096,3634],'firstStage':{'file':str(S/'d4-derivation.json'),'sha256':p.sha(S/'d4-derivation.json')},'base':p.reference(S/'d4-derived.png','first-stage derived'),'sources':[p.reference(fa,'return source1'),p.reference(fb,'return source2')],'sourceSeamPath':path.tolist(),'sourceIndex':p.reference(O/'d4-source-index.png','same-coordinate source IDs'),'alpha':p.reference(O/'d4-alpha.png','recorded return material alpha'),'support':p.reference(O/'d4-support.png','union support'),'formula':'(base*(255-alpha)+gen*alpha+127)//255; native y585..615 top fade,748..780 bottom fade; x160..220 left fade; gold protected','resampled':False,'spatialBlur':False})
for i,(l,r) in enumerate([(100,900),(850,1650),(1600,2401)],1):p.save_png(O/f'd4-qa-{i}.png',Image.fromarray(d).crop((l,485,r,825)))
src=H/'d5-gold-joint-v1';base=np.array(Image.open(src/'edit-guide-native.png').convert('RGB'));gen=np.array(Image.open(src/'raw-native.png').convert('RGB'));y,x=np.indices((1254,1254))
w=s(x,550,595)*(1-s(x,1050,1100))*s(y,300,345)*(1-s(y,645,690))
alpha=np.rint(w*255).astype('uint8');d=((base.astype('uint32')*(255-alpha[...,None])+gen.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
p.save_png(O/'d5-derived.png',Image.fromarray(d));p.save_png(O/'d5-alpha.png',Image.fromarray(alpha))
p.put_json(O/'d5-derivation.json',{'tileBox':[400,2550,1654,3804],'base':p.reference(src/'edit-guide-native.png','native baseline'),'source':p.reference(src/'raw-native.png','builtin native gold joint edit'),'alpha':p.reference(O/'d5-alpha.png','recorded native material alpha'),'formula':'native rect [550,300,1100,690] smoothstep outer45..50px;(base*(255-alpha)+generated*alpha+127)//255','resampled':False,'spatialBlur':False})
p.save_png(O/'d5-qa.png',Image.fromarray(d).crop((500,280,1150,740)))
print(O)

