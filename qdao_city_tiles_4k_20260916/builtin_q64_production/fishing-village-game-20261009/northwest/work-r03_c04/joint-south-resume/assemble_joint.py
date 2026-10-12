from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;B=W.parents[1]
sys.path.insert(0,str(B));sys.path.insert(0,str(B/'work-r03_c04'))
from assemble_r03_c03 import append_hard
from apply_r03_c04_repairs import minimum_path,overlay_mask
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resolve(p):return Path(p) if Path(p).is_absolute() else B/p
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pixels(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def save(p,a):Image.fromarray(a).save(p)
out=W/('proposal-'+(sys.argv[1] if len(sys.argv)>1 else 'v1'));out.mkdir(exist_ok=True)
sources=[];arrays={};byfile={}
def add(src):
 p=resolve(src['file']);key=str(p.resolve()).lower()
 if key in byfile:return byfile[key]
 rp=resolve(src.get('generationRecord',str(p)+'.generation.json'));r=read(rp)
 assert sha(p)==r['sha256']
 sid=len(sources)+1;byfile[key]=sid
 sources.append({'sourceId':sid,'file':str(p),'sha256':sha(p),'generationRecord':str(rp),'generationRecordSha256':sha(rp),'globalNativeBox':r['globalNativeBox'],'actualModel':r.get('actualModel'),'actualQuality':r.get('actualQuality'),'nativeScaleResampled':False})
 arrays[sid]=pixels(p);assert arrays[sid].shape==(1254,1254,3)
 return sid
nrp=B/'work-r03_c04/tiles/r03_c04.assembly.json';n=read(nrp)
srp=B/'work-r04_c04/joint-west/final-v3/joint-assembly.json';s=read(srp)
npth=B/'work-r03_c04/tiles/r03_c04.candidate.png';nids=resolve(n['sourceIdMap']['file'])
sa=next(a for a in s['artifacts'] if a['globalBox']==[12288,12288,16384,16384]);spth=Path(sa['file']);sids=Path(sa['sourceIdMap']['file'])
j=np.concatenate((pixels(npth),pixels(spth)),axis=0);ji=np.zeros((8192,4096),np.uint16)
ni=np.asarray(Image.open(nids));si=np.asarray(Image.open(sids))
for source in n['sources']:ji[:4096][ni==source['sourceId']]=add(source)
for source in s['sources']:
 old=source.get('jointSourceId',source.get('sourceId'))
 if np.any(si==old):ji[4096:][si==old]=add(source)
assert np.all(ji>0)
base=j.copy();baseids=ji.copy()
def row(tile,rownum):
 plan=read(B/('work-'+tile)/'selected.json');sel=sorted([a for a in plan['sources'] if a['row']==rownum],key=lambda a:a['column'])
 a=None;ids=None
 for v in sel:
  sid=add(v);p=arrays[sid];i=np.full((1254,1254),sid,np.uint16)
  if a is None:a,ids=p.copy(),i
  else:a,ids,_=append_hard(a,ids,p,i,'context-row')
 return a[:,115:4211],ids[:,115:4211]
na,nai=row('r03_c04',4);sb,sbi=row('r04_c04',1)
y=3981
a=np.concatenate((j[y:4096],na[1139:]),axis=0);ai=np.concatenate((ji[y:4096],nai[1139:]),axis=0)
b=np.concatenate((sb[:115],j[4096:4211]),axis=0);bi=np.concatenate((sbi[:115],ji[4096:4211]),axis=0)
cost=np.sum((a.astype(np.int32)-b.astype(np.int32))**2,axis=2,dtype=np.int64).T
# Preserve already-reviewed west corner's exact original tile ownership at x<64.
cost[:64,:]=1<<50;cost[:64,115]=0
path,total=minimum_path(cost,0,229)
take=np.arange(230)[:,None]>=path[None,:]
j[y:y+230]=np.where(take[:,:,None],b,a);ji[y:y+230]=np.where(take,bi,ai)
details=[{'type':'shared horizontal hard cut','globalYByX':(path+12173).tolist(),'globalXStart':12288,'squaredError':total,'preservedOriginalCornerWidth':64}]
for kind in ['post','lamp','road']:
 p=W/('r03_c04_r04_c04_'+kind+'_whole_bridge_v01.png');sid=add({'file':str(p)})
 box=sources[sid-1]['globalNativeBox'];x0,y0=box[0]-12288,box[1]-8192;x1,y1=x0+1254,y0+1254
 crop=j[y0:y1,x0:x1];r=arrays[sid]
 mask,dp=overlay_mask(crop,r)
 if kind=='post':
  cost=np.sum((crop.astype(np.int32)-r.astype(np.int32))**2,axis=2,dtype=np.int64)
  left,total=minimum_path(cost[:,:230],1,60)
  yy,xx=np.indices((1254,1254));right=np.array(dp['rightXByY']);top=np.array(dp['topYByX']);bottom=np.array(dp['bottomYByX'])
  mask=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:]);dp['leftXByY']=left.tolist();dp['leftLimitReason']='retain complete narrow post silhouette x95..222; no seam through its trunk'
 if kind=='road':
  # Road must reach right formal tile edge; east-neighbor seam remains future work.
  yy,xx=np.indices((1254,1254));left=np.array(dp['leftXByY']);top=np.array(dp['topYByX']);bottom=np.array(dp['bottomYByX'])
  mask=(xx>=left[:,None])&(yy>=top[None,:])&(yy<bottom[None,:]);dp['rightXByY']=[1254]*1254;dp['rightEdgeRule']='native bridge reaches formal tile east edge; east neighbor pending'
 crop[mask]=r[mask];ji[y0:y1,x0:x1][mask]=sid
 save(out/(kind+'-ownership-mask.png'),(mask*255).astype(np.uint8));save(out/(kind+'-applied.png'),crop)
 for edge,rect in [('north',(0,0,1254,230)),('south',(0,1024,1254,1254)),('west',(0,0,230,1254)),('east',(1024,0,1254,1254))]:save(out/(kind+'-'+edge+'.png'),crop[rect[1]:rect[3],rect[0]:rect[2]])
 details.append({'type':'whole-object-native-bridge','kind':kind,'sourceId':sid,'globalNativeBox':box,'selectedPixels':int(mask.sum()),'path':dp})
proof=[]
for src in sources:
 sid=src['sourceId'];yy,xx=np.nonzero(ji==sid)
 if len(xx)==0:continue
 box=src['globalNativeBox'];sx=xx+12288-box[0];sy=yy+8192-box[1]
 assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254)),src
 mismatch=int(np.count_nonzero(np.any(j[yy,xx]!=arrays[sid][sy,sx],axis=1)));assert mismatch==0
 proof.append({'sourceId':sid,'pixels':len(xx),'mismatches':mismatch})
artifacts=[]
for name,y0 in [('r03_c04',0),('r04_c04',4096)]:
 p=out/(name+'.joint-proposal.png');ip=out/(name+'.source-id.png');save(p,j[y0:y0+4096]);save(ip,ji[y0:y0+4096]);artifacts.append({'file':str(p),'sha256':sha(p),'globalBox':[12288,8192+y0,16384,12288+y0],'sourceIdMap':{'file':str(ip),'sha256':sha(ip)}})
for i in range(8):save(out/f'shared-segment-{i+1:02d}.png',j[3866:4326,i*512:(i+1)*512])
for i in range(1,4):save(out/f'shared-cross-{i}.png',j[3756:4436,i*1024-340:i*1024+340])
save(out/'whole-shared-band.png',j[3700:4500])
write(out/'joint-assembly.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'status':'candidate-pending-native-visual-review','formalAccepted':False,'sources':sources,'artifacts':artifacts,'paths':details,'baseNorth':{'assembly':str(nrp),'sha256':sha(nrp),'candidate':str(npth),'candidateSha256':sha(npth)},'baseSouth':{'assembly':str(srp),'sha256':sha(srp),'candidate':str(spth),'candidateSha256':sha(spth)},'script':str(Path(__file__)),'scriptSha256':sha(__file__),'proof':{'pixelCount':8192*4096,'mismatches':0,'contributions':proof},'allPixelsNative':True,'resize':False,'feather':False,'guidePixelsUsed':False,'actualModel':None,'actualQuality':None})
print(json.dumps({'out':str(out),'sources':len(sources),'pixelCount':8192*4096,'mismatches':0}))
