from workflow import *
sys.path.insert(0,str(B));sys.path.insert(0,str(B/'work-r03_c04'))
from assemble_r03_c03 import compose
from apply_r03_c04_repairs import minimum_path,window_mask
O=W/sys.argv[1];O.mkdir(exist_ok=True);Q=O/'qa';Q.mkdir(exist_ok=True)
sources=[];arrays={};seen={}
def add(p):
 p=Path(p);key=str(p.resolve()).lower()
 if key in seen:return seen[key]
 g=read(str(p)+'.generation.json');assert sha(p)==g['sha256'];a=np.asarray(Image.open(p).convert('RGB'));assert a.shape==(1254,1254,3);sid=len(sources)+1
 sources.append({'sourceId':sid,'file':str(p),'sha256':sha(p),'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json'),'globalNativeBox':g['globalNativeBox'],'nativeScaleResampled':False,'actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality')});arrays[sid]=a;seen[key]=sid;return sid
patches=[]
for r in range(1,5):
 for c in range(1,5):
  p=selected(r,c);sid=add(p);assert sid==(r-1)*4+c;patches.append(arrays[sid])
pixels,ids,seams=compose(patches);ids=ids.astype(np.uint16)
inherit=[]
for ap,axis,box in [(NEIGHBORS[0],'north',[OX,OY,OX+4096,OY+115]),(NEIGHBORS[1],'west',[OX,OY,OX+115,OY+4096])]:
 a,m,oldids,rec=sample(ap,box);mapped=np.zeros_like(oldids,dtype=np.uint16)
 for s in rec['sources']:
  old=s.get('sourceId',s.get('jointSourceId'))
  if np.any(oldids==old):mapped[oldids==old]=add(s['file'])
 view=pixels[:115,:] if axis=='north' else pixels[:,:115];iv=ids[:115,:] if axis=='north' else ids[:,:115]
 d=a.astype(np.int32)-view.astype(np.int32);cost=np.sum(d*d,axis=2,dtype=np.int64);cost[~m]=1<<50
 costpath=cost.T if axis=='north' else cost
 path,total=minimum_path(costpath,1,114)
 take=(np.arange(115)[:,None]<path[None,:]) if axis=='north' else (np.arange(115)[None,:]<path[:,None]);take &= m
 view[take]=a[take];iv[take]=mapped[take]
 inherit.append({'assembly':str(ap),'sha256':sha(ap),'axis':axis,'withinNewTileOnly':True,'selectedPixels':int(take.sum()),'path':path.tolist(),'cost':total})
nrec=read(NEIGHBORS[0]);npng=B/'delivery-2x2/stage-v4/r04_c04.png';north=np.asarray(Image.open(npng).convert('RGB')).copy();no=np.asarray(Image.open(nrec['sourceIdMap']['file']));ni=np.zeros_like(no,dtype=np.uint16)
for s in nrec['sources']:
 old=s.get('sourceId',s.get('jointSourceId'))
 if np.any(no==old):ni[no==old]=add(s['file'])
assert ni.min()>0
bridge=B/'native/r05_c04_slim_post_head_bridge_v01.png';sid=add(bridge);g=sources[sid-1]['globalNativeBox'];base=np.zeros((1254,1254,3),np.uint8)
cut=OY-g[1];xx=g[0]-OX
base[:cut]=north[g[1]-12288:4096,xx:xx+1254]
base[cut:]=pixels[:1254-cut,xx:xx+1254]
mask,path=window_mask(base,arrays[sid],[380,400,1254,1254]);head=base.copy();head[mask]=arrays[sid][mask]
mb=mask[:cut];north[g[1]-12288:4096,xx:xx+1254][mb]=head[:cut][mb];ni[g[1]-12288:4096,xx:xx+1254][mb]=sid
mbs=mask[cut:];pixels[:1254-cut,xx:xx+1254][mbs]=head[cut:][mbs];ids[:1254-cut,xx:xx+1254][mbs]=sid
delta=np.zeros((4096,4096),np.uint8);delta[g[1]-12288:4096,xx:xx+1254]=mask[:cut].astype(np.uint8)*255
Image.fromarray(mask.astype(np.uint8)*255).save(O/'north-head-bridge.mask.png');Image.fromarray(head).save(Q/'north-head-bridge.100pct.png');Image.fromarray(base).save(Q/'north-head-before.100pct.png')
Image.fromarray(delta).save(O/'r04_c04.delta-mask.png');dids=np.zeros_like(ni);dids[delta>0]=sid;Image.fromarray(dids).save(O/'r04_c04.delta-source-id.png')
Image.fromarray(north).save(O/'r04_c04.with-north-head.png');Image.fromarray(ni).save(O/'r04_c04.source-id.png')
Image.fromarray(pixels).save(O/'r05_c04.candidate.png');Image.fromarray(ids).save(O/'r05_c04.source-id.png');write(O/'seams.json',seams)
def proof(a,ix,origin):
 counts=[];miss=0
 for s in sources:
  yy,xx=np.nonzero(ix==s['sourceId']);g=s['globalNativeBox'];sx=xx+origin[0]-g[0];sy=yy+origin[1]-g[1]
  assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));miss+=int(np.any(arrays[s['sourceId']][sy,sx]!=a[yy,xx],axis=1).sum());counts.append({'sourceId':s['sourceId'],'pixelCount':int(xx.size)})
 assert miss==0 and (ix>0).all();return {'verifiedPixels':int(ix.size),'pixelMismatches':miss,'uncovered':int((ix==0).sum()),'allPixelsNativeExact':True,'counts':counts}
proofs={'r05_c04':proof(pixels,ids,[OX,OY]),'r04_c04':proof(north,ni,[OX,12288])};write(O/'replay-proof.json',proofs)
baseline={'candidate':{'file':str(npng),'sha256':sha(npng)},'assembly':{'file':str(NEIGHBORS[0]),'sha256':sha(NEIGHBORS[0])},'sourceIdMap':{'file':nrec['sourceIdMap']['file'],'sha256':sha(nrec['sourceIdMap']['file'])}}
overlay={'id':'north-slim-post-head','file':str(bridge),'sha256':sha(bridge),'sourceId':sid,'globalNativeBox':g,'mask':str(O/'north-head-bridge.mask.png'),'maskSha256':sha(O/'north-head-bridge.mask.png'),'paths':path,'selectedPixels':int(mask.sum()),'northSelectedPixels':int((delta>0).sum()),'southSelectedPixels':int(mbs.sum()),'wholeCoreForced':False}
for tile,a,ix,origin,fn,idfn in [('r05_c04',pixels,ids,[OX,OY],'r05_c04.candidate.png','r05_c04.source-id.png'),('r04_c04',north,ni,[OX,12288],'r04_c04.with-north-head.png','r04_c04.source-id.png')]:
 rec={'tile':tile,'createdAt':datetime.now(timezone.utc).isoformat(),'status':'candidate-pending-full-native-QA','formalAccepted':False,'globalCoreBox':origin+[origin[0]+4096,origin[1]+4096],'candidate':{'file':str(O/fn),'sha256':sha(O/fn)},'sourceIdMap':{'file':str(O/idfn),'sha256':sha(O/idfn)},'sources':sources,'composition':{'method':'native integer minimum-error hard cuts, existing north/west native inheritance inside new tile then exact native head bridge window','resample':False,'feather':False,'paint':False,'colorMatching':False},'boundaryInheritance':inherit if tile=='r05_c04' else [],'overlays':[overlay],'baseline':baseline if tile=='r04_c04' else None,'proof':{'file':str(O/'replay-proof.json'),'sha256':sha(O/'replay-proof.json')},'script':{'file':str(Path(__file__)),'sha256':sha(__file__)}}
 write(O/('assembly.json' if tile=='r05_c04' else 'r04_c04.assembly.json'),rec)
write(O/'north-delta.json',{'target':'r04_c04','baseline':baseline,'overlay':overlay,'mask':{'file':str(O/'r04_c04.delta-mask.png'),'sha256':sha(O/'r04_c04.delta-mask.png')},'sourceIdMap':{'file':str(O/'r04_c04.delta-source-id.png'),'sha256':sha(O/'r04_c04.delta-source-id.png')},'candidate':str(O/'r04_c04.with-north-head.png'),'assembly':str(O/'r04_c04.assembly.json'),'status':'pending-native-visual-QA'})
for k in (1,2,3):
 for j in range(4):
  Image.fromarray(pixels[j*1024:(j+1)*1024,k*1024-200:k*1024+200]).save(Q/f'v{k}-{j+1}.100pct.png');Image.fromarray(pixels[k*1024-200:k*1024+200,j*1024:(j+1)*1024]).save(Q/f'h{k}-{j+1}.100pct.png')
for y in (1024,2048,3072):
 for x in (1024,2048,3072):Image.fromarray(pixels[y-260:y+260,x-260:x+260]).save(Q/f'junction-{x}-{y}.100pct.png')
west=np.asarray(Image.open(B/'work-r05_c03/final-v1/r05_c03.candidate.png').convert('RGB'))
for j in range(4):
 Image.fromarray(np.concatenate([north[-200:,j*1024:(j+1)*1024],pixels[:200,j*1024:(j+1)*1024]],axis=0)).save(Q/f'north-{j+1}.100pct.png');Image.fromarray(np.concatenate([west[j*1024:(j+1)*1024,-200:],pixels[j*1024:(j+1)*1024,:200]],axis=1)).save(Q/f'west-{j+1}.100pct.png')
for r in range(4):
 for c in range(4):Image.fromarray(pixels[r*1024:(r+1)*1024,c*1024:(c+1)*1024]).save(Q/f'core-{r+1}-{c+1}.100pct.png')
Image.fromarray(pixels).resize((1024,1024),Image.Resampling.LANCZOS).save(Q/'overview-review-only.png')
# Four full native sides of whole head bridge for review, 260px strips plus exact context.
for label,bb in [('top',[0,0,1254,300]),('bottom',[0,954,1254,1254]),('left',[0,0,500,1254]),('right',[954,0,1254,1254])]:Image.fromarray(head).crop(bb).save(Q/f'head-{label}.100pct.png')
print(json.dumps({'sources':len(sources),'tileSha256':sha(O/'r05_c04.candidate.png'),'northDeltaPixels':int((delta>0).sum()),'proof':{k:{'pixels':v['verifiedPixels'],'mismatches':v['pixelMismatches']} for k,v in proofs.items()}}))
