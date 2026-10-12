"""Partial mechanical research only; final full-height seam waits for complete right tile."""
from pathlib import Path
import json,hashlib,sys,importlib.util
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parent.parent;N=R/'work-r04_c03/joint-north'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(p):
 p=Path(p);return p if p.is_absolute() else R/p
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('hard',R/'assemble_r03_c03.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
j=read(N/'joint-assembly.json');rightrecord=R/'work-r04_c04/tiles/r04_c04.first-three-rows.assembly.json';p=read(rightrecord)
registry=j['sources'].copy();arrays={}
for s in registry:
 assert sha(s['file'])==s['sha256'];arrays[s['jointSourceId']]=np.asarray(Image.open(s['file']).convert('RGB'))
for e in p['sources']:
 f=path(e['file']);g=read(path(e['generationRecord']));sid=e['sourceId']+35;assert sha(f)==e['sha256']
 registry.append({'jointSourceId':sid,'tile':'r04_c04','tileSourceId':e['sourceId'],'file':str(f),'sha256':sha(f),'globalNativeBox':g['globalNativeBox']});arrays[sid]=np.asarray(Image.open(f).convert('RGB'))
def row(tile,y):
 es=sorted([s for s in registry if s['tile']==tile and s['globalNativeBox'][1]==y],key=lambda s:s['globalNativeBox'][0]);assert len(es)==4
 a=arrays[es[0]['jointSourceId']].copy();ids=np.full((1254,1254),es[0]['jointSourceId'],np.uint8)
 for s in es[1:]:a,ids,_=h.append_hard(a,ids,arrays[s['jointSourceId']],np.full((1254,1254),s['jointSourceId'],np.uint8),'row')
 return a,ids
def full(tile,n):
 a,ids=row(tile,12173)
 for rr in range(1,n):
  b,bi=row(tile,12173+rr*1024);t,ti,_=h.append_hard(a.transpose(1,0,2),ids.T,b.transpose(1,0,2),bi.T,'stack');a=t.transpose(1,0,2);ids=ti.T
 return a,ids
left,li=full('r04_c03',4);right,ri=full('r04_c04',3)
north,ni=row('r03_c03',11149);northcut=np.array(read(N/'joint-path.json')['fullPathGlobalYByX'])-12173
take=np.arange(230)[:,None]>=northcut[None,:]
left[:230]=np.where(take[:,:,None],left[:230],north[1024:1254]);li[:230]=np.where(take,li[:230],ni[1024:1254])
assert np.array_equal(left[115:4211,115:4211],np.asarray(Image.open(N/'r04_c03.joint-proposal.png')))
assert np.array_equal(right[115:3187,115:4211],np.asarray(Image.open(p['candidate'])))
a=left[:3302,4096:4326];b=right[:,:230]
diff=a.astype(np.int32)-b.astype(np.int32);cost=np.sum(diff*diff,axis=2,dtype=np.int64)
# Preserve the entire previous SW top115px proposal; its north pair must not be invalidated.
inf=np.int64(1<<40);cost[:230,:115]=inf
back=np.zeros(cost.shape,np.int8);prev=cost[0].copy();offsets=np.array([0,-1,1],np.int8)
for y in range(1,len(cost)):
 candidates=np.stack((prev,np.r_[inf,prev[:-1]],np.r_[prev[1:],inf]));choice=np.argmin(candidates,axis=0);back[y]=offsets[choice];prev=cost[y]+candidates[choice,np.arange(230)]
cut=np.empty(3302,np.int32);cut[-1]=np.argmin(prev)
for y in range(3301,0,-1):cut[y-1]=cut[y]+back[y,cut[y]]
assert np.all(cut[:230]>=115) and np.all(np.abs(np.diff(cut))<=1)
take=np.arange(230)[None,:]>=cut[:,None];band=np.where(take[:,:,None],b,a);ids=np.where(take,ri[:,:230],li[:3302,4096:4326])
newleft=left[115:3187,115:4211].copy();newright=right[115:3187,115:4211].copy();newleft[:,-115:]=band[115:3187,:115];newright[:,:115]=band[115:3187,115:]
assert np.array_equal(newleft[:115],left[115:230,115:4211])
before=np.concatenate((left[115:3187,4211-320:4211],right[115:3187,115:435]),axis=1);after=np.concatenate((newleft[:,-320:],newright[:,:320]),axis=1)
Image.fromarray(before).save(D/'study-first3-before-100pct.png');Image.fromarray(after).save(D/'study-first3-after-100pct.png');Image.fromarray(band).save(D/'study-first3-native-band.png');Image.fromarray(ids).save(D/'study-first3-native-band-source-id.png')
for i in range(6):Image.fromarray(after[i*512:(i+1)*512]).save(D/f'study-first3-after-segment-{i+1}.png')
count=0
for s in registry:
 yy,xx=np.nonzero(ids==s['jointSourceId'])
 if not len(xx):continue
 bx,by,_,_=s['globalNativeBox'];assert np.array_equal(band[yy,xx],arrays[s['jointSourceId']][yy+12173-by,xx+12173-bx]);count+=len(xx)
assert count==3302*230
record={'status':'partial-first3-research-not-final-proposal','finalCandidatesWritten':False,'rightInput':{'file':str(rightrecord),'sha256':sha(rightrecord)},'northJointManifest':{'file':str(N/'joint-assembly.json'),'sha256':sha(N/'joint-assembly.json')},'globalNativeOverlapBox':[12173,12173,12403,15475],'pathGlobalXByY':(12173+cut).tolist(),'maximumStep':int(np.abs(np.diff(cut)).max()),'cornerConstraint':{'globalY':[12173,12403],'globalXMinimum':12288,'purpose':'Preserve previous joint-north SW top115px exactly; do not overwrite earlier shared north path.'},'pixelProvenanceVerified':count,'sources':registry,'blend':False,'resample':False,'geometryMoved':False,'limitations':['Right fourth row omitted: final full-height path must be recomputed after native bridge and complete4K assembly.','NE tile has no complete candidate; full four-tile corner acceptance remains pending.','Bottom blue net corner is structurally wrong in v01/v02: no hard cut is allowed to claim it fixed.'],'artifacts':[{'file':str(f),'sha256':sha(f)} for f in sorted(D.glob('study-first3-*.png'))]}
write(D/'study-first3.json',record);print(json.dumps({'status':record['status'],'verifiedPixels':count,'pathRange':[int(cut.min()+12173),int(cut.max()+12173)]}))
