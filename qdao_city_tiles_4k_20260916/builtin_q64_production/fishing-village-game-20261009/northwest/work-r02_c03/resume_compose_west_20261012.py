from repair_composite import *
D=W/'resume-20261012-v1';F=D/'composition-v7';F.mkdir(exist_ok=True)
a,ids,sources=loadbase('resume-20261012-v1/composition-v2')
b=[7565,8077,8819,9331];gy,gx=np.indices((1254,1254));gx+=b[0];gy+=b[1]
m=read(B/'work-r03_c02/west-final/r03_c02.west-final.assembly.json');bm=np.asarray(Image.open(m['sourceIdMap']['file']));base=np.asarray(Image.open(m['candidate']['file']))
jm=read(B/'work-r03_c02/west-final/final-joint.assembly.json');old19=jm['sources']['19'];assert old19['globalNativeBox']==b
def common(s):
 for key,v in sources.items():
  if v['sha256']==s['sha256'] and v['globalNativeBox']==s['globalNativeBox']:return int(key)
 key=max(max(int(k) for k in sources)+1,20000);s=s.copy();s['sourceId']=key;sources[str(key)]=s;return key
wi=np.full((1254,1254),common(old19),dtype=np.uint16);wa=np.asarray(Image.open(old19['file'])).copy()
cond=(gx<8192)&(gy>=8192);wa[cond]=base[gy[cond]-8192,gx[cond]-4096]
bc=bm[np.clip(gy-8192,0,4095),np.clip(gx-4096,0,4095)]
for s in m['sources']:wi[cond&(bc==s['sourceId'])]=common(s)
cond=(gx>=8077);wa[cond]=a[gy[cond]-3981,gx[cond]-8077];wi[cond]=ids[gy[cond]-3981,gx[cond]-8077]
n='r02_r03_roof_west_bridge_v02';p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');assert g['globalNativeBox']==b
src=np.asarray(Image.open(p));cost=np.sum((wa.astype(np.int32)-src.astype(np.int32))**2,axis=2,dtype=np.int64)+1
lc,_=minimum_path(cost,0,180);rc,_=minimum_path(cost,1080,1253);tc,_=minimum_path(cost.T,0,160);yy,xx=np.indices((1254,1254))
blue=lambda z:(z[:,:,2].astype(int)>z[:,:,0].astype(int)+25)&(z[:,:,2].astype(int)>z[:,:,1].astype(int)+2)
bl=blue(wa)|blue(src);lo=np.where(bl,yy,1254).min(axis=0);hi=np.where(bl,yy,-1).max(axis=0);obj=(yy>=lo[None,:])&(yy<=hi[None,:]+8)
mask=(xx>=lc[:,None])&(xx<rc[:,None])&(yy>=tc[None,:])&obj
wa[mask]=src[mask];wi[mask]=120;sources['120']={'sourceId':120,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')}
cond=(gx>=8077);a[gy[cond]-3981,gx[cond]-8077]=wa[cond];ids[gy[cond]-3981,gx[cond]-8077]=wi[cond]
Image.fromarray(wa).save(F/'west-joint.png');Image.fromarray(wi).save(F/'west-joint.source-id.png');Image.fromarray(mask.astype(np.uint8)*255).save(F/(n+'.mask.png'))
checks=[]
for k in np.unique(wi):
 s=sources[str(k)];im=np.asarray(Image.open(s['file']));iy,ix=np.nonzero(wi==k);sx=ix+b[0]-s['globalNativeBox'][0];sy=iy+b[1]-s['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(wa[iy,ix],im[sy,sx]);checks.append({'sourceId':int(k),'pixels':len(iy),'mismatches':0})
write(F/'west-joint.assembly.json',{'globalBox':b,'candidate':{'file':str(F/'west-joint.png'),'sha256':sha(F/'west-joint.png')},'sourceIdMap':{'file':str(F/'west-joint.source-id.png'),'sha256':sha(F/'west-joint.source-id.png')},'sources':sources,'proof':{'pixels':1254*1254,'mismatches':0,'contributions':checks},'sourceSelectionOnly':True,'nativeScaleResampled':False,'formalAccepted':False})
write(F/(n+'.mask.json'),{'sourceId':120,'globalNativeBox':b,'pixels':int(mask.sum()),'mask':str(F/(n+'.mask.png')),'maskSha256':sha(F/(n+'.mask.png')),'method':'hard source path within narrow native blue ceramic connector union with tiny shadow; source-selection only; no RGB alteration'})
finish(F,a,ids,sources)
pair=Image.fromarray(a)
for j in range(4):pair.crop((115+j*1024,3980,115+(j+1)*1024,4580)).save(F/f'south-{j+1}.png')
print(json.dumps({'final':str(F),'westJointProofMismatches':0}))
