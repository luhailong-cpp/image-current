from repair_composite import *
D=W/'resume-20261012-v1';F=D/'composition-v9';F.mkdir(exist_ok=True)
a,i,s=loadbase('resume-20261012-v1/composition-v8');wm=read(D/'composition-v8/west-joint.assembly.json');wa=np.asarray(Image.open(D/'composition-v8/west-joint.png')).copy();wi=np.asarray(Image.open(D/'composition-v8/west-joint.source-id.png')).copy();b=wm['globalBox'];yy,xx=np.indices(wi.shape)
src=np.asarray(Image.open(W/'native/r02_r03_roof_west_bridge_v02.png'));cost=np.sum((wa.astype(np.int32)-src.astype(np.int32))**2,axis=2,dtype=np.int64)+1;lc,_=minimum_path(cost,0,180)
blue=lambda z:(z[:,:,2].astype(int)>z[:,:,0].astype(int)+25)&(z[:,:,2].astype(int)>z[:,:,1].astype(int)+2)
bl=blue(wa)|blue(src);lo=np.where(bl,yy,1254).min(axis=0);hi=np.where(bl,yy,-1).max(axis=0);mask=(yy>=115)&(xx<627)&(xx>=lc[:,None])&(yy>=lo[None,:])&(yy<=hi[None,:]+8)
wa[mask]=src[mask];wi[mask]=120
gy,gx=yy+b[1],xx+b[0];cond=(gx>=8077)&(gx<8192);a[gy[cond]-3981,gx[cond]-8077]=wa[cond];i[gy[cond]-3981,gx[cond]-8077]=wi[cond]
finish(F,a,i,s);Image.fromarray(wa).save(F/'west-joint.png');Image.fromarray(wi).save(F/'west-joint.source-id.png');wm['candidate']={'file':str(F/'west-joint.png'),'sha256':sha(F/'west-joint.png')};wm['sourceIdMap']={'file':str(F/'west-joint.source-id.png'),'sha256':sha(F/'west-joint.source-id.png')};wm['sources']=s
checks=[]
for k in np.unique(wi):
 z=s[str(k)];im=np.asarray(Image.open(z['file']));iy,ix=np.nonzero(wi==k);sx=ix+b[0]-z['globalNativeBox'][0];sy=iy+b[1]-z['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(wa[iy,ix],im[sy,sx]);checks.append({'sourceId':int(k),'pixels':len(iy),'mismatches':0})
wm['proof']={'pixels':1254*1254,'mismatches':0,'contributions':checks};wm['adoptableNeighborPart']='r03_c02 core y>=8192; upper-left region y<8192 belongs to future r02_c02 and is guide-only';write(F/'west-joint.assembly.json',wm)
assert sha(F/'r02_c03.candidate.png')==sha(D/'composition-v8/r02_c03.candidate.png')
print(json.dumps({'final':str(F),'candidateUnchangedFromV8':True}))
