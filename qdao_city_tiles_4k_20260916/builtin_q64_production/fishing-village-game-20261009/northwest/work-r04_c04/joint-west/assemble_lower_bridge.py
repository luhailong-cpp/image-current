from pathlib import Path
import json,hashlib,sys,importlib.util
import numpy as np
from PIL import Image
from datetime import datetime,timezone
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parent.parent;T=D/'trial-bottom-cut';O=D/'lower-v1';O.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def art(p):return {'file':str(p),'sha256':sha(p)}
def save(p,a):Image.fromarray(a).save(p)
spec=importlib.util.spec_from_file_location('hard',R/'assemble_r03_c03.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
spec=importlib.util.spec_from_file_location('rep',R/'apply_r03_c03_repairs.py');rep=importlib.util.module_from_spec(spec);spec.loader.exec_module(rep)
m=read(T/'joint-west-assembly.json');registry=m['sources'].copy();arrays={}
for s in registry:
 assert sha(s['file'])==s['sha256'];assert sha(s['generationRecord'])==s['generationRecordSha256']
 arrays[s['jointSourceId']]=np.asarray(Image.open(s['file']).convert('RGB'))
def add(file,tile,sid):
 g=read(str(file)+'.generation.json');a=np.asarray(Image.open(file).convert('RGB'));assert a.shape==(1254,1254,3)
 registry.append({'jointSourceId':sid,'tile':tile,'file':str(file),'sha256':sha(file),'generationRecord':str(file)+'.generation.json','generationRecordSha256':sha(str(file)+'.generation.json'),'globalNativeBox':g['globalNativeBox'],'actualModel':g['actualModel'],'actualQuality':g['actualQuality'],'nativeScaleResampled':False});arrays[sid]=a
for cc in range(1,5):
 ss=read(R/f'work-r05_c03/selections/s01_s{cc:02d}.json');add(Path(ss['file']),'r05_c03',53+cc)
add(R/'native/r04_c03_c04_lower_net_transition_bridge_v01.png','global-lower-net-bridge',58)
# Extended canvas, only known sources carry nonzero IDs. Unknown areas never enter final rectangular tiles.
a=np.zeros((5120,8192,3),np.uint8);ids=np.zeros((5120,8192),np.uint8)
for tile,sl in [('r04_c03',slice(0,4096)),('r04_c04',slice(4096,8192))]:
 a[:4096,sl]=np.asarray(Image.open(T/(tile+'.joint-west-proposal.png')));ids[:4096,sl]=np.asarray(Image.open(T/(tile+'.joint-west-source-id.png')))
def row(es):
 es=sorted(es,key=lambda s:s['globalNativeBox'][0]);assert len(es)==4
 o=arrays[es[0]['jointSourceId']].copy();oi=np.full((1254,1254),es[0]['jointSourceId'],np.uint8)
 for e in es[1:]:o,oi,_=h.append_hard(o,oi,arrays[e['jointSourceId']],np.full((1254,1254),e['jointSourceId'],np.uint8),'mechanical-row')
 return o,oi
south,si=row([s for s in registry if s['tile']=='r05_c03'])
assert np.array_equal(south[115:1139,115:4211],np.asarray(Image.open(R/'work-r05_c03/output/r05_c03.first-row.partial.png')))
a[4096:5120,:4211]=south[115:1139,115:4326];ids[4096:5120,:4211]=si[115:1139,115:4326]
before=a.copy();beforeids=ids.copy()
# One global north/south hardcut for existing partial southern row, exact common230 overlap.
upper,ui=row([s for s in registry if s['tile']=='r04_c03' and s['globalNativeBox'][1]==15245])
ub=upper[1024:1254,115:4326].copy();ubi=ui[1024:1254,115:4326].copy()
ub[:115]=a[3981:4096,:4211];ubi[:115]=ids[3981:4096,:4211]
lb=south[:230,115:4326];lbi=si[:230,115:4326]
cost=np.sum((ub.astype(np.int32)-lb.astype(np.int32))**2,axis=2,dtype=np.int64)
cut,total=rep.minimum_path(cost.T,0,229)
take=np.arange(230)[:,None]>=cut[None,:]
a[3981:4211,:4211]=np.where(take[:,:,None],lb,ub);ids[3981:4211,:4211]=np.where(take,lbi,ubi)
# Lower bridge: existing unknown lower-right pixels are owned entirely by native bridge; no guide pixels.
box=[11648,15700,12902,16954];x=box[0]-8192;y=box[1]-12288;ba=arrays[58]
base=a[y:y+1254,x:x+1254].copy();known=ids[y:y+1254,x:x+1254]!=0
# Use bridge itself only as zero-error cost in unknown region (no blend); ownership forced to bridge there.
costbase=base.copy();costbase[~known]=ba[~known]
mask,paths=rep.overlay_mask(costbase,ba)
mask|=~known
reg=a[y:y+1254,x:x+1254];reg[mask]=ba[mask];ids[y:y+1254,x:x+1254][mask]=58
# Support bridge core remains byte exact.
sb=[12865,14365,13889,15389]
assert np.array_equal(a[sb[1]-12288:sb[3]-12288,sb[0]-8192:sb[2]-8192],before[sb[1]-12288:sb[3]-12288,sb[0]-8192:sb[2]-8192])
assert np.array_equal(a[:115,:4096],before[:115,:4096])
counts=[];verified=0
for s in registry:
 yy,xx=np.nonzero(ids==s['jointSourceId']);bx,by,_,_=s['globalNativeBox']
 if len(xx):
  sx=xx+8192-bx;sy=yy+12288-by
  assert ((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254)).all();assert np.array_equal(a[yy,xx],arrays[s['jointSourceId']][sy,sx])
 counts.append({'jointSourceId':s['jointSourceId'],'pixels':len(xx)});verified+=len(xx)
outputs=[]
for tile,sl in [('r04_c03',slice(0,4096)),('r04_c04',slice(4096,8192))]:
 p=O/(tile+'.joint-proposal.png');i=O/(tile+'.source-id.png');save(p,a[:4096,sl]);save(i,ids[:4096,sl]);outputs.append({'file':str(p),'sha256':sha(p),'sourceIdMap':art(i),'globalBox':[8192 if tile.endswith('03') else 12288,12288,12288 if tile.endswith('03') else 16384,16384]})
p=O/'r05_c03.first-row.joint-proposal.png';i=O/'r05_c03.first-row.source-id.png';save(p,a[4096:5120,:4096]);save(i,ids[4096:5120,:4096]);outputs.append({'file':str(p),'sha256':sha(p),'sourceIdMap':art(i),'globalBox':[8192,16384,12288,17408],'partial':True})
save(O/'lower-bridge-mask.png',mask.astype(np.uint8)*255);save(O/'lower-bridge-applied.png',reg);save(O/'lower-bridge-known-base-mask.png',known.astype(np.uint8)*255)
# Explicit valid-pixel diagnostics around boundaries. Alpha0 is unknown, never final game art.
def crop(label,b):
 xx,yy,xx2,yy2=[b[0]-8192,b[1]-12288,b[2]-8192,b[3]-12288];rgb=a[yy:yy2,xx:xx2];ii=ids[yy:yy2,xx:xx2];rgba=np.concatenate((rgb,(ii!=0).astype(np.uint8)[:,:,None]*255),axis=2)
 p=O/(label+'.png');save(p,rgba);return {'file':str(p),'sha256':sha(p),'globalBox':b,'unscaled':True,'unknownPixels':int((ii==0).sum())}
diag=[]
for side,b in [('north',[11648,15500,12902,15930]),('west',[11448,15700,11878,16954]),('east',[12672,15700,13102,16954]),('south',[11648,16724,12902,17154])]:
 diag.append(crop('lower-'+side+'-100pct',b))
for k in range(8):diag.append(crop('west-final-segment-'+str(k+1).zfill(2),[11968,12288+k*512,12608,12288+(k+1)*512]))
for k in range(8):diag.append(crop('south-existing-segment-'+str(k+1).zfill(2),[8192+k*512,16154,8192+(k+1)*512,16614]))
diag.append(crop('southwest-3tiles-intersection-100pct',[11763,15872,12902,16896]))
path={'northSouthGlobalOverlap':[8192,16269,12403,16499],'pathGlobalYByX':(cut+16269).tolist(),'singlePathForBothExistingRows':True,'costSumSquaredRGB':total,'lowerBridgeBox':box,'lowerBridgeSourceId':58,'mask':art(O/'lower-bridge-mask.png'),'paths':paths,'unknownRegionRule':'All previously absent pixels inside lower bridge now exact native58; do not export outside declared 4K tiles/partial existing row as a completed tile.','supportBridgeCorePreserved':True,'northwestNorth115Preserved':True}
write(O/'joint-paths.json',path)
manifest={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'proposals-pending-visual-QA','formalAccepted':False,'globalCanvasBox':[8192,12288,16384,17408],'base':art(T/'joint-west-assembly.json'),'script':art(Path(__file__)),'paths':art(O/'joint-paths.json'),'sources':registry,'artifacts':outputs,'diagnostics':diag,'allKnownCanvasPixelsVerified':verified,'finalDeclaredPixels':2*4096*4096+4096*1024,'contributions':counts,'resize':False,'blend':False,'modifiedOriginalCandidates':False,'supportBridgeCorePreserved':True,'jointNorthCornerPreserved':True,'unreviewedExternalEdges':['right tile north with unfinished r03c04','right lower outward boundary beyond bridge; r05c04 not generated'],'previousFailedLowerCutsSupersededByNative58':True}
write(O/'joint-assembly.json',manifest);print(json.dumps({'manifest':art(O/'joint-assembly.json'),'verifiedPixels':verified,'bridgePixels':int(mask.sum()),'outputs':outputs}))

