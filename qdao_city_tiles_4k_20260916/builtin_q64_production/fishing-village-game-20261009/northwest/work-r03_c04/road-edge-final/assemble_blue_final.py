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
S=B/'work-r03_c04/joint-south-resume/proposal-v1';m=rd(S/'joint-assembly.json');sources=m['sources'].copy();arts=[];arrays={}
for tile,box in [('r03_c04',[12288,8192,16384,12288]),('r04_c04',[12288,12288,16384,16384])]:
 a=next(a for a in m['artifacts'] if a['globalBox']==box);arrays[tile]=[rgb(a['file']),np.array(Image.open(a['sourceIdMap']['file'])).astype(np.uint16),a]
for sid,name in [(46,'r03_c04_road_blue_geometry_locked_v01'),(47,'r03_c04_road_north_blue_locked_v01'),(48,'r03_c04_road_west_complete_geometry_v02')]:
 p=W/(name+'.png');r=rd(str(p)+'.generation.json');sources.append(dict(sourceId=sid,file=str(p),sha256=sha(p),generationRecord=str(p)+'.generation.json',generationRecordSha256=sha(str(p)+'.generation.json'),globalNativeBox=r['globalNativeBox'],actualModel=None,actualQuality=None,nativeScaleResampled=False))
right=rgb(sources[-3]['file'])
for tile,(a,i,art) in arrays.items():
 y,x=np.nonzero(i==45);a[y,x]=right[y+art['globalBox'][1]-11490,x+12288-15130];i[y,x]=46
a,i,_=arrays['r03_c04'];n=rgb(sources[-2]['file']);y0=2783;x0=2842;reg=a[y0:y0+1254,x0:x0+1254];cost=np.sum((reg.astype(np.int32)-n.astype(np.int32))**2,axis=2,dtype=np.int64)
# Whole upper slab faces are retained; cut follows the original grout zigzag.
xx=np.arange(1254);top=np.rint(np.interp(xx,[0,235,439,848,1150,1253],[211,414,265,580,365,437])).astype(int)
bot,_=minimum_path(cost.T,970,1253);yy,xx=np.indices((1254,1254));mask=(yy>=top[None,:])&(yy<bot[None,:]);reg[mask]=n[mask];i[y0:y0+1254,x0:x0+1254][mask]=47
northmask=mask.copy()
n=rgb(sources[-1]['file']);y0=2808;x0=1962;reg=a[y0:y0+1254,x0:x0+1254];cost=np.sum((reg.astype(np.int32)-n.astype(np.int32))**2,axis=2,dtype=np.int64)
top,_=minimum_path(cost.T,0,115);bot,_=minimum_path(cost.T,850,1253);rightcut,_=minimum_path(cost,880,1040)
yy,xx=np.indices((1254,1254));mask=(yy>=top[None,:])&(yy<bot[None,:])&(xx>=242)&(xx<rightcut[:,None])
# Preserve the pole and base as entire original objects; only road/sand to their right may change.
pole=np.interp(np.arange(1254),[0,750,805,880,940,1010,1050,1120,1253],[242,244,306,324,270,287,367,390,515])
mask &= xx>=pole[:,None];reg[mask]=n[mask];i[y0:y0+1254,x0:x0+1254][mask]=48
westmask=mask.copy();D=W/'blue-final-v1';D.mkdir(exist_ok=True)
Image.fromarray((northmask*255).astype('uint8')).save(D/'north-mask.png');Image.fromarray((westmask*255).astype('uint8')).save(D/'west-mask.png')
for tile,(a,i,art) in arrays.items():
 p=D/(tile+'.candidate.png');ip=D/(tile+'.source-id.png');Image.fromarray(a).save(p);Image.fromarray(i).save(ip);changed=np.any(a!=rgb(art['file']),axis=2);Image.fromarray((changed*255).astype('uint8')).save(D/(tile+'.changed-mask.png'));counts=[]
 for s in sources:
  yy,xx=np.nonzero(i==s['sourceId'])
  if not len(xx):continue
  assert sha(s['file'])==s['sha256'];native=rgb(s['file']);sy=yy+art['globalBox'][1]-s['globalNativeBox'][1];sx=xx+12288-s['globalNativeBox'][0];assert np.array_equal(a[yy,xx],native[sy,sx]);counts.append(dict(sourceId=s['sourceId'],pixels=len(xx),mismatches=0))
 arts.append(dict(tile=tile,**info(p),sourceIdMap=info(ip),changedMask=info(D/(tile+'.changed-mask.png')),globalBox=art['globalBox'],changedPixels=int(changed.sum()),proof=dict(pixels=16777216,mismatches=0,contributions=counts),base=art))
a=arrays['r03_c04'][0];s=arrays['r04_c04'][0]
Image.fromarray(a[2600:4096,1762:4096]).save(D/'road-full.100pct.png')
Image.fromarray(a[2600:4096,1762:4096]).resize((1400,897)).save(D/'road-full.preview.png')
Image.fromarray(a[2690:3240,2760:4096]).save(D/'north-cut.100pct.png')
Image.fromarray(a[2780:3710,1870:3270]).save(D/'west-cut.100pct.png')
Image.fromarray(np.concatenate([a[3776:4096,2842:4096],s[:320,2842:4096]],axis=0)).save(D/'shared-road-boundary.100pct.png')
wr(D/'assembly.json',dict(createdAt=datetime.now(timezone.utc).isoformat(),status='pending visual QA',formalAccepted=False,baseAssembly=info(S/'joint-assembly.json'),sources=sources,artifacts=arts,script=info(Path(__file__)),resize=False,feather=False,modelActual=None,qualityActual=None))
print(json.dumps({'artifacts':[{k:v for k,v in a.items() if k not in ['base','proof']} for a in arts]}))
