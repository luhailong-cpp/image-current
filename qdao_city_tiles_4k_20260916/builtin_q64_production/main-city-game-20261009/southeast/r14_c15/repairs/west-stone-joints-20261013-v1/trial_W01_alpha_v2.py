from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;out=D/'W01-alpha-v2';out.mkdir(exist_ok=False)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
p=read(D/'W01/preparation.json')
old=np.array(Image.open(p['unmarkedReference']['path']).convert('RGB'));srcpath=D/'W01/actual-native-6de871737bf798b4.png';new=np.array(Image.open(srcpath).convert('RGB'))
prior=np.array(Image.open(p['fullAlpha']['path']).convert('L'))
# Pixel-source-preserving alpha only: find an upper bottom join in previously authorized rectangle.
# Left side must remain below removed branch y610; at right the removed branch is higher.
x0,y0,x1,y1=p['nativeCrop'];n=x1-x0
error=np.mean((old.astype(np.float32)-new.astype(np.float32))**2,axis=2)
ys=np.arange(590,666);h=len(ys)
cost=np.full((h,n),np.inf,dtype=np.float64);back=np.zeros((h,n),np.int16)
for j,x in enumerate(range(x0,x1)):
 lo=round(646-(x-x0)*0.12)
 hi=min(665,lo+18)
 for i,y in enumerate(ys):
  if not lo<=y<=hi:continue
  val=float(error[y-3:y+4,x].mean())
  if j==0:cost[i,j]=val
  else:
   a=max(0,i-1);b=min(h,i+2);k=a+int(np.argmin(cost[a:b,j-1]));cost[i,j]=val+cost[k,j-1];back[i,j]=k
idx=int(np.argmin(cost[:,-1]));path=np.zeros(n,np.int16)
for j in range(n-1,-1,-1):
 path[j]=ys[idx]
 if j:idx=int(back[idx,j])
alpha=prior.copy()
for j,x in enumerate(range(x0,x1)):
 end=int(path[j]);fade=24
 for y in range(y0,y1):
  cap=max(0,min(255,round(255*(end-y)/fade)))
  alpha[y,x]=min(int(alpha[y,x]),cap)
assert np.all(alpha<=prior)
Image.fromarray(alpha).save(out/'alpha-native-1254.png')
Image.fromarray(alpha[y0:y1,x0:x1]).save(out/'alpha-crop.png')
np.savez_compressed(out/'minimum-error-bottom-path.npz',x=np.arange(x0,x1,dtype=np.int16),y=path)
blend=((old.astype(np.uint32)*(255-alpha[...,None])+new.astype(np.uint32)*alpha[...,None]+127)//255).astype(np.uint8)
Image.fromarray(blend).save(out/'composed-core-join-1254.png')
for name,b in {'bottom-shoulder-before':[870,590,1060,760],'bottom-shoulder-after':[870,590,1060,760],'fixed-west-boundary-after':[512,400,896,744],'top-after':[512,390,1080,550],'right-after':[920,406,1080,744],'bottom-after':[512,560,1080,760]}.items():
 im=blend
 if name.endswith('before'):
  im=((old.astype(np.uint32)*(255-prior[...,None])+new.astype(np.uint32)*prior[...,None]+127)//255).astype(np.uint8)
 Image.fromarray(im[b[1]:b[3],b[0]:b[2]]).save(out/(name+'.png'))
doc={'schemaVersion':1,'operation':'same_native_alpha_reselection_only','priorPreparation':info(D/'W01/preparation.json'),'actualNative':info(srcpath),'priorAlpha':p['fullAlpha'],'newAlpha':info(out/'alpha-native-1254.png'),'newAlphaCrop':info(out/'alpha-crop.png'),'minimumErrorPath':info(out/'minimum-error-bottom-path.npz'),'method':'Across x640..999 choose minimum mean squared RGB error path, y window [round(646-(x-640)*0.12), +18], 1px per column step; cap old alpha with 24px linear transition to zero at path. No RGB alteration or resampling.','nativeCrop':p['nativeCrop'],'pasteBoxIn4096':p['pasteBoxIn4096'],'alphaSupportSubsetOfOriginal':True,'newNetworkCall':False,'formalAccepted':False,'published':False}
(out/'alpha-selection.json').write_text(json.dumps(doc,indent=2),encoding='utf-8')
print(json.dumps({'dir':str(out),'pathMinMax':[int(path.min()),int(path.max())],'selection':info(out/'alpha-selection.json')}))

