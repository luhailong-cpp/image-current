from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
from datetime import datetime,timezone
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest/work-r02_c04/resume-20261012-v03/');W=D.parent;old=W/'resume-20261012-v02';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,j):Path(p).write_text(json.dumps(j,indent=2),encoding='utf8')
def path(cost,step=3):
 h,w=cost.shape;prev=cost[:,0].copy();back=np.zeros((h,w),np.int16)
 for x in range(1,w):
  v=np.stack([np.roll(prev,k) for k in range(-step,step+1)])
  for k in range(-step,step+1):
   if k<0:v[k+step,k:]=1e15
   elif k>0:v[k+step,:k]=1e15
  z=np.argmin(v,axis=0);back[:,x]=z-step;prev=v[z,np.arange(h)]+cost[:,x]
 y=int(np.argmin(prev));line=np.empty(w,int)
 for x in range(w-1,-1,-1):line[x]=y;y-=int(back[y,x])
 return line
def mask(src,base,bands):
 cost=np.mean(abs(src.astype(float)-base.astype(float)),axis=2)+.05;yy,xx=np.indices(cost.shape);t,b,l,r=bands
 def horizontal(band):
  z=cost.copy();z[(yy<band[0])|(yy>band[1])]=1e12;return path(z)
 def vertical(band):
  z=cost.copy();z[(xx<band[0])|(xx>band[1])]=1e12;return path(z.T)
 return (yy>=horizontal(t)[None,:])&(yy<=horizontal(b)[None,:])&(xx>=vertical(l)[:,None])&(xx<=vertical(r)[:,None])
m=json.loads((old/'joint.assembly.json').read_text()); rgb=np.asarray(Image.open(old/'joint.context.png').convert('RGB')).copy(); ids=np.asarray(Image.open(old/'joint.source-id.png')).copy();ox,oy=m['globalBox'][:2];sources=m['sources'];patches=[]
for n,bands in [('r02_c04_foliage_internal_L_repair_20261012_v01',[(410,475),(795,850),(370,445),(825,890)]),('r02_c04_foliage_stonecap_corner_repair_20261012_v01',[(340,380),(530,610),(470,525),(680,745)])]:
 p=W/'native'/(n+'.png');g=json.loads(Path(str(p)+'.generation.json').read_text());b=g['globalNativeBox'];x,y=b[0]-ox,b[1]-oy;a=np.asarray(Image.open(p).convert('RGB'));base=rgb[y:y+1254,x:x+1254];mm=mask(a,base,bands)
 if 'stonecap' in n:
  R,G,B=base.astype(float).transpose(2,0,1);mm&=(G>R*1.018)&(G>B*1.018)
 k=max(s['sourceId'] for s in sources)+1;base[mm]=a[mm];ids[y:y+1254,x:x+1254][mm]=k
 mp=D/(n+'.hard-mask.png');Image.fromarray(mm.astype(np.uint8)*255).save(mp);sources.append({'sourceId':k,'file':str(p),'sha256':sha(p),'globalNativeBox':b,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'actualModel':None,'actualQuality':None,'nativeScaleResampled':False}); patches.append({'id':n,'sourceId':k,'globalNativeBox':b,'hardMask':str(mp),'hardMaskSHA256':sha(mp),'pixels':int(mm.sum()),'composition':'binary optimal seams choose original native pixels; no blending'});Image.fromarray(base).save(D/'qa'/(n+'.composed.100pct.png'))
Image.fromarray(rgb).save(D/'joint.context.png');Image.fromarray(ids).save(D/'joint.source-id.png');m.update({'file':str(D/'joint.context.png'),'sha256':sha(D/'joint.context.png'),'sourceIdMap':str(D/'joint.source-id.png'),'sourceIdSHA256':sha(D/'joint.source-id.png'),'sources':sources,'baseAssembly':str(old/'joint.assembly.json'),'baseAssemblySHA256':sha(old/'joint.assembly.json'),'patches':patches,'status':'new-internal-foliage-repair-candidate'});write(D/'joint.assembly.json',m)
crop=rgb[115:4211,115:4211];ci=ids[115:4211,115:4211];basecrop=np.asarray(Image.open(old/'r02_c04.candidate.png').convert('RGB'));assert np.array_equal(crop[3584:],basecrop[3584:]);assert np.array_equal(crop[:,:300],basecrop[:,:300]);assert np.array_equal(crop[:,-300:],basecrop[:,-300:]);assert np.array_equal(rgb[4211:],np.asarray(Image.open(old/'joint.context.png'))[4211:])
Image.fromarray(crop).save(D/'r02_c04.candidate.png');Image.fromarray(ci).save(D/'r02_c04.source-id.png')
rows=[]
for s in sources:
 yy,xx=np.nonzero(ci==s['sourceId'])
 if not len(xx):continue
 a=np.asarray(Image.open(s['file']).convert('RGB'));xs=xx+12288-s['globalNativeBox'][0];ys=yy+4096-s['globalNativeBox'][1];valid=(xs>=0)&(xs<a.shape[1])&(ys>=0)&(ys<a.shape[0]);assert valid.all();mis=int(np.any(crop[yy,xx]!=a[ys,xs],axis=1).sum());assert mis==0;assert sha(s['file'])==s['sha256'];rows.append({'sourceId':s['sourceId'],'file':s['file'],'sha256':s['sha256'],'pixels':len(xx),'invalidCoordinates':0,'mismatches':0})
proof={'pixels':int(ci.size),'uncovered':int((ci==0).sum()),'mismatches':0,'invalidCoordinates':0,'nativeScaleResampled':False,'feathered':False,'painted':False,'sources':rows};assert proof['uncovered']==0;write(D/'r02_c04.source-proof.json',proof)
a=json.loads((old/'r02_c04.assembly.json').read_text());a.update({'createdAt':datetime.now(timezone.utc).isoformat(),'candidate':{'file':str(D/'r02_c04.candidate.png'),'sha256':sha(D/'r02_c04.candidate.png')},'sourceIdMap':{'file':str(D/'r02_c04.source-id.png'),'sha256':sha(D/'r02_c04.source-id.png')},'sources':sources,'inputs':[{'assembly':str(D/'joint.assembly.json'),'sha256':sha(D/'joint.assembly.json'),'crop':[115,115,4211,4211]},{'baseAssembly':str(old/'r02_c04.assembly.json'),'sha256':sha(old/'r02_c04.assembly.json')}],'overlays':a.get('overlays',[])+patches,'proof':{'file':str(D/'r02_c04.source-proof.json'),'sha256':sha(D/'r02_c04.source-proof.json'),'pixels':int(ci.size),'mismatches':0},'status':'internal-visual-QA-pending','formalAccepted':False});write(D/'r02_c04.assembly.json',a)
Image.fromarray(crop).resize((1024,1024),Image.Resampling.LANCZOS).save(D/'qa/r02_c04.preview-only.png')
inv=json.loads((old/'final-internal-qa-materials/inventory.json').read_text());q=D/'final-internal-qa-materials';q.mkdir(exist_ok=True);rows=[]
for z in inv['materials']:
 p=q/Path(z['file']).name;Image.fromarray(crop).crop(z['cropBox']).save(p);rows.append(dict(z,file=str(p),sha256=sha(p),matchesPriorReviewedPixels=sha(p)==z['sha256'],priorMaterial=z['file']))
write(q/'inventory.json',{'candidateSHA256':sha(D/'r02_c04.candidate.png'),'counts':inv['counts'],'nativeScaleResampled':False,'materials':rows})
write(D/'unchanged-regions-proof.json',{'baseCandidateSHA256':sha(old/'r02_c04.candidate.png'),'candidateSHA256':sha(D/'r02_c04.candidate.png'),'southLast512PixelsUnchanged':True,'west300PixelsUnchanged':True,'east300PixelsUnchanged':True,'r03NeighborDeltaAllPixelsUnchanged':True,'independentDelta':str(old/'r03_c04-independent-north-delta/delta.json'),'independentDeltaSHA256':sha(old/'r03_c04-independent-north-delta/delta.json'),'changedPixels':int(np.any(crop!=basecrop,axis=2).sum())})
print(json.dumps({'candidate':a['candidate'],'proof':{k:proof[k] for k in ['pixels','mismatches','uncovered']},'patches':patches,'changedMaterials':[str(z['file']) for z in rows if not z['matchesPriorReviewedPixels']]}))

