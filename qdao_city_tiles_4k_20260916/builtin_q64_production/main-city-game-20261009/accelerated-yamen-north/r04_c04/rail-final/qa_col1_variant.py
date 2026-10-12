from pathlib import Path
import sys, json, importlib.util, hashlib, shutil
sys.dont_write_bytecode=True
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent;T=O.parent
spec=importlib.util.spec_from_file_location('p',T.parent/'pipeline.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
Q=O/'qa-native-col1';Q.mkdir(exist_ok=True)
arrays={}
for patch in p.patch_ids():
 f=p.selected(T,patch)
 if patch in ['s03_01','s04_01']: f=O/'exported-native-v1'/f'{patch}-rail-connector-derived.png'
 arrays[int(patch[1:3])-1,int(patch[4:6])-1]=np.array(Image.open(f).convert('RGB'))
im,paths=p.assemble_arrays(arrays,'minimum-error');im.save(Q/'candidate-minimum-error.png')
for name,box in [('rail-full-join-native',(450,2900,1100,4096)),('internal-y3072-segment01-native',(0,2912,1024,3232)),('internal-y3072-segment02-native',(1024,2912,2048,3232)),('internal-x1024-bottom-native',(864,3072,1184,4096)),('internal-y3072-segment03-native',(2048,2912,3072,3232)),('internal-y3072-segment04-native',(3072,2912,4096,3232))]:
 im.crop(box).save(Q/(name+'.png'))
S=np.array(Image.open(T.parent.parent/'northwest/r05_c04/native/s01_01.png').convert('RGB'))
Image.fromarray(np.concatenate([np.array(im)[-320:,:1024],S[115:435,115:1139]],axis=0)).save(Q/'external-south-segment01-native.png')
(Q/'seam-paths.json').write_text(json.dumps(paths),encoding='utf-8')
print('saved col1-only candidate')
