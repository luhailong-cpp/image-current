from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,os,sys
from datetime import datetime,timezone
R=Path(__file__).resolve().parent.parent;Q=R/'qa/r08_c11-production';Q.mkdir(exist_ok=True)
assert os.environ.get('ISLAND_PROGRESS_FILE')=='progress-r08_c11.json'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
refs=rd(R/'references.json');plan=next(t for t in rd(R/'coordinate-plan.json')['tiles'] if t['id']=='r08_c11')
mode=sys.argv[1]
if mode=='setup':
 layout=Image.open(refs[0]['file']).convert('RGB')
 for p in plan['patches']:
  f=R/'guides'/f"{p['id']}.layout-only.png"
  if f.exists():continue
  layout.transform((1254,1254),Image.Transform.EXTENT,tuple(p['layoutReferenceBox']),Image.Resampling.BICUBIC).save(f)
  wr(Path(str(f)+'.generation.json'),{'file':str(f),'sha256':sh(f),'operation':'Mechanical enlarged coordinate crop for layout guidance only; not final art.','source':refs[0],'sourceCropBox':p['layoutReferenceBox'],'globalBox':p['nativeGlobalBox'],'usableAsFinalArt':False})
 f=Q/'tile-layout-only.png';layout.transform((1024,1024),Image.Transform.EXTENT,(40960*1254/57344,28672*1254/57344,45056*1254/57344,32768*1254/57344),Image.Resampling.BICUBIC).save(f)
 progress=R/'progress-r08_c11.json'
 if not progress.exists():
  wr(progress,{'schemaVersion':1,'zone':'southeast','status':'guides_prepared','updatedAt':now(),'currentTile':'r08_c11','generatedNativeCount':0,'candidate4kCount':0,'formalAcceptedCount':0,'inFlight':False,'actualModel':None,'actualQuality':None,'submittedParameters':{'model':None,'quality':None},'configSnapshotTargetOnly':rd(R/'progress-r08_c12.json')['configSnapshot'],'southNeighbor':'tiles/r09_c11.candidate-v05.png','eastNeighbor':'tiles/r08_c12.candidate-v15.png','nextStep':'Start p44 at fixed south/east corner; then p43,p42,p41 and expand upward.'})
 wr(Q/'plan.json',{'createdAt':now(),'tile':plan,'tileWorldOrigin':[40960,28672],'sequence':[f'r08_c11_p{r}{c}' for r in [4,3,2,1] for c in [4,3,2,1]],'southCandidate':'tiles/r09_c11.candidate-v05.png','eastCandidate':'tiles/r08_c12.candidate-v15.png','cornerCandidate':'tiles/r09_c12.candidate-v09.png','formalAccepted':False})
 print(str(f));sys.exit(0)

pid=sys.argv[2];ver=sys.argv[3];p=next(p for p in plan['patches'] if p['id']==pid);g=p['nativeGlobalBox'];yy,xx=np.indices((1254,1254));wx=xx+g[0];wy=yy+g[1]
guide=R/'guides'/f'{pid}.layout-only.png';arr=np.array(Image.open(guide).convert('RGB'));provenance=np.zeros((1254,1254),np.uint16);sources=[];coverage=[]
def add_source(file,expected,worldorigin):
 key=(str(Path(file).resolve()),tuple(worldorigin));old=next((s for s in sources if (str(Path(s['file']).resolve()),tuple(s['worldOrigin']))==key),None)
 if old:return old['id']
 assert sh(file)==expected
 s={'id':len(sources)+1,'file':str(file),'sha256':expected,'worldOrigin':worldorigin};sources.append(s);return s['id']
def candidate(tid,ver,origin,extend,allowextend=True):
 file=R/'tiles'/f'{tid}.candidate-{ver}.png';ca=np.asarray(Image.open(file).convert('RGB'));tx=wx-origin[0];ty=wy-origin[1]
 if tid=='r08_c12':
  data=rd(R/'qa/r08_c12.final-visible-source-map-v15.json');ids=np.zeros((4096,4096),np.uint16);ss=[]
  for i,z in enumerate(data['contributions'],1):
   x0,y0,x1,y1=z['destinationBox'];sx,sy=z['sourceCrop'][:2];ids[y0:y1,x0:x1]=i;ss.append({'id':i,'file':z['file'],'sha256':z['sha256'],'originInTile':[x0-sx,y0-sy]})
 else:
  data=rd(R/'qa'/f'{tid}-{ver}'/'source-audit.json');ids=np.asarray(Image.open(data['sourceID']));ss=data['sources']
 assert sh(file)==data['sha256']
 inside=(tx>=0)&(tx<4096)&(ty>=0)&(ty<4096);clx=np.clip(tx,0,4095);cly=np.clip(ty,0,4095);selected=ids[cly,clx]
 ext=((ty>=-115)&(ty<0)&(tx>=0)&(tx<4096)) if extend=='north' else ((tx>=-115)&(tx<0)&(ty>=0)&(ty<4096))
 if not allowextend:ext[:]=False
 for s in ss:
  ox,oy=s['originInTile'];sx=tx-ox;sy=ty-oy;take=(inside|ext)&(selected==s['id'])&(sx>=0)&(sx<1254)&(sy>=0)&(sy<1254)
  if not take.any():continue
  n=add_source(s['file'],s['sha256'],[origin[0]+ox,origin[1]+oy]);a=np.asarray(Image.open(s['file']).convert('RGB'));arr[take]=a[sy[take],sx[take]];provenance[take]=n
  if (take&inside).any():assert np.array_equal(arr[take&inside],ca[ty[take&inside],tx[take&inside]])
 coverage.append({'candidate':str(file),'sha256':sh(file),'candidatePixelsInsideContext':int(inside.sum()),'extendedHaloPixels':int((ext&(provenance>0)).sum()),'extensionRule':'Only the boundary source-ID native may extend at original coordinates when it actually covers the requested outside pixel; never use older displaced geometry.'})
candidate('r09_c11','v05',[40960,32768],'north')
candidate('r08_c12','v15',[45056,28672],'west')
candidate('r09_c12','v09',[45056,32768],'north')
# Adjacent generated patches share actual 230px source coordinates.
for filename in sys.argv[4:]:
 f=R/'native'/filename;rec=rd(Path(str(f)+'.generation.json'));ng=rec['coordinate']['nativeGlobalBox'];sx=wx-ng[0];sy=wy-ng[1];take=(sx>=0)&(sx<1254)&(sy>=0)&(sy<1254)
 assert take.any();n=add_source(f,rec['sha256'],ng[:2]);a=np.asarray(Image.open(f).convert('RGB'));arr[take]=a[sy[take],sx[take]];provenance[take]=n
# Current repair natives provide their real halos into still-unknown neighbors.
# Finished selected cores are restored afterward, so a halo never overrides a
# different already-owned pixel.
overlays=R/'selected-overlays-r08_c11.json'
if overlays.exists():
 for z in rd(overlays)['overlays']:
  f=Path(z['file']);ox,oy=z['originInTile'];sx=wx-(40960+ox);sy=wy-(28672+oy);take=(sx>=0)&(sx<1254)&(sy>=0)&(sy<1254)
  if not take.any():continue
  n=add_source(f,z['sha256'],[40960+ox,28672+oy]);a=np.asarray(Image.open(f).convert('RGB'));arr[take]=a[sy[take],sx[take]];provenance[take]=n
# Exact selected cores override speculative neighbor halos at every already-owned coordinate.
selection=R/'selected-native-r08_c11.json'
if selection.exists():
 for fn in rd(selection)['selected'].values():
  f=R/'native'/fn;rec=rd(Path(str(f)+'.generation.json'));ng=rec['coordinate']['nativeGlobalBox'];sx=wx-ng[0];sy=wy-ng[1];take=(sx>=115)&(sx<1139)&(sy>=115)&(sy<1139)
  if not take.any():continue
  n=add_source(f,rec['sha256'],ng[:2]);a=np.asarray(Image.open(f).convert('RGB'));arr[take]=a[sy[take],sx[take]];provenance[take]=n
overlays=R/'selected-overlays-r08_c11.json'
if overlays.exists():
 for z in rd(overlays)['overlays']:
  f=Path(z['file']);ox,oy=z['originInTile'];sx=wx-(40960+ox);sy=wy-(28672+oy);sc=z['sourceCrop'];take=(sx>=sc[0])&(sx<sc[2])&(sy>=sc[1])&(sy<sc[3])
  if not take.any():continue
  n=add_source(f,z['sha256'],[40960+ox,28672+oy]);a=np.asarray(Image.open(f).convert('RGB'));arr[take]=a[sy[take],sx[take]];provenance[take]=n
# Already finished external candidate CORE pixels are strongest. Do not override
# a selected interior core with an older neighboring speculative halo.
candidate('r09_c11','v05',[40960,32768],'north',False)
candidate('r08_c12','v15',[45056,28672],'west',False)
candidate('r09_c12','v09',[45056,32768],'north',False)
out=R/'guides'/f'{pid}.native-context-{ver}.png';assert not out.exists();Image.fromarray(arr).save(out);sid=Q/f'{pid}-{ver}.context-source-id.png';Image.fromarray(provenance).save(sid)
for s in sources:s['selectedPixels']=int((provenance==s['id']).sum())
wr(Path(str(out)+'.generation.json'),{'file':str(out),'sha256':sh(out),'operation':'Exact same-world-coordinate native pixel anchors over enlarged layout guide; no anchor RGB changes or resampling. Guide only, never final art.','layout':str(guide),'layoutSha256':sh(guide),'coordinate':p,'sources':sources,'sourceID':str(sid),'sourceIDSha256':sh(sid),'candidateAnchors':coverage,'nativeAnchorPixels':int((provenance>0).sum()),'unknownHaloUsesLayoutNotInventedNative':True,'usableAsFinalArt':False})
print(json.dumps({'context':str(out),'sha256':sh(out),'anchorPixels':int((provenance>0).sum()),'sources':[{k:s[k] for k in ['id','file','selectedPixels']} for s in sources if s['selectedPixels']]}))
