from production import *
sys.path.insert(0,str(B))
from assemble_r03_c03 import append_hard,minimum_vertical_seam
from datetime import datetime,timezone
D=W/'base-v1';D.mkdir(exist_ok=True);Q=D/'qa';Q.mkdir(exist_ok=True)
assert not (D/'r02_c02.candidate.png').exists()
sources=[];key_by_identity={};cuts=[]
def add(z):
 ident=(str(Path(z['file']).resolve()),z['sha256'],tuple(z['globalNativeBox']))
 if ident in key_by_identity:return key_by_identity[ident]
 k=len(sources)+1;item=dict(z);item['sourceId']=k;item['previousSourceId']=z.get('sourceId');sources.append(item);key_by_identity[ident]=k;return k
def import_ids(ids,ss):
 dic={int(z['sourceId']):z for z in ss} if isinstance(ss,list) else {int(k):v for k,v in ss.items()};out=np.zeros(ids.shape,np.uint16)
 for key in np.unique(ids):out[ids==key]=add(dic[int(key)])
 return out
strips=[];sids=[]
for r in range(1,5):
 for c in range(1,5):
  p=native(r,c);assert p;g=read(str(p)+'.generation.json');assert sha(p)==g['sha256']==sha(g['toolOriginal']['file']);assert g['globalNativeBox']==box(r,c);assert g['route']=='builtin';assert g['actualModel'] is None and g['actualQuality'] is None
  req=read(g['evidence']['request']);assert sha(g['evidence']['request'])==g['evidence']['requestSha256'];assert sha(g['evidence']['receipt'])==g['evidence']['receiptSha256'];assert Path(g['prompt']).read_text(encoding='utf8').strip()==req['prompt'].strip();assert sha(g['prompt'])==g['promptSha256']
  assert [z['file'] for z in g['references']]==req['referenced_image_paths'];assert all(sha(z['file'])==z['sha256'] and z['role'] for z in g['references']);assert all(str(ref).replace('\\','/') in [z['file'].replace('\\','/') for z in g['references']] for ref in REFS)
  k=add({'sourceId':(r-1)*4+c,'row':r,'column':c,'file':str(p),'sha256':sha(p),'globalNativeBox':g['globalNativeBox'],'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'actualModel':None,'actualQuality':None,'nativeScaleResampled':False})
  im=np.asarray(Image.open(p).convert('RGB'));assert im.shape==(1254,1254,3);ii=np.full(im.shape[:2],k,np.uint16)
  if c==1:strip=im;sid=ii
  else:strip,sid,cut=append_hard(strip,sid,im,ii,f'own-row-{r}-col-{c-1}-{c}');cuts.append(cut)
 strips.append(strip);sids.append(sid)
a=strips[0];ids=sids[0]
for r in range(1,4):
 a,ids,cut=append_hard(a.transpose(1,0,2),ids.T,strips[r].transpose(1,0,2),sids[r].T,f'own-row-{r}-{r+1}');a=a.transpose(1,0,2);ids=ids.T;cuts.append(cut)
own=a.copy();ownids=ids.copy();Image.fromarray(own).save(D/'own-native-context.png');Image.fromarray(ownids).save(D/'own-source-id.png')
index=read(B/'current-artifacts.json');easm=B/index['r02_c03']['assembly'];sasm=B/index['r03_c02']['assembly'];seasm=B/index['r03_c03']['assembly']
em=read(easm);sm=read(sasm);sem=read(seasm)
assert sha(B/index['r02_c03']['candidate'])=='47aefbfeab411f9da7ddf783e8f625fe4fbd60665d36822d9d93c15e96ad5162'
assert sha(B/index['r03_c02']['candidate'])=='d939a4e2ca9122742753391e252c1ef8626f1722cc9b9ced9a338c20e06f1675'
fm=read(EF/'assembly.json');east=np.asarray(Image.open(fm['candidate']['file']).convert('RGB'))[:4326,:1254];eid=import_ids(np.asarray(Image.open(fm['sourceIdMap']['file']))[:4326,:1254],fm['sources'])
assert np.array_equal(east[115:4211,115:1254],np.asarray(Image.open(em['candidate']['file']).convert('RGB'))[:,:1139])
def bounded_append(base,bi,inc,ii,label,exact_after=None):
 aa=base[:,-230:];bb=inc[:,:230];diff=aa.astype(np.int32)-bb.astype(np.int32);cost=np.sum(diff*diff,axis=2,dtype=np.int64);h,w=cost.shape;cost[:,115:]=1<<50
 if exact_after is not None:cost[exact_after:,:]=1<<50;cost[exact_after:,115]=np.sum(diff[exact_after:,115]**2,axis=1)
 prev=cost[0].copy();back=np.zeros((h,w),np.int8);inf=np.int64(1<<60)
 for y in range(1,h):
  vals=np.stack([prev,np.r_[inf,prev[:-1]],np.r_[prev[1:],inf]]);z=np.argmin(vals,axis=0);back[y]=np.array([0,-1,1],np.int8)[z];prev=cost[y]+vals[z,np.arange(w)]
 line=np.empty(h,int);line[-1]=np.argmin(prev)
 for y in range(h-1,0,-1):line[y-1]=line[y]+back[y,line[y]]
 if exact_after is None:assert np.all(line<115)
 else:assert np.all(line[:exact_after]<115) and np.all(line[exact_after:]==115)
 take=np.arange(230)[None,:]>=line[:,None];out=np.concatenate([base[:,:-230],np.where(take[...,None],bb,aa),inc[:,230:]],axis=1);oi=np.concatenate([bi[:,:-230],np.where(take,ii[:,:230],bi[:,-230:]),ii[:,230:]],axis=1)
 cuts.append({'label':label,'pathLocal':line.tolist(),'overlap':230,'restriction':'cut remains inside new tile; adopted neighbor core pixels remain unchanged','exactBoundaryAfterTransverse':exact_after,'blend':False,'resample':False});return out,oi
a,ids=bounded_append(a,ids,east,eid,'east-adopted-r02_c03')
# Native south context: each selected source contributes only at its registered pixel coordinate.
south=np.empty((1254,5350,3),np.uint8);southids=np.zeros((1254,5350),np.uint16);gy,gx=np.indices(south.shape[:2]);gx+=3981;gy+=8077
for m,ap,left,right,originx in [(sm,sasm,3981,8192,4096),(sem,seasm,8192,9331,8192)]:
 si=np.asarray(Image.open(m['sourceIdMap']['file']));sel=(gx>=left)&(gx<right);oldids=si[np.clip(gy-8192,0,4095),np.clip(gx-originx,0,4095)];ss={int(z['sourceId']):z for z in m['sources']}
 for key in np.unique(oldids[sel]):
  z=ss[int(key)];mask=sel&(oldids==key);yy,xx=np.nonzero(mask);im=np.asarray(Image.open(z['file']).convert('RGB'));sx=gx[yy,xx]-z['globalNativeBox'][0];sy=gy[yy,xx]-z['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));south[yy,xx]=im[sy,sx];southids[yy,xx]=add(z)
 core=sel&(gx>=originx)&(gx<originx+4096)&(gy>=8192);im=np.asarray(Image.open(m['candidate']['file']).convert('RGB'));assert np.array_equal(south[core],im[(gy-8192)[core],(gx-originx)[core]])
a,ids=bounded_append(a.transpose(1,0,2),ids.T,south.transpose(1,0,2),southids.T,'south-adopted-r03_c02',exact_after=4211);a=a.transpose(1,0,2);ids=ids.T
def proof(rgb,ii,origin,path):
 rows=[];assert not (ii==0).any()
 for k in np.unique(ii):
  z=sources[int(k)-1];p=z['file'];assert sha(p)==z['sha256'];im=np.asarray(Image.open(p).convert('RGB'));yy,xx=np.nonzero(ii==k);sx=xx+origin[0]-z['globalNativeBox'][0];sy=yy+origin[1]-z['globalNativeBox'][1];assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));mis=int(np.any(rgb[yy,xx]!=im[sy,sx],axis=1).sum());assert mis==0;rows.append({'sourceId':int(k),'pixels':int(len(xx)),'mismatches':mis,'sha256':sha(p)})
 out={'pixels':int(ii.size),'uncovered':0,'mismatches':0,'invalidCoordinates':0,'contributions':rows,'nativeScaleResampled':False,'feathered':False,'painted':False};write(path,out);return out
Image.fromarray(a).save(D/'full-context.png');Image.fromarray(ids).save(D/'full-source-id.png');fullpr=proof(a,ids,[3981,3981],D/'full-source-proof.json')
crop=a[115:4211,115:4211];ci=ids[115:4211,115:4211];Image.fromarray(crop).save(D/'r02_c02.candidate.png');Image.fromarray(ci).save(D/'r02_c02.source-id.png');pr=proof(crop,ci,[4096,4096],D/'r02_c02.source-proof.json')
assert np.array_equal(a[115:4211,4211:5350],np.asarray(Image.open(em['candidate']['file']).convert('RGB'))[:,:1139]);assert np.array_equal(a[4211:5350,115:4211],np.asarray(Image.open(sm['candidate']['file']).convert('RGB'))[:1139]);assert np.array_equal(a[4211:5350,4211:5350],np.asarray(Image.open(sem['candidate']['file']).convert('RGB'))[:1139,:1139])
neighbors=[{'tile':t,'assembly':str(ap),'assemblySha256':sha(ap),'candidate':m['candidate'],'adoptedCoreChangedPixels':0} for t,ap,m in [('r02_c03',easm,em),('r03_c02',sasm,sm),('r03_c03',seasm,sem)]]
common={'schemaVersion':1,'tile':'r02_c02','createdAtUtc':datetime.now(timezone.utc).isoformat(),'sources':sources,'seams':cuts,'neighbors':neighbors,'actualModel':None,'actualQuality':None,'resampled':False,'feathered':False,'painted':False,'formalAccepted':False,'status':'candidate-awaiting-16-core-24-seam-9-junction-visual-review'}
write(D/'full.assembly.json',{**common,'globalBox':[3981,3981,9331,9331],'candidate':{'file':str(D/'full-context.png'),'sha256':sha(D/'full-context.png')},'sourceIdMap':{'file':str(D/'full-source-id.png'),'sha256':sha(D/'full-source-id.png')},'proof':{'file':str(D/'full-source-proof.json'),'sha256':sha(D/'full-source-proof.json'),'pixels':fullpr['pixels'],'mismatches':0}})
write(D/'r02_c02.assembly.json',{**common,'globalCoreBox':[4096,4096,8192,8192],'outputSize':[4096,4096],'candidate':{'file':str(D/'r02_c02.candidate.png'),'sha256':sha(D/'r02_c02.candidate.png')},'sourceIdMap':{'file':str(D/'r02_c02.source-id.png'),'sha256':sha(D/'r02_c02.source-id.png')},'proof':{'file':str(D/'r02_c02.source-proof.json'),'sha256':sha(D/'r02_c02.source-proof.json'),'pixels':pr['pixels'],'mismatches':0},'fullAssembly':{'file':str(D/'full.assembly.json'),'sha256':sha(D/'full.assembly.json'),'crop':[115,115,4211,4211]}})
print(json.dumps({'ownNativeCount':16,'candidate':str(D/'r02_c02.candidate.png'),'sha256':sha(D/'r02_c02.candidate.png'),'proofPixels':pr['pixels'],'proofMismatches':0,'neighborCoreChangedPixels':0}))
