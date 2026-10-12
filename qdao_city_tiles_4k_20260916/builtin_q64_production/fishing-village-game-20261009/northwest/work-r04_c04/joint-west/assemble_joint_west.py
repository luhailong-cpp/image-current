"""Two-tile native composition, frozen north corner plus global bridge ownership."""
from pathlib import Path
import json,hashlib,sys,importlib.util
from datetime import datetime,timezone
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parent.parent;N=R/'work-r04_c03/joint-north'
D=D/'trial-bottom-cut';D.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(p):
 p=Path(p);return p if p.is_absolute() else R/p
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def art(p):return {'file':str(p),'sha256':sha(p)}
def save(p,a):Image.fromarray(a).save(p)
spec=importlib.util.spec_from_file_location('hard',R/'assemble_r03_c03.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
spec=importlib.util.spec_from_file_location('rep',R/'apply_r03_c03_repairs.py');rep=importlib.util.module_from_spec(spec);spec.loader.exec_module(rep)
j=read(N/'joint-assembly.json');rr=R/'work-r04_c04/tiles/r04_c04.repair-v2.assembly.json';rightrec=read(rr)
assert rightrec['sha256']=='8ce33727f0ff9641e47004c1eeb454e51d2062a5024cf4517adb2041d2e774a4'
registry=j['sources'].copy();arrays={}
inputs=[art(N/'joint-assembly.json'),art(N/'joint-path.json'),art(N/'r04_c03.joint-proposal.png'),art(rr),art(Path(rightrec['candidate'])),art(Path(rightrec['sourceIdMap']))]
for s in registry:
 assert sha(s['file'])==s['sha256'] and sha(s['generationRecord'])==s['generationRecordSha256'];arrays[s['jointSourceId']]=np.asarray(Image.open(s['file']).convert('RGB'))
for e in rightrec['sources']:
 f=path(e['file']);rp=path(e['generationRecord']);g=read(rp);sid=e['sourceId']+35
 assert sha(f)==e['sha256'] and sha(rp)==e['generationRecordSha256']
 registry.append({'jointSourceId':sid,'tile':'r04_c04','tileSourceId':e['sourceId'],'file':str(f),'sha256':sha(f),'generationRecord':str(rp),'generationRecordSha256':sha(rp),'globalNativeBox':g['globalNativeBox'],'actualModel':g['actualModel'],'actualQuality':g['actualQuality'],'nativeScaleResampled':False});arrays[sid]=np.asarray(Image.open(f).convert('RGB'))
assert len(rightrec['sources'])==17
def row(tile,y):
 es=sorted([s for s in registry if s['tile']==tile and s['globalNativeBox'][1]==y],key=lambda s:s['globalNativeBox'][0]);assert len(es)==4
 a=arrays[es[0]['jointSourceId']].copy();ids=np.full((1254,1254),es[0]['jointSourceId'],np.uint8)
 for s in es[1:]:a,ids,_=h.append_hard(a,ids,arrays[s['jointSourceId']],np.full((1254,1254),s['jointSourceId'],np.uint8),'row')
 return a,ids
def full(tile):
 a,ids=row(tile,12173)
 for rr in range(1,4):
  b,bi=row(tile,12173+rr*1024);t,ti,_=h.append_hard(a.transpose(1,0,2),ids.T,b.transpose(1,0,2),bi.T,'stack');a=t.transpose(1,0,2);ids=ti.T
 return a,ids
left,li=full('r04_c03');right,ri=full('r04_c04')
north,ni=row('r03_c03',11149);northcut=np.array(read(N/'joint-path.json')['fullPathGlobalYByX'])-12173
take=np.arange(230)[:,None]>=northcut[None,:]
left[:230]=np.where(take[:,:,None],left[:230],north[1024:1254]);li[:230]=np.where(take,li[:230],ni[1024:1254])
assert np.array_equal(left[115:4211,115:4211],np.asarray(Image.open(N/'r04_c03.joint-proposal.png')))
right[115:4211,115:4211]=np.asarray(Image.open(rightrec['candidate']))
ri[115:4211,115:4211]=np.asarray(Image.open(rightrec['sourceIdMap']))+35
a=left[:,4096:4326];b=right[:,:230];diff=a.astype(np.int32)-b.astype(np.int32);cost=np.sum(diff*diff,axis=2,dtype=np.int64)
bounds=np.zeros(4326,np.int32);bounds[:230]=115;cut,total=rep.minimum_path(cost,0,229,bounds)
take=np.arange(230)[None,:]>=cut[:,None];band=np.where(take[:,:,None],b,a);ids=np.where(take,ri[:,:230],li[:,4096:4326])
oldleft=left[115:4211,115:4211];oldright=right[115:4211,115:4211];newleft=oldleft.copy();newright=oldright.copy();nli=li[115:4211,115:4211].copy();nri=ri[115:4211,115:4211].copy()
newleft[:,-115:]=band[115:4211,:115];newright[:,:115]=band[115:4211,115:];nli[:,-115:]=ids[115:4211,:115];nri[:,:115]=ids[115:4211,115:]
assert np.array_equal(newleft[:115],oldleft[:115])
combined=np.concatenate((newleft,newright),axis=1);owners=np.concatenate((nli,nri),axis=1)
bridge=R/'native/r04_c03_c04_blue_net_corner_bridge_v01.png';brp=Path(str(bridge)+'.generation.json');g=read(brp)
assert sha(bridge)=='f528de594e3b7d92e94ae6c22d6bff4477266ac1b3b458e4a55d553baf97edc6'==g['sha256']
box=g['globalNativeBox'];assert box==[11648,15104,12902,16358]
ba=np.asarray(Image.open(bridge).convert('RGB'));assert ba.shape==(1254,1254,3)
sid=53;arrays[sid]=ba;registry.append({'jointSourceId':sid,'tile':'global-cross-tile-bridge','file':str(bridge),'sha256':sha(bridge),'generationRecord':str(brp),'generationRecordSha256':sha(brp),'globalNativeBox':box,'actualModel':g['actualModel'],'actualQuality':g['actualQuality'],'nativeScaleResampled':False})
x0,y0=box[0]-8192,box[1]-12288;region=combined[y0:y0+1254,x0:x0+1254];base_region=region.copy()
constraints=[{'xStart':430,'xEndExclusive':1030,'minY':1250,'reason':'Diagnostic attempt to keep whole bridge mesh below old disconnected bottom cuts.'}]
mask,bridgepaths=rep.overlay_mask(region,ba,constraints)
yy,xx=np.indices((1254,1254));protected=(xx+box[0]>=12865)&(yy+box[1]<15389)
mask&=~protected
assert mask[115:1139,115:1139].all()
bridgepaths['protectedOtherBridgeCore']={'globalBox':[12865,14365,13889,15389],'rule':'Blue-corner mask excluded from existing root support-bridge core; own core unaffected.'}
region[mask]=ba[mask];owners[y0:y0+1254,x0:x0+1254][mask]=sid
assert np.array_equal(region[~mask],base_region[~mask])
assert np.array_equal(combined[:115,:4096],oldleft[:115])
verify=[];count=0
for s in registry:
 yy,xx=np.nonzero(owners==s['jointSourceId'])
 if not len(xx):continue
 bx,by,_,_=s['globalNativeBox'];sx=xx+8192-bx;sy=yy+12288-by
 assert np.all((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254));assert np.array_equal(combined[yy,xx],arrays[s['jointSourceId']][sy,sx]);count+=len(xx)
 verify.append({'jointSourceId':s['jointSourceId'],'pixels':len(xx)})
assert count==2*4096*4096
for tile,sl in [('r04_c03',slice(0,4096)),('r04_c04',slice(4096,8192))]:save(D/f'{tile}.joint-west-proposal.png',combined[:,sl]);save(D/f'{tile}.joint-west-source-id.png',owners[:,sl])
save(D/'blue-bridge-ownership-mask.png',mask.astype(np.uint8)*255);save(D/'blue-bridge-applied-100pct.png',region)
before=np.concatenate((oldleft[:,-320:],oldright[:,:320]),axis=1);after=combined[:,4096-320:4096+320]
save(D/'west-boundary-before-100pct.png',before);save(D/'west-boundary-after-100pct.png',after)
for i in range(8):save(D/f'west-after-segment-{i+1:02d}.png',after[i*512:(i+1)*512])
for rr in range(1,4):save(D/f'west-cross-{rr}.png',after[rr*1024-230:rr*1024+230])
def crop_global(b):
 b=[max(b[0],8192),max(b[1],12288),min(b[2],16384),min(b[3],16384)]
 return combined[b[1]-12288:b[3]-12288,b[0]-8192:b[2]-8192],b
diagnostics=[]
for label,b in [('west',[box[0]-200,box[1],box[0]+200,box[3]]),('east',[box[2]-200,box[1],box[2]+200,box[3]]),('north',[box[0],box[1]-200,box[2],box[1]+200]),('south',[box[0],box[3]-230,box[2],box[3]+200])]:
 a,bb=crop_global(b);f=D/f'blue-bridge-{label}-100pct.png';save(f,a);diagnostics.append({'side':label,'file':str(f),'globalBox':bb,'size':[a.shape[1],a.shape[0]],'unscaled':True})
pathrec={'globalNativeOverlapBox':[12173,12173,12403,16499],'pathGlobalXByY':(12173+cut).tolist(),'samePathForBothTiles':True,'cornerConstraint':{'y':[12173,12403],'minimumCutX':12288,'preservesEntireSouthwestNorth115':True},'costSumSquaredRGB':total,'bridgeGlobalBox':box,'bridgeMask':art(D/'blue-bridge-ownership-mask.png'),'bridgePaths':bridgepaths,'bridgeRule':'One shared global source ownership mask before splitting at x12288','bridgePixels':int(mask.sum()),'resample':False,'blend':False}
write(D/'joint-west-path-and-bridge.json',pathrec)
for e in inputs:assert sha(e['file'])==e['sha256']
out={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'two-tile-proposals-pending-west-and-bridge-visual-QA','formalAccepted':False,'originalCandidatesModified':False,'inputs':inputs,'sources':registry,'proposalPixelsVerified':count,'contributions':verify,'northCornerPreserved':True,'sameGlobalBridgeMaskBothTiles':True,'algorithm':art(R/'assemble_r03_c03.py'),'repairAlgorithm':art(R/'apply_r03_c03_repairs.py'),'script':art(Path(__file__)),'pathAndBridge':art(D/'joint-west-path-and-bridge.json'),'bridgeEdgeCrops':diagnostics,'knownSeparateRightInternalDefect':'Main left post-to-blue-net detached rope awaiting separate root bridge; unrelated to shared west boundary.','artifacts':[art(f) for f in sorted(D.glob('*.png')) if f.name.startswith(('r04_','west-','blue-bridge-'))]}
write(D/'joint-west-assembly.json',out)
print(json.dumps({'manifest':art(D/'joint-west-assembly.json'),'verifiedPixels':count,'bridgePixels':int(mask.sum()),'northCornerPreserved':True}))
