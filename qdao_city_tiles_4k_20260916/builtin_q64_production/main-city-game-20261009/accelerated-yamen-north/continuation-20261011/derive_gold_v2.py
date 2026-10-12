import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
d=Path(__file__).resolve().parent/'gold-joint01';a=np.array(Image.open(d/'context-native.png').convert('RGB'));b=np.array(Image.open(d/'raw-v1.png').convert('RGB'));y,x=np.indices((1254,1254))
def s(v,a,b):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
alpha=np.rint(255*s(x,718,724)*(1-s(x,778,784))*s(y,93,99)*(1-s(y,198,204))).astype('uint8')
out=((a.astype('uint32')*(255-alpha[...,None])+b.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
p.save_png(d/'alpha-v2.png',Image.fromarray(alpha));p.save_png(d/'support-v2.png',Image.fromarray((alpha>0).astype('uint8')*255));p.save_png(d/'derived-context-v2.png',Image.fromarray(out));p.save_png(d/'qa-native-v2.png',Image.fromarray(out).crop((610,0,980,330)))
p.put_json(d/'derivation-v2.json',{'base':p.reference(d/'context-native.png','native context'),'raw':p.reference(d/'raw-v1.png','generated gold joint'),'alpha':p.reference(d/'alpha-v2.png','native-coordinate alpha'),'formula':'255*s(x,718,724)*(1-s(x,778,784))*s(y,93,99)*(1-s(y,198,204))','tileBox':[400,2842,1654,4096],'resized':False,'spatialBlur':False,'formalAccepted':False})

