from repair_composite import *
D=W/'resume-20261012-v1';F=D/'composition-v11';F.mkdir(exist_ok=True)
a,i,s=loadbase('resume-20261012-v1/composition-v10');wm=read(D/'composition-v10/west-joint.assembly.json');wa=np.asarray(Image.open(D/'composition-v10/west-joint.png')).copy();wi=np.asarray(Image.open(D/'composition-v10/west-joint.source-id.png')).copy();b=wm['globalBox']
n='r02_r03_roof_neighbor_surgical_v04';p=W/'native'/(n+'.png');g=read(str(p)+'.generation.json');src=np.asarray(Image.open(p));cost=np.sum((wa.astype(np.int32)-src.astype(np.int32))**2,axis=2,dtype=np.int64)+1
lc,_=minimum_path(cost,460,510);rc,_=minimum_path(cost,680,730);tc,_=minimum_path(cost.T,130,150);bc,_=minimum_path(cost.T,260,280);yy,xx=np.indices(cost.shape);mask=(xx>=lc[:,None])&(xx<rc[:,None])&(yy>=tc[None,:])&(yy<bc[None,:]);wa[mask]=src[mask];wi[mask]=122
s['122']={'sourceId':122,'file':str(p),'sha256':sha(p),'globalNativeBox':g['globalNativeBox'],'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')}
gy,gx=yy+b[1],xx+b[0];cond=(gx>=8077);a[gy[cond]-3981,gx[cond]-8077]=wa[cond];i[gy[cond]-3981,gx[cond]-8077]=wi[cond]
finish(F,a,i,s);Image.fromarray(wa).save(F/'west-joint.png');Image.fromarray(wi).save(F/'west-joint.source-id.png');wm['candidate']={'file':str(F/'west-joint.png'),'sha256':sha(F/'west-joint.png')};wm['sourceIdMap']={'file':str(F/'west-joint.source-id.png'),'sha256':sha(F/'west-joint.source-id.png')};wm['sources']=s
checks=[]
for k in np.unique(wi):
 z=s[str(k)];im=np.asarray(Image.open(z['file']));iy,ix=np.nonzero(wi==k);sx=ix+b[0]-z['globalNativeBox'][0];sy=iy+b[1]-z['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(wa[iy,ix],im[sy,sx]);checks.append({'sourceId':int(k),'pixels':len(iy),'mismatches':0})
wm['proof']={'pixels':1254*1254,'mismatches':0,'contributions':checks};write(F/'west-joint.assembly.json',wm)
mp=F/(n+'.mask.png');Image.fromarray(mask.astype(np.uint8)*255).save(mp);write(F/(n+'.mask.json'),{'file':str(mp),'sha256':sha(mp),'globalNativeBox':b,'pixels':int(mask.sum()),'sourceId':122,'method':'four minimum native RGB difference hard selection paths; no blending or resampling','margins':{'left':[460,510],'right':[680,730],'top':[130,150],'bottom':[260,280]}})
joint=Image.new('RGB',(600,1024));joint.paste(Image.fromarray(wa).crop((327,115,627,1139)),(0,0));joint.paste(Image.fromarray(a).crop((115,4211,415,5235)),(300,0));joint.save(F/'r03-west-east-joint.png');Image.fromarray(wa).crop((350,100,800,350)).save(F/'surgical-join-closeup.png')
assert sha(F/'r02_c03.candidate.png')==sha(D/'composition-v9/r02_c03.candidate.png')
print(json.dumps({'final':str(F),'candidateUnchangedFromV9':True,'selectedPixels':int(mask.sum())}))
