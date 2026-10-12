import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
H=ROOT/'finish-20261012';O=H/'micro-derived-v2';O.mkdir(exist_ok=True)
def s(v,l,r):
 t=np.clip((v-l)/(r-l),0,1);return t*t*(3-2*t)
y,x=np.indices((1254,1254))
def rect(l,t,r,b,f):
 return s(x,l,l+f)*(1-s(x,r-f,r))*s(y,t,t+f)*(1-s(y,b-f,b))
for tag in ['c05-wood-v1','c05-floor-v1','c05-plinth-v1','c05-green-band-v1','d4-color-splice-v1']:
 d=H/tag;base=np.array(Image.open(d/'edit-guide-native.png').convert('RGB'));gen=np.array(Image.open(d/'raw-native.png').convert('RGB'))
 if tag=='c05-wood-v1':w=np.maximum(rect(80,555,180,680,18),rect(420,565,495,680,14))
 elif tag=='c05-floor-v1':w=rect(540,575,670,660,18)
 elif tag=='c05-plinth-v1':
  w=rect(330,35,700,1254,90);w*=1-s(y,1005,1050)+s(y,1100,1155)
  w=np.maximum(w,rect(450,35,620,125,18))
 elif tag=='c05-green-band-v1':w=s(x,75,105)*s(y,1107,1134)*(1-s(y,1200,1228))
 else:w=rect(530,520,790,695,35)
 alpha=np.rint(w*255).astype('uint8')
 out=((base.astype('uint32')*(255-alpha[...,None])+gen.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
 p.save_png(O/(tag+'-derived.png'),Image.fromarray(out));p.save_png(O/(tag+'-alpha.png'),Image.fromarray(alpha))
 p.put_json(O/(tag+'-derivation.json'),{'coordinates':p.read(d/'preparation.json'),'base':p.reference(d/'edit-guide-native.png','native base guide'),'source':p.reference(d/'raw-native.png','builtin actual edit'),'alpha':p.reference(O/(tag+'-alpha.png'),'recorded native material alpha'),'formula':'(base*(255-alpha)+source*alpha+127)//255','recipe':str(Path(__file__).resolve()),'resampled':False,'spatialBlur':False,'formalAccepted':False})
 boxes={'c05-wood-v1':[(65,550,210,690),(405,550,520,690)],'c05-floor-v1':[(520,560,690,680)],'c05-plinth-v1':[(290,10,780,270),(290,400,780,650),(290,1000,780,1254)],'c05-green-band-v1':[(0,1050,1254,1254)],'d4-color-splice-v1':[(490,490,850,725)]}[tag]
 for i,box in enumerate(boxes,1):p.save_png(O/(tag+f'-qa-{i}.png'),Image.fromarray(out).crop(box))
print(O)

