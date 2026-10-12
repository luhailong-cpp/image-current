from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;B=W.parents[1];sys.path[:0]=[str(B),str(B/'work-r03_c04')]
from apply_r03_c04_repairs import minimum_path
rd=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:np.array(Image.open(p).convert('RGB'))
def info(p,**k):return dict(file=str(p),sha256=sha(p),**k)
def wr(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
v1=rd(W/'blue-final-v1/assembly.json');v2=rd(W/'blue-final-v2/assembly.json');sources=v1['sources'].copy();arts=[];arrays={};original=rd(B/'work-r03_c04/joint-south-resume/proposal-v1/joint-assembly.json')
for tile in ['r03_c04','r04_c04']:
 art=next(q for q in v1['artifacts'] if q['tile']==tile);p=v2['candidate']['file'] if tile=='r03_c04' else art['file'];ip=v2['sourceIdMap']['file'] if tile=='r03_c04' else art['sourceIdMap']['file'];arrays[tile]=[rgb(p),np.array(Image.open(ip)).astype(np.uint16),art]
for sid,name in [(49,'r03_c04_road_north_seam_finish_v01'),(50,'r03_c04_road_west_seam_finish_v01')]:
 p=W/(name+'.png');r=rd(str(p)+'.generation.json');sources.append(dict(sourceId=sid,file=str(p),sha256=sha(p),generationRecord=str(p)+'.generation.json',generationRecordSha256=sha(str(p)+'.generation.json'),globalNativeBox=r['globalNativeBox'],actualModel=None,actualQuality=None,nativeScaleResampled=False))
a,i,_=arrays['r03_c04'];n=rgb(sources[-2]['file']);y0=2783;x0=2842;reg=a[y0:y0+1254,x0:x0+1254];cost=np.sum((reg.astype(np.int32)-n.astype(np.int32))**2,axis=2,dtype=np.int64)
xx=np.arange(1254);guide=np.interp(xx,[0,235,439,848,1150,1253],[211,414,265,580,365,437]);yy,xx=np.indices((1254,1254));grout=(reg.astype(np.int64).sum(2)+n.astype(np.int64).sum(2))*100+cost//20;grout[np.abs(yy-guide[None,:])>14]=10**12;top,_=minimum_path(grout.T,0,800)
bot,_=minimum_path(cost.T,1100,1253);mask=(yy>=top[None,:])&(yy<bot[None,:]);reg[mask]=n[mask];i[y0:y0+1254,x0:x0+1254][mask]=49;northmask=mask.copy()
n=rgb(sources[-1]['file']);y0=2508;x0=1962;reg=a[y0:y0+1254,x0:x0+1254];cost=np.sum((reg.astype(np.int32)-n.astype(np.int32))**2,axis=2,dtype=np.int64);top,_=minimum_path(cost.T,0,140);bot,_=minimum_path(cost.T,1100,1253);rightcut,_=minimum_path(cost,1000,1253);yy,xx=np.indices((1254,1254));mask=(yy>=top[None,:])&(yy<bot[None,:])&(xx>=242)&(xx<rightcut[:,None]);pole=np.interp(np.arange(1254),[0,1040,1105,1180,1240,1253],[242,244,306,324,270,270]);mask &= xx>=pole[:,None];reg[mask]=n[mask];i[y0:y0+1254,x0:x0+1254][mask]=50;westmask=mask.copy()
D=W/'blue-final-v3';D.mkdir(exist_ok=True);Image.fromarray((northmask*255).astype('uint8')).save(D/'north-mask.png');Image.fromarray((westmask*255).astype('uint8')).save(D/'west-mask.png')
for tile,(a,i,art) in arrays.items():
 p=D/(tile+'.candidate.png');ip=D/(tile+'.source-id.png');Image.fromarray(a).save(p);Image.fromarray(i).save(ip);orig=next(q for q in original['artifacts'] if q['globalBox']==art['globalBox']);changed=np.any(a!=rgb(orig['file']),axis=2);Image.fromarray((changed*255).astype('uint8')).save(D/(tile+'.changed-mask.png'));counts=[]
 for s in sources:
  yy,xx=np.nonzero(i==s['sourceId'])
  if not len(xx):continue
  assert sha(s['file'])==s['sha256'];native=rgb(s['file']);sy=yy+art['globalBox'][1]-s['globalNativeBox'][1];sx=xx+12288-s['globalNativeBox'][0];assert np.array_equal(a[yy,xx],native[sy,sx]);counts.append(dict(sourceId=s['sourceId'],pixels=len(xx),mismatches=0))
 arts.append(dict(tile=tile,**info(p),sourceIdMap=info(ip),changedMask=info(D/(tile+'.changed-mask.png')),globalBox=art['globalBox'],changedPixels=int(changed.sum()),proof=dict(pixels=16777216,mismatches=0,contributions=counts),base=orig))
a=arrays['r03_c04'][0];s=arrays['r04_c04'][0]
def crop(name,box):
 x,y,x1,y1=box;Image.fromarray(a[y-8192:y1-8192,x-12288:x1-12288]).save(D/(name+'.100pct.png'))
crop('road-full',[14050,10500,16384,12288]);Image.open(D/'road-full.100pct.png').resize((1400,1073)).save(D/'road-full.preview.png')
crop('north-cut',[15040,11000,16384,11720]);crop('west-cut',[14300,10700,15580,11930]);crop('lower-cut',[15130,12050,16384,12288]);crop('tassel',[15530,10975,15850,11450]);Image.fromarray(np.concatenate([a[3776:4096,2842:4096],s[:320,2842:4096]],axis=0)).save(D/'shared-road-boundary.100pct.png')
wr(D/'assembly.json',dict(createdAt=datetime.now(timezone.utc).isoformat(),status='pending visual QA',formalAccepted=False,baseAssembly=info(B/'work-r03_c04/joint-south-resume/proposal-v1/joint-assembly.json'),sources=sources,artifacts=arts,script=info(Path(__file__)),resize=False,feather=False,modelActual=None,qualityActual=None))
print(json.dumps({'artifacts':[{k:v for k,v in q.items() if k not in ['base','proof']} for q in arts]}))
