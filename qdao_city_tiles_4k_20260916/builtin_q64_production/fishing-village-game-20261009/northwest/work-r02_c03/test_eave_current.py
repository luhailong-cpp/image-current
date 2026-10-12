from production import *
sys.path.insert(0,str(B));from apply_r03_c03_repairs import minimum_path
m=read(W/'south-current-v1/assembly.json');a=np.asarray(Image.open(m['candidate']['file'])).copy();ids=np.asarray(Image.open(m['sourceIdMap']['file'])).copy();em=read(W/'eave-whole-v1/assembly.json');e=np.asarray(Image.open(em['candidate']['file']));ei=np.asarray(Image.open(em['sourceIdMap']['file']));orig=a[:,:1254].copy();cost=np.sum((orig.astype(np.int32)-e.astype(np.int32))**2,axis=2,dtype=np.int64)+1;left,_=minimum_path(cost,115,230);right,_=minimum_path(cost,1100,1253);yy,xx=np.indices(cost.shape);mask=np.isin(ei,[3,4])&(xx>=left[:,None])&(xx<right[:,None]);a[:,:1254][mask]=e[mask];ids[:,:1254][mask]=ei[mask]+900
for s in em['sources']:
 if s['sourceId'] in [3,4]:m['sources'][str(s['sourceId']+900)]={**s,'sourceId':s['sourceId']+900}
D=W/'eave-current-test';D.mkdir(exist_ok=True);Image.fromarray(a).save(D/'pair.png');Image.fromarray(ids).save(D/'source-id.png');Image.fromarray(mask.astype(np.uint8)*255).save(D/'mask.png');write(D/'assembly.json',{'globalBox':m['globalBox'],'sources':m['sources'],'status':'diagnostic-not-accepted'})
for n,b in [('left',[0,870,480,2200]),('right',[900,870,1470,2200]),('center',[300,900,1200,1650])]:Image.fromarray(a).crop(b).save(D/(n+'.png'))
print(json.dumps({'selected':int(mask.sum())}))
