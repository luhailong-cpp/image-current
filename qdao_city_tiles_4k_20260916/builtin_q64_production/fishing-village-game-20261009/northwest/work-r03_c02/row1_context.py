from pathlib import Path
import json, importlib.util, hashlib
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent; R=W.parent
spec=importlib.util.spec_from_file_location('assembly',R/'assemble_r03_c03.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
names=['r03_c02_s01_s01_v01','r03_c02_s01_s02_v01','r03_c02_s01_s03_v02','r03_c02_s01_s04_v01','r03_c03_s01_s01_v01']
sources=[]; seams=[]
for sid,n in enumerate(names,1):
 p=R/'native'/f'{n}.png'; a=np.array(Image.open(p).convert('RGB')); sm=np.full((1254,1254),sid,np.uint8)
 sources.append({'id':sid,'file':str(p),'sha256':m.sha(p),'globalNativeBox':m.read(str(p)+'.generation.json')['globalNativeBox']})
 if sid==1: canvas,ids=a,sm
 else:
  canvas,ids,d=m.append_hard(canvas,ids,a,sm,n); seams.append(d)
for sid,n in [(17,'r03_c02_s01_c03_c04_bridge_v01'),(18,'r03_c02_c03_roof_bridge_v01')]:
 p=R/'native'/f'{n}.png'; rec=m.read(str(p)+'.generation.json'); a=np.array(Image.open(p).convert('RGB')); x=rec['globalNativeBox'][0]-3981; old=canvas[:,x:x+1254].copy()
 left,lc=m.minimum_vertical_seam(old[:,:115],a[:,:115]); right,rc=m.minimum_vertical_seam(a[:,1139:],old[:,1139:]); right+=1139
 take=(np.arange(1254)[None,:]>=left[:,None])&(np.arange(1254)[None,:]<right[:,None])
 canvas[:,x:x+1254]=np.where(take[...,None],a,old);ids[:,x:x+1254]=np.where(take,sid,ids[:,x:x+1254])
 sources.append({'id':sid,'file':str(p),'sha256':m.sha(p),'globalNativeBox':rec['globalNativeBox']})
 seams.append({'bridge':n,'leftXByY':left.tolist(),'rightXByY':right.tolist(),'globalOrigin':rec['globalNativeBox'][:2],'wholeCoreForced':True,'resampled':False,'feather':False})
prefix=W/'qa'/'row1-with-approved-bridges'
Image.fromarray(canvas).save(str(prefix)+'.png');Image.fromarray(ids).save(str(prefix)+'.source-id.png')
m.write_json(Path(str(prefix)+'.json'),{'sources':sources,'globalNativeBox':[3981,8077,9331,9331],'seams':seams,'formalAccepted':False,'role':'diagnostic context; cross-tile bridge integration root-owned'})
for sc in range(1,5):
 n=f'r03_c02_s02_s{sc:02d}_v01';p=R/'native'/f'{n}.png'
 if not p.exists():continue
 a=np.array(Image.open(p).convert('RGB'));north=canvas[:,(sc-1)*1024:(sc-1)*1024+1254];northid=ids[:,(sc-1)*1024:(sc-1)*1024+1254]
 joined,jid,d=m.append_hard(north.transpose(1,0,2),northid.T,a.transpose(1,0,2),np.full((1254,1254),20+sc,np.uint8),'north-with-bridges')
 joined=joined.transpose(1,0,2);jid=jid.T;op=W/'qa'/f'{n}.north-context'
 Image.fromarray(joined).save(str(op)+'.hardcut.png');Image.fromarray(jid).save(str(op)+'.source-id.png');Image.fromarray(joined).crop([0,824,1254,1454]).save(str(op)+'.seam100pct.png')
 m.write_json(Path(str(op)+'.json'),{'path':d,'context':str(prefix)+'.json','incoming':str(p),'incomingSHA256':m.sha(p),'globalNativeBox':[3981+(sc-1)*1024,8077,5235+(sc-1)*1024,10355]})
print(str(prefix))
