from pathlib import Path
import sys,json,hashlib,importlib.util
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;T=O.parent;Q=O/'qa-native-stairs-restored';Q.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('p',T.parent/'pipeline.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
A=np.array(Image.open(O/'alternative7-native.png').convert('RGB'));B=np.array(Image.open(O/'stage4-derived-native.png').convert('RGB'))
x=np.arange(1254)[None,:]+.5;t=np.clip((x-1012)/(1044-1012),0,1);w=np.broadcast_to(t*t*(3-2*t),(1254,1254));alpha=np.floor(w*255+.5).astype(np.uint32)
C=((A.astype(np.uint32)*(255-alpha[:,:,None])+B.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
Image.fromarray(alpha.astype(np.uint8)).save(O/'restore-stairs-alpha.png')
Image.fromarray(C).save(O/'alternative8-native.png')
arrays={}
for patch in p.patch_ids():
 f=p.selected(T,patch)
 if patch=='s03_01':f=O/'exported-native-v1/s03_01-rail-connector-derived.png'
 if patch=='s04_01':f=O/'alternative8-native.png'
 arrays[int(patch[1:3])-1,int(patch[4:6])-1]=np.array(Image.open(f).convert('RGB'))
im,paths=p.assemble_arrays(arrays,'minimum-error');im.save(Q/'candidate-minimum-error.png')
for name,box in [('rail-full-join-native',(450,2900,1100,4096)),('internal-y3072-segment01-native',(0,2912,1024,3232)),('internal-x1024-bottom-native',(864,3072,1184,4096)),('residual-stair-detail-native',(950,3870,1220,4050))]:im.crop(box).save(Q/(name+'.png'))
S=np.array(Image.open(T.parent.parent/'northwest/r05_c04/native/s01_01.png').convert('RGB'))
Image.fromarray(np.concatenate([np.array(im)[-320:,:1024],S[115:435,115:1139]],axis=0)).save(Q/'external-south-segment01-native.png')
(Q/'seam-paths.json').write_text(json.dumps(paths),encoding='utf-8')
print('same-world stage4 stair restoration alpha trial saved')
