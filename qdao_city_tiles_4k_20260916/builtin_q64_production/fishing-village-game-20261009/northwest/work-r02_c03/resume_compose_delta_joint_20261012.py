from repair_composite import *
D=W/'resume-20261012-v1';F=D/'composition-v10';F.mkdir(exist_ok=True)
a,i,s=loadbase('resume-20261012-v1/composition-v9');wm=read(D/'composition-v9/west-joint.assembly.json');wa=np.asarray(Image.open(D/'composition-v9/west-joint.png')).copy();wi=np.asarray(Image.open(D/'composition-v9/west-joint.source-id.png')).copy();b=wm['globalBox']
src=np.asarray(Image.open(W/'native/r02_r03_roof_west_surgical_v03.png'));sb=s['121']['globalNativeBox'];l=sb[0]-b[0];t=b[1]-sb[1];h=sb[3]-b[1];w=627-l
incoming=src[t:t+h,:w];old=wa[:h,l:627];cost=np.sum((old.astype(np.int32)-incoming.astype(np.int32))**2,axis=2,dtype=np.int64)+1;path,_=minimum_path(cost,10,w-1)
yy,xx=np.indices((h,w));blue=lambda z:(z[:,:,2].astype(int)>z[:,:,0].astype(int)+25)&(z[:,:,2].astype(int)>z[:,:,1].astype(int)+2)
bl=blue(old)|blue(incoming);lo=np.where(bl,yy,h).min(axis=0);hi=np.where(bl,yy,-1).max(axis=0)
mask=(yy>=115)&(xx>=path[:,None])&(yy>=lo[None,:])&(yy<=hi[None,:]+8)
wa[:h,l:627][mask]=incoming[mask];wi[:h,l:627][mask]=121
yy,xx=np.indices(wi.shape);gy,gx=yy+b[1],xx+b[0];cond=(gx>=8077)&(gx<8192);a[gy[cond]-3981,gx[cond]-8077]=wa[cond];i[gy[cond]-3981,gx[cond]-8077]=wi[cond]
finish(F,a,i,s);Image.fromarray(wa).save(F/'west-joint.png');Image.fromarray(wi).save(F/'west-joint.source-id.png');wm['candidate']={'file':str(F/'west-joint.png'),'sha256':sha(F/'west-joint.png')};wm['sourceIdMap']={'file':str(F/'west-joint.source-id.png'),'sha256':sha(F/'west-joint.source-id.png')};wm['sources']=s
checks=[]
for k in np.unique(wi):
 z=s[str(k)];im=np.asarray(Image.open(z['file']));iy,ix=np.nonzero(wi==k);sx=ix+b[0]-z['globalNativeBox'][0];sy=iy+b[1]-z['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(wa[iy,ix],im[sy,sx]);checks.append({'sourceId':int(k),'pixels':len(iy),'mismatches':0})
wm['proof']={'pixels':1254*1254,'mismatches':0,'contributions':checks};write(F/'west-joint.assembly.json',wm)
write(F/'neighbor-joint-selection.json',{'sourceId':121,'globalOverlapBox':[8077,8192,8192,8754],'method':'native RGB difference minimum hard selection path; no blending or resampling','pathNativeX':path.tolist(),'changedPixels':int(mask.sum())})
joint=Image.new('RGB',(600,1024));joint.paste(Image.fromarray(wa).crop((327,115,627,1139)),(0,0));joint.paste(Image.fromarray(a).crop((115,4211,415,5235)),(300,0));joint.save(F/'r03-west-east-joint.png')
assert sha(F/'r02_c03.candidate.png')==sha(D/'composition-v9/r02_c03.candidate.png')
print(json.dumps({'final':str(F),'candidateUnchangedFromV9':True,'selectedPixels':int(mask.sum())}))
