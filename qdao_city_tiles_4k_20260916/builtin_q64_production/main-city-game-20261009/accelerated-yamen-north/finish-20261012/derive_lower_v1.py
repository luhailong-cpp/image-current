import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';O=H/'lower-merged-v1';O.mkdir(exist_ok=True)
def s(v,l,r):
 t=np.clip((v-l)/(r-l),0,1);return t*t*(3-2*t)
def blend(tag,base,gen,w,record):
 alpha=np.rint(w*255).astype('uint8')
 d=((base.astype('uint32')*(255-alpha[...,None])+gen.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
 p.save_png(O/(tag+'-derived.png'),Image.fromarray(d));p.save_png(O/(tag+'-alpha.png'),Image.fromarray(alpha))
 p.put_json(O/(tag+'-derivation.json'),dict(record,alpha=p.reference(O/(tag+'-alpha.png'),'recorded same-coordinate material alpha'),formula='(base*(255-alpha)+generated*alpha+127)//255',resampled=False,spatialBlur=False))
 return d,alpha
basefile=ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-945fa7bcbb42.png'
full=np.array(Image.open(basefile).convert('RGB'))
base=full[2380:3634,1695:4096].copy()
fa=H/'d4-left-v1/raw-native.png';fb=H/'d4-right-v1/raw-native.png';a,b=[np.array(Image.open(f).convert('RGB')) for f in (fa,fb)]
gen=base.copy();gen[:,:1254]=a;gen[:,1147:]=b
path=p.minimum_seam(a[510:680,1147:],b[510:680,:107]);path=np.pad(path,(510,574),mode='edge')
sid=np.ones((1254,2401),np.uint8);sid[:,1147:]=2
for y in range(1254):
 k=1147+path[y];gen[y,1147:k]=a[y,1147:k];sid[y,1147:k]=1
y,x=np.indices(base.shape[:2]);w=s(y,520,552)*(1-s(y,650,684))*s(x,160,220)
gold=(base[:,:,0]>base[:,:,2]*1.28)&(base[:,:,0]>75);w[gold]=0
d,am=blend('d4',base,gen,w,{'base':p.reference(basefile,'native original'),'tileBox':[1695,2380,4096,3634],'sources':[p.reference(fa,'source1 origin1695'),p.reference(fb,'source2 origin2842')],'sourceSeamPath':path.tolist(),'alphaFormula':'native y520..552 top fade,650..684 bottom fade; x160..220 left fade; gold protected'})
p.save_png(O/'d4-source-index.png',Image.fromarray(sid))
for i,(l,r) in enumerate([(100,900),(850,1650),(1600,2401)],1):p.save_png(O/f'd4-qa-{i}.png',Image.fromarray(d).crop((l,485,r,720)))
for tag,region,fade in [('d5-gold-joint-v1',[660,365,880,545],22),('e1-west-v1',[490,0,770,1254],40),('e2-west-v1',[470,0,795,1120],30)]:
 src=H/tag;base=np.array(Image.open(src/'edit-guide-native.png').convert('RGB'));gen=np.array(Image.open(src/'raw-native.png').convert('RGB'))
 y,x=np.indices((1254,1254));l,t,r,bo=region
 w=s(x,l,l+fade)*(1-s(x,r-fade,r))
 if tag.startswith('d5'):w*=s(y,t,t+fade)*(1-s(y,bo-fade,bo))
 elif tag.startswith('e1'):w*=s(y,0,45)*(1-s(y,1210,1254))
 else:w*=s(y,0,40)*(1-s(y,1080,1120))
 d,am=blend(tag,base,gen,w,{'base':p.reference(src/'edit-guide-native.png','native guide'),'source':p.reference(src/'raw-native.png','builtin native edit'),'region':region,'fade':fade,'coordinates':p.read(src/'preparation.json')})
 boxes=([570,300,975,640],) if tag.startswith('d5') else ([420,0,850,410],[420,400,850,800],[420,790,850,1254])
 for i,box in enumerate(boxes,1):p.save_png(O/(tag+f'-qa-{i}.png'),Image.fromarray(d).crop(tuple(box)))
print(O)

