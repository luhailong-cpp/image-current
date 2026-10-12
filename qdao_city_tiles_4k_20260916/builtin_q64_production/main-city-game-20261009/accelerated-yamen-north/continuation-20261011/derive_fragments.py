import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
HERE=Path(__file__).resolve().parent;base=ROOT/'r03_c05/candidate/r03_c05-pipeline-fixed-native-contexts-e28885c9de32.png';full=np.array(Image.open(base).convert('RGB'));contexts=[]
specs=[('roof-fragments01',[300,1440,1554,2694],[(600,558,860,735,14),(900,665,1165,817,14)]),('roof-fragments02',[1200,1440,2454,2694],[(145,598,452,738,14),(455,598,715,738,14),(720,573,906,715,14),(855,465,986,605,10)])]
y,x=np.indices((1254,1254))
def s(v,a,b):
 t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
for name,box,rects in specs:
 d=HERE/name;L,T,R,B=box;a=full[T:B,L:R].copy();b=np.array(Image.open(d/'raw-v1.png').convert('RGB'));w=np.zeros((1254,1254))
 for l,t,r,bo,f in rects:w=np.maximum(w,s(x,l,l+f)*(1-s(x,r-f,r))*s(y,t,t+f)*(1-s(y,bo-f,bo)))
 alpha=np.rint(255*w).astype('uint8');o=((a.astype('uint32')*(255-alpha[...,None])+b.astype('uint32')*alpha[...,None]+127)//255).astype('uint8');full[T:B,L:R]=o
 p.save_png(d/'current-base-context.png',Image.fromarray(a));p.save_png(d/'alpha.png',Image.fromarray(alpha));p.save_png(d/'support.png',Image.fromarray((alpha>0).astype('uint8')*255));p.save_png(d/'derived-context.png',Image.fromarray(o));p.save_png(d/'qa-native.png',Image.fromarray(o).crop((500 if name.endswith('01') else 100,440,1254 if name.endswith('01') else 1060,840)))
 p.put_json(d/'derivation.json',{'base':p.reference(d/'current-base-context.png','current native context in application order'),'raw':p.reference(d/'raw-v1.png','generated roof repair'),'alpha':p.reference(d/'alpha.png','recorded native-coordinate alpha'),'rectanglesLTRBFeather':rects,'formula':'alpha=round255max(smoothstep rectangle weights); RGB=(base*(255-alpha)+raw*alpha+127)//255','tile':'r03_c05','tileBox':box,'noResize':True,'noWarp':True,'noSpatialBlur':True,'formalAccepted':False})
 contexts.append({'tileBox':box,'derivedFile':str(d/'derived-context.png'),'supportFile':str(d/'support.png'),'manifest':str(d/'derivation.json')})
p.put_json(HERE/'fragments-integration-spec.json',{'tile':'r03_c05','outputDirectory':'continuation-20261011/fragments-v1','baseCandidate':str(base),'contexts':contexts})
print('2 confined native derivations ready')

