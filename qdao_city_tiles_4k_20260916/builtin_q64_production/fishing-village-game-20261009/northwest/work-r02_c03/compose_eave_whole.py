from production import *
sys.path.insert(0,str(B))
from apply_r03_c03_repairs import minimum_path
from assemble_r03_c03 import append_hard
D=W/'eave-whole-v1';D.mkdir(exist_ok=True)
old=read(W/'roof-join-v2/assembly.json');a=np.asarray(Image.open(old['candidate']['file'])).copy();ids=np.asarray(Image.open(old['sourceIdMap']['file'])).copy();sources=old['sources'].copy()
p=B/'native/r02_c03_eave_whole_join_v01.png';im=np.asarray(Image.open(p));g=read(str(p)+'.generation.json');sources.append({'sourceId':4,'file':str(p),'sha256':sha(p),'globalNativeBox':g['globalNativeBox'],'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')})
y=7850-7053;base=a[y:y+1254];cost=np.sum((base.astype(np.int32)-im.astype(np.int32))**2,axis=2,dtype=np.int64)+1
top,_=minimum_path(cost.T,0,230);bottom,_=minimum_path(cost.T,1100,1253);yy,xx=np.indices(cost.shape);mask=(yy>=top[None,:])&(yy<bottom[None,:]);base[mask]=im[mask];ids[y:y+1254][mask]=4
proof=[]
for s in sources:
 yy,xx=np.nonzero(ids==s['sourceId']);src=np.asarray(Image.open(s['file']));b=s['globalNativeBox'];assert np.array_equal(a[yy,xx],src[yy+7053-b[1],xx+8077-b[0]])
 proof.append({'sourceId':s['sourceId'],'pixels':int(len(yy)),'mismatches':0})
cp=D/'pair.png';ip=D/'source-id.png';mp=D/'mask.png';Image.fromarray(a).save(cp);Image.fromarray(ids).save(ip);Image.fromarray(mask.astype(np.uint8)*255).save(mp)
write(D/'assembly.json',{'globalBox':[8077,7053,9331,9331],'candidate':{'file':str(cp),'sha256':sha(cp)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'sources':sources,'proof':proof,'mask':{'file':str(mp),'sha256':sha(mp)},'topPath':top.tolist(),'bottomPath':bottom.tolist(),'status':'candidate-pending-current-baseline-side-checks','formalAccepted':False})
for name,b in [('north',[0,650,1254,1070]),('south',[0,1850,1254,2278]),('left',[0,700,340,2100]),('right',[914,700,1254,2100])]:Image.fromarray(a).crop(b).save(D/(name+'.100pct.png'))
print(json.dumps({'proofPixels':int(ids.size),'mismatches':0,'selected':int(mask.sum())}))
