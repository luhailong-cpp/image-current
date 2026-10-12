import sys,pathlib,json,numpy as np,hashlib
from PIL import Image
Z=pathlib.Path(__file__).resolve().parents[2];T=Z/'r05_c03';sys.path.insert(0,str(Z));import assemble_native as A
arr,src,missing=A.load_sources(T,A.validate_tile('r05_c03')[1]);strips=[];paths=[]
def join(a,b,path):
 left,right=a[:,-230:],b[:,:230];out=np.where((np.arange(230)[None,:]>=path[:,None])[...,None],right,left);return np.concatenate([a[:,:-230],out,b[:,230:]],axis=1)
for r in range(4):
 row=arr[r,0]
 for c in range(1,4):
  p=np.full(1254,0 if r==3 and c==1 else 115,np.int32);row=join(row,arr[r,c],p);paths.append({'axis':'x','row':r+1,'col':c+1,'path':p.tolist()})
 strips.append(row)
a=strips[0].transpose(1,0,2)
for r in range(1,4):
 p=np.full(4326,115,np.int32)
 if r==3:
  p[:2350]=0
  p[2350:2465]=np.arange(115)
 a=join(a,strips[r].transpose(1,0,2),p);paths.append({'axis':'y','row':r+1,'path':p.tolist()})
im=Image.fromarray(a.transpose(1,0,2)[115:4211,115:4211])
sig=hashlib.sha256(json.dumps({'sources':src,'paths':paths},sort_keys=True).encode()).hexdigest()[:12];name='r05_c03-candidate-local-cuts-v2-'+sig
out=A.save_png(im,T/'candidate'/(name+'.png'));m=json.loads((T/'candidate/r05_c03-candidate-hard-65f341e34b58.assembly.json').read_text());m.update(createdAtUtc=A.now(),method='hard-with-bounded-native-overlap-cuts',output=out,nativeSources=src,seamPaths=paths,script={'file':str(pathlib.Path(__file__).resolve()),'sha256':A.sha(pathlib.Path(__file__))})
m['qa']=A.write_qa(im,out,T/'qa'/name);A.write_json(T/'candidate'/(name+'.assembly.json'),m);print(json.dumps({'output':out,'qa':str(T/'qa'/name)},indent=2))

