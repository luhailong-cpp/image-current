import sys
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import pipeline as p
d=Path(__file__).resolve().parent/'flower-return01';a=np.array(Image.open(d/'context-native.png').convert('RGB'));b=np.array(Image.open(d/'raw-v1.png').convert('RGB'))
y,x=np.indices((1254,1254));dist=np.sqrt((x-661)**2+(y-693)**2);t=np.clip((dist-54)/11,0,1);alpha=np.rint(255*(1-t*t*(3-2*t))).astype('uint8');out=((a.astype('uint32')*(255-alpha[...,None])+b.astype('uint32')*alpha[...,None]+127)//255).astype('uint8')
p.save_png(d/'alpha.png',Image.fromarray(alpha));p.save_png(d/'support.png',Image.fromarray((alpha>0).astype('uint8')*255));p.save_png(d/'derived-context.png',Image.fromarray(out));p.save_png(d/'qa-native.png',Image.fromarray(out).crop((540,580,780,805)))
p.put_json(d/'derivation.json',{'context':p.reference(d/'context-native.png','same-coordinate source'), 'raw':p.reference(d/'raw-v1.png','generated motif'),'alpha':p.reference(d/'alpha.png','smooth radial material alpha'),'formula':'(base*(255-alpha)+raw*alpha+127)//255; radial center(661,693), full radius54, zero radius65, smoothstep between','tile':'r03_c05','tileBox':[400,2842,1654,4096],'noResize':True,'noWarp':True,'noSpatialBlur':True,'formalAccepted':False})
e=Path(__file__).resolve().parent/'gold-joint01';e.mkdir(exist_ok=True)
p.save_png(e/'context-native.png',Image.fromarray(out));p.put_json(e/'preparation.json',{'source':str(d/'derived-context.png'),'sourceSHA256':p.sha(d/'derived-context.png'),'tile':'r03_c05','tileBox':[400,2842,1654,4096],'worldBox':[16784,11034,18038,12288],'nativePixels':[1254,1254],'defect':'D5 vertical slice where horizontal gold roof beam joins large curved beam near context x750 y100..250'})
print(d)

