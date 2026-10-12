from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;B=W.parents[1];sys.path.insert(0,str(B/'work-r03_c04'));sys.path.insert(0,str(B))
from apply_r03_c04_repairs import minimum_path
rd=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:np.asarray(Image.open(p).convert('RGB')).copy()
def info(p,**kw):return {'file':str(p),'sha256':sha(p),**kw}
def wr(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
base=B/'work-r03_c04/joint-south-resume/proposal-v1';m=rd(base/'joint-assembly.json');a0=next(x for x in m['artifacts'] if x['globalBox']==[12288,8192,16384,12288]);a=rgb(a0['file']);bi=np.asarray(Image.open(a0['sourceIdMap']['file']));i=bi.copy();original=a.copy();sources=m['sources'].copy()
new=W/'r03_c04_road_edge_north_v02.png';r=rgb(new);rec=rd(str(new)+'.generation.json');sid=max(s['sourceId'] for s in sources)+1;box=rec['globalNativeBox'];x0,y0=box[0]-12288,box[1]-8192
region=a[y0:y0+1254,x0:x0+1254];cost=np.sum((region.astype(np.int32)-r.astype(np.int32))**2,axis=2,dtype=np.int64)
top,tc=minimum_path(cost.T,0,220);bottom,bc=minimum_path(cost.T,1024,1253)
yy,xx=np.indices((1254,1254));mask=(yy>=top[None,:])&(yy<bottom[None,:]);region[mask]=r[mask];i[y0:y0+1254,x0:x0+1254][mask]=sid
sources.append({'sourceId':sid,'file':str(new),'sha256':sha(new),'generationRecord':str(new)+'.generation.json','generationRecordSha256':sha(str(new)+'.generation.json'),'globalNativeBox':box,'actualModel':None,'actualQuality':None,'nativeScaleResampled':False})
out=W/'stage-north';out.mkdir(exist_ok=True)
p=out/'r03_c04.candidate.png';ip=out/'r03_c04.source-id.png';Image.fromarray(a).save(p);Image.fromarray(i).save(ip);Image.fromarray((mask*255).astype(np.uint8)).save(out/'native-mask.png')
ds=[]
def crop(name,box):
 x,y,x2,y2=box;p=out/(name+'.100pct.png');Image.fromarray(a[y-8192:y2-8192,x-12288:x2-12288]).save(p);ds.append(info(p,globalBox=box,nativeScale=1))
crop('north',[15130,10860,16384,11200]);crop('south',[15130,11990,16384,12288]);crop('west',[14960,10975,15430,12229]);crop('old-break-full',[14960,11360,16384,11820]);crop('tassel',[15540,10975,15800,11470])
proof=[]
for s in sources:
 syid=s['sourceId'];yy,xx=np.nonzero(i==syid)
 if not len(xx):continue
 assert sha(s['file'])==s['sha256'];v=rgb(s['file']);sx=xx+12288-s['globalNativeBox'][0];sy=yy+8192-s['globalNativeBox'][1];assert np.array_equal(a[yy,xx],v[sy,sx]);proof.append({'sourceId':syid,'pixels':len(xx),'mismatches':0})
assert np.array_equal(a[4096-59:],original[4096-59:])
manifest={'createdAt':datetime.now(timezone.utc).isoformat(),'candidate':info(p),'sourceIdMap':info(ip),'globalBox':[12288,8192,16384,12288],'sources':sources,'base':a0,'baseAssembly':info(base/'joint-assembly.json'),'newSourceId':sid,'newNative':info(new),'newNativePixels':int(mask.sum()),'cut':{'topYByX':top.tolist(),'bottomYByX':bottom.tolist(),'globalNativeBox':box,'hardSelection':True},'proof':{'pixels':16777216,'mismatches':0,'contributions':proof},'diagnostics':ds,'formalAccepted':False,'resize':False,'feather':False,'script':info(Path(__file__))}
wr(out/'assembly.json',manifest);print(json.dumps({'candidate':manifest['candidate'],'pixels':int(mask.sum())}))
