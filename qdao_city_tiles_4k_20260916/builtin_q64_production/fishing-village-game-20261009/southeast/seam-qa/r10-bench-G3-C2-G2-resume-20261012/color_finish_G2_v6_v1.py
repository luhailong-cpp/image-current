from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;B=D.parent.parent; STEM='eastdeck-G2-v6-color-finish-v1'; FRAME=[32141,37925,33395,39179]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rawp=D/'eastdeck-G2-conditioned-v6-raw.png'; oldp=D/'eastdeck-G2-conditioned-v5-bounded-preview-native1254.png';maskp=D/'eastdeck-G2-conditioned-v6-adopt-mask-native1254.png'
raw=np.asarray(Image.open(rawp).convert('RGB')).astype(np.float32);old=np.asarray(Image.open(oldp).convert('RGB')).astype(np.float32);m=np.asarray(Image.open(maskp))==255
lum1=old.mean(2);lum2=raw.mean(2)
grad=np.maximum(np.maximum(abs(np.gradient(lum1,axis=0)),abs(np.gradient(lum1,axis=1))),np.maximum(abs(np.gradient(lum2,axis=0)),abs(np.gradient(lum2,axis=1))))
valid=(~m)&(grad<12)&(np.max(abs(old-raw),axis=2)<65)
step=16; xs=np.arange(0,1254+step,step).clip(0,1253);ys=xs.copy();N=len(xs)
grid=np.zeros((N,N,3),np.float32);fixed=np.zeros((N,N),bool)
for j,y in enumerate(ys):
 for i,x in enumerate(xs):
  if m[y,x]:continue
  yy=slice(max(0,y-20),min(1254,y+21));xx=slice(max(0,x-20),min(1254,x+21));ok=valid[yy,xx]
  if ok.sum()>=12:
   grid[j,i]=np.median((old-raw)[yy,xx][ok],axis=0);fixed[j,i]=True
grid=np.clip(grid,-24,24)
for k in range(3500):
 pre=grid.copy()
 grid[1:-1,1:-1]=np.where(fixed[1:-1,1:-1,None],grid[1:-1,1:-1],(pre[:-2,1:-1]+pre[2:,1:-1]+pre[1:-1,:-2]+pre[1:-1,2:])/4)
 if k%100==0 and np.max(abs(grid-pre))<0.0003:break
# Bilinear RGB offset field only, never source-art resampling.
coord=np.arange(1254)/step;i0=np.floor(coord).astype(int);t=(coord-i0).astype(np.float32)
i1=np.minimum(i0+1,N-1);field=np.empty((1254,1254,3),np.float32)
for ch in range(3):
 a=grid[i0[:,None],i0[None,:],ch]*(1-t[:,None])*(1-t[None,:])
 a+=grid[i0[:,None],i1[None,:],ch]*(1-t[:,None])*t[None,:]
 a+=grid[i1[:,None],i0[None,:],ch]*t[:,None]*(1-t[None,:])
 a+=grid[i1[:,None],i1[None,:],ch]*t[:,None]*t[None,:]
 field[:,:,ch]=a
field=np.clip(field,-24,24)
corrected=np.clip(np.rint(raw+field),0,255).astype(np.uint8)
final=old.astype(np.uint8).copy();final[m]=corrected[m]
assert np.array_equal(final[~m],old.astype(np.uint8)[~m])
p=D/(STEM+'-bounded-preview-native1254.png');assert not p.exists();Image.fromarray(final).save(p)
z=D/(STEM+'-replay.npz');assert not z.exists();np.savez_compressed(z,raw=raw.astype(np.uint8),before=old.astype(np.uint8),mask=m,offsetField=field,final=final,grid=grid)
base=json.loads((D/'eastdeck-G2-final-v5.adoption-instructions.json').read_text())
spec=importlib.util.spec_from_file_location('sources',B/'review_external_seams.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);sources=mod.Sources();records=[]
for r in base['patches']:
 cur,err=sources.source(r['tile'],r['patch']);assert not err;assert cur['sha256']==r['sourceSha256']
 native=np.asarray(Image.open(r['source']).convert('RGB')).copy();nb=r['nativeFrameWorld']
 world=[max(nb[0],FRAME[0]),max(nb[1],FRAME[1]),min(nb[2],FRAME[2]),min(nb[3],FRAME[3])]
 sx0,sy0,sx1,sy1=world[0]-FRAME[0],world[1]-FRAME[1],world[2]-FRAME[0],world[3]-FRAME[1];dx,dy=world[0]-nb[0],world[1]-nb[1]
 localmask=m[sy0:sy1,sx0:sx1];piece=final[sy0:sy1,sx0:sx1];dest=native[dy:dy+sy1-sy0,dx:dx+sx1-sx0];dest[localmask]=piece[localmask]
 pp=D/(STEM+'-'+r['tile']+'-'+r['patch']+'-provisional-native1254.png');assert not pp.exists();Image.fromarray(native).save(pp)
 rr={'tile':r['tile'],'patch':r['patch'],'file':str(pp),'sha256':sha(pp),'source':r['source'],'sourceSha256':r['sourceSha256'],'nativeFrameWorld':nb,'selected':False};records.append(rr);sources.tile(r['tile'])['selection']['patches'][r['patch']]=str(pp)
rebuilt,_,missing=sources.extract(FRAME);assert not missing;assert np.array_equal(final,np.asarray(rebuilt))
ev=[]
for n,box in {'center':[376,146,979,1164],'left':[376,146,504,1164],'right':[786,146,979,1164],'top':[440,146,915,274],'bottom':[440,1036,915,1164],'stoneboundary':[550,146,914,354]}.items():
 pp=D/(STEM+'-'+n+'-native.png');assert not pp.exists();Image.fromarray(final).crop(box).save(pp);ev.append({'name':n,'file':str(pp),'sha256':sha(pp),'guideBox':box})
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_native_review','raw':str(rawp),'rawSha256':sha(rawp),'base':str(oldp),'baseSha256':sha(oldp),'mask':str(maskp),'maskSha256':sha(maskp),'fieldOperation':'Bounded additive low-frequency RGB field from robust low-gradient outside-mask samples; harmonic interpolation on16px grid and bilinear field evaluation only. Artwork never resampled, warped, blurred or blended.','maxAbsField':float(abs(field[m]).max()),'colorCap':24,'fieldIterations':k+1,'replay':str(z),'replaySha256':sha(z),'outsideMaskChangedPixels':0,'nativeCoreReplayExact':True,'preview':str(p),'previewSha256':sha(p),'patches':records,'evidence':ev,'formalAccepted':False,'internalReady':False,'materialPending':True,'canonicalSelectionsModified':False}
pp=D/(STEM+'.report.json');assert not pp.exists();pp.write_text(json.dumps(report,indent=2))
print(json.dumps({'report':str(pp),'maxAbsField':report['maxAbsField'],'nativeCoreReplayExact':True,'iterations':k+1}))

