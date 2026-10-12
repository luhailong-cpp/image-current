from production import *
sys.path.insert(0,str(B))
from assemble_r03_c03 import append_hard
D=W/'south-current-v1';D.mkdir(exist_ok=True);sources={};strips=[];sids=[];cuts=[]
for c in range(1,5):
 p=native(4,c);g=read(str(p)+'.generation.json');key=12+c;sources[key]={'sourceId':key,'file':str(p),'sha256':sha(p),'globalNativeBox':g['globalNativeBox'],'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')};im=np.asarray(Image.open(p));ii=np.full(im.shape[:2],key,np.uint16)
 if c==1:strip=im;sid=ii
 else:strip,sid,cut=append_hard(strip,sid,im,ii,'v'+str(c));cuts.append(cut)
m=read(B/'work-r03_c02/west-final/final-joint.assembly.json');current=np.asarray(Image.open(m['candidate']));currentids=np.asarray(Image.open(m['sourceIdFile']));south=np.asarray(Image.open(southern_context()));gy,gx=np.indices(south.shape[:2]);gx+=8077;gy+=8077;ids=currentids[np.clip(gy-8192,0,4095),np.clip(gx-4096,0,8191)].astype(np.uint16)+10000
for k in np.unique(ids):
 s=m['sources'][str(k-10000)];sources[int(k)]={**s,'sourceId':int(k)}
a,oi,cut=append_hard(strip.transpose(1,0,2),sid.T,south.transpose(1,0,2),ids.T,'r02-r03');a=a.transpose(1,0,2);oi=oi.T;cuts.append(cut)
for s in sources.values():
 yy,xx=np.nonzero(oi==s['sourceId']);src=np.asarray(Image.open(s['file']));b=s['globalNativeBox'];assert np.array_equal(a[yy,xx],src[yy+7053-b[1],xx+8077-b[0]])
p=D/'pair.png';ip=D/'source-id.png';Image.fromarray(a).save(p);Image.fromarray(oi).save(ip)
write(D/'assembly.json',{'globalBox':[8077,7053,12403,9331],'candidate':{'file':str(p),'sha256':sha(p)},'sourceIdMap':{'file':str(ip),'sha256':sha(ip)},'sources':sources,'seams':cuts,'proof':{'pixels':int(oi.size),'mismatches':0},'status':'pending-100percent-review'})
for c in range(4):Image.fromarray(a).crop((115+c*1024,900,115+(c+1)*1024,1500)).save(D/f'seam-{c+1}.png')
print(json.dumps({'pixels':int(oi.size),'mismatches':0,'sources':len(sources)}))
