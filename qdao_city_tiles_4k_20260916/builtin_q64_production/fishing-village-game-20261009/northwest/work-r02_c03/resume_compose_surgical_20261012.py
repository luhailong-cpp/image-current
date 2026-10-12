from repair_composite import *
D=W/'resume-20261012-v1';F=D/'composition-v8';F.mkdir(exist_ok=True)
a,i,s=loadbase('resume-20261012-v1/composition-v7');n='r02_r03_roof_west_surgical_v03'
patch(a,i,s,n,121,top=(400,520),bottom=(1170,1253),left=(0,50),right=(1100,1253),mode='roof',out=F)
finish(F,a,i,s)
wm=read(D/'composition-v7/west-joint.assembly.json');wa=np.asarray(Image.open(D/'composition-v7/west-joint.png')).copy();wi=np.asarray(Image.open(D/'composition-v7/west-joint.source-id.png')).copy();b=wm['globalBox'];yy,xx=np.indices(wi.shape);gx=xx+b[0];gy=yy+b[1];cond=gx>=8077;wa[cond]=a[gy[cond]-3981,gx[cond]-8077];wi[cond]=i[gy[cond]-3981,gx[cond]-8077]
Image.fromarray(wa).save(F/'west-joint.png');Image.fromarray(wi).save(F/'west-joint.source-id.png');wm['candidate']={'file':str(F/'west-joint.png'),'sha256':sha(F/'west-joint.png')};wm['sourceIdMap']={'file':str(F/'west-joint.source-id.png'),'sha256':sha(F/'west-joint.source-id.png')};wm['sources']=s
checks=[]
for k in np.unique(wi):
 z=s[str(k)];im=np.asarray(Image.open(z['file']));iy,ix=np.nonzero(wi==k);sx=ix+b[0]-z['globalNativeBox'][0];sy=iy+b[1]-z['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(wa[iy,ix],im[sy,sx]);checks.append({'sourceId':int(k),'pixels':len(iy),'mismatches':0})
wm['proof']={'pixels':1254*1254,'mismatches':0,'contributions':checks};write(F/'west-joint.assembly.json',wm)
pair=Image.fromarray(a)
for j in range(4):pair.crop((115+j*1024,3980,115+(j+1)*1024,4580)).save(F/f'south-{j+1}.png')
print(json.dumps({'final':str(F),'westJointProofMismatches':0}))
