from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageFilter
W=Path(__file__).resolve().parent;B=W.parents[1];sys.path[:0]=[str(B),str(B/'work-r03_c04')]
from apply_r03_c04_repairs import minimum_path
rd=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:np.array(Image.open(p).convert('RGB'))
def info(p,**k):return dict(file=str(p),sha256=sha(p),**k)
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=rd(W/'blue-final-v3/assembly.json');sources=m['sources'].copy();n0=rgb(m['artifacts'][0]['file']);s0=rgb(m['artifacts'][1]['file']);ni0=np.array(Image.open(m['artifacts'][0]['sourceIdMap']['file']));si0=np.array(Image.open(m['artifacts'][1]['sourceIdMap']['file']));a=np.concatenate([n0,s0],axis=0);i=np.concatenate([ni0,si0],axis=0);p=W/'r03_c04_road_right_seam_finish_v01.png';r=rd(str(p)+'.generation.json');sources.append(dict(sourceId=51,file=str(p),sha256=sha(p),generationRecord=str(p)+'.generation.json',generationRecordSha256=sha(str(p)+'.generation.json'),globalNativeBox=r['globalNativeBox'],actualModel=None,actualQuality=None,nativeScaleResampled=False));n=rgb(p);reg=a[3298:4552,2842:4096];cost=np.sum((reg.astype(np.int32)-n.astype(np.int32))**2,axis=2,dtype=np.int64);top,_=minimum_path(cost.T,0,220);bottom,_=minimum_path(cost.T,1100,1253);left,_=minimum_path(cost,0,115);yy,xx=np.indices((1254,1254));mask=(yy>=top[None,:])&(yy<bottom[None,:])&(xx>=left[:,None]);reg[mask]=n[mask];i[3298:4552,2842:4096][mask]=51
# Restore complete original colored fish/tassel objects, including their antialiased silhouette.
old=rgb(m['artifacts'][0]['base']['file']);oi=np.array(Image.open(m['artifacts'][0]['base']['sourceIdMap']['file']));prop=np.zeros((4096,4096),bool)
for box in [[15100,9900,16384,10960],[15580,10900,15820,11410]]:
 x,y,x1,y1=box;v=old[y-8192:y1-8192,x-12288:x1-12288].astype('int16');q=(v[:,:,0]-v[:,:,2]>55)&(v[:,:,0]>100);q=np.array(Image.fromarray((q*255).astype('uint8')).filter(ImageFilter.MaxFilter(5)))>0;prop[y-8192:y1-8192,x-12288:x1-12288] |= q
a[:4096][prop]=old[prop];i[:4096][prop]=oi[prop]
D=W/'final-candidate';D.mkdir(exist_ok=True);Image.fromarray((mask*255).astype('uint8')).save(D/'right-native-mask.png');arts=[]
for idx,tile in enumerate(['r03_c04','r04_c04']):
 out=a[idx*4096:(idx+1)*4096];ids=i[idx*4096:(idx+1)*4096];art=m['artifacts'][idx];p=D/(tile+'.candidate.png');ip=D/(tile+'.source-id.png');Image.fromarray(out).save(p);Image.fromarray(ids.astype('uint16')).save(ip);changed=np.any(out!=rgb(art['base']['file']),axis=2);cp=D/(tile+'.changed-mask.png');Image.fromarray((changed*255).astype('uint8')).save(cp);arts.append(dict(tile=tile,**info(p),globalBox=art['globalBox'],sourceIdMap=info(ip),changedMask=info(cp),changedPixels=int(changed.sum()),base=art['base']))
def crop(name,box):
 x,y,x1,y1=box;p=D/(name+'.100pct.png');Image.fromarray(a[y-8192:y1-8192,x-12288:x1-12288]).save(p);return info(p,globalBox=box,nativeScale=1)
ds=[]
for name,box in [('road-full',[14050,10500,16384,12550]),('north-cut',[15040,11000,16384,11720]),('west-cut',[14300,10700,15580,11930]),('lower-cut',[15130,12050,16384,12450]),('tassel',[15530,10975,15850,11450]),('north-west-turn',[14450,10900,15450,11800]),('shared-road-boundary',[15130,11968,16384,12608]),('south-native-bottom',[15130,12590,16384,12800])]:ds.append(crop(name,box))
Image.open(D/'road-full.100pct.png').resize((1400,1230)).save(D/'road-full.preview.png')
wr(D/'assembly.json',dict(createdAt=datetime.now(timezone.utc).isoformat(),status='pending independent replay and 100% review',formalAccepted=False,baseAssembly=m['baseAssembly'],sources=sources,artifacts=arts,diagnostics=ds,script=info(Path(__file__)),resize=False,feather=False,proceduralPainting=False,modelActual=None,qualityActual=None))
print(json.dumps({'artifacts':[{k:v for k,v in q.items() if k!='base'} for q in arts]}))
