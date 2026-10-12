from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib,shutil
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;R=D.parent.parent;B=D/'lower-v2';O=D/'final-v3';O.mkdir(exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'file':str(p),'sha256':sha(p)}
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def path(v):
 p=Path(v);return p if p.is_absolute() else R/p
m=read(B/'joint-assembly.json');r6p=R/'work-r04_c04/tiles/r04_c04.repair-v6.assembly.json';r6=read(r6p);r2=read(R/'work-r04_c04/tiles/r04_c04.repair-v2.assembly.json')
assert sha(r6['candidate'])==r6['sha256']=='b766f7b9b168fd3ce7a88d8f66b8528b7e89c6adb556cecee56581337229f296'
v6=np.asarray(Image.open(r6['candidate']).convert('RGB'));v2=np.asarray(Image.open(r2['candidate']).convert('RGB'));i6=np.asarray(Image.open(r6['sourceIdMap']))
im=np.asarray(Image.open(B/'r04_c04.joint-proposal.png')).copy();ids=np.asarray(Image.open(B/'r04_c04.source-id.png')).copy()
take=i6>=18;yy,xx=np.nonzero(take);assert len(xx) and int(xx.min()+12288)>=14300
assert np.array_equal(v6[~take],v2[~take])
assert not np.isin(ids[take],[53,58,59]).any()
old=im.copy();im[take]=v6[take];ids[take]=i6[take]+42
assert np.array_equal(im[:,:14300-12288],old[:,:14300-12288])
registry=m['sources'].copy()
for s in r6['sources']:
 if s['sourceId']<=17:continue
 p=path(s['file']);rp=path(s['generationRecord']);g=read(rp);assert sha(p)==s['sha256'];assert sha(rp)==s['generationRecordSha256']
 registry.append({'jointSourceId':s['sourceId']+42,'tile':'r04_c04','tileSourceId':s['sourceId'],'file':str(p),'sha256':sha(p),'generationRecord':str(rp),'generationRecordSha256':sha(rp),'globalNativeBox':g['globalNativeBox'],'actualModel':g['actualModel'],'actualQuality':g['actualQuality'],'nativeScaleResampled':False})
assert len(registry)==62
Image.fromarray(im).save(O/'r04_c04.joint-proposal.png');Image.fromarray(ids).save(O/'r04_c04.source-id.png')
for n in ['r04_c03.joint-proposal.png','r04_c03.source-id.png','r05_c03.first-row.joint-proposal.png','r05_c03.first-row.source-id.png']:shutil.copy2(B/n,O/n)
outputs=[]
for e in m['artifacts']:
 ee=dict(e);p=O/Path(e['file']).name;ip=O/Path(e['sourceIdMap']['file']).name
 ee['file']=str(p);ee['sha256']=sha(p);ee['sourceIdMap']=art(ip);outputs.append(ee)
# Reopen every final PNG and native PNG, verify exact unchanged integer-coordinate contributions.
arr={s['jointSourceId']:np.asarray(Image.open(s['file']).convert('RGB')) for s in registry};reg={s['jointSourceId']:s for s in registry}
proof=[];count=0
for e in outputs:
 p=Path(e['file']);a=np.asarray(Image.open(p).convert('RGB'));ii=np.asarray(Image.open(e['sourceIdMap']['file']));bx,by,x2,y2=e['globalBox']
 assert a.shape==(y2-by,x2-bx,3) and (ii>0).all();counts=[]
 for sid in np.unique(ii):
  yy,xx=np.nonzero(ii==sid);b=reg[int(sid)]['globalNativeBox'];sx=xx+bx-b[0];sy=yy+by-b[1]
  assert ((sx>=0)&(sx<1254)&(sy>=0)&(sy<1254)).all();assert np.array_equal(a[yy,xx],arr[sid][sy,sx]);counts.append({'sourceId':int(sid),'pixels':len(xx)})
 proof.append({'file':str(p),'size':[a.shape[1],a.shape[0]],'verifiedPixels':ii.size,'mismatchedPixels':0,'contributions':counts});count+=ii.size
assert count==37748736
mech={'status':'pass','declaredOutputPixelsVerified':count,'mismatchedPixels':0,'uncoveredPixels':0,'resampledPixels':0,'blendedPixels':0,'guidePixelsUsed':0,'outputs':proof,'v6Rebase':{'input':art(r6p),'pixelMask':'v6 source-id>=18','newGlobalJointIds':[60,61,62],'changedPixels':int(take.sum()),'minGlobalX':int(np.nonzero(take)[1].min()+12288),'sharedWestAndSouthNetCropsUnchanged':True,'originalSupportCorePreserved':True},'previousMechanicalCheck':art(B/'mechanical-check.json'),'finalCandidateOriginalsUnmodified':True}
write(O/'mechanical-check.json',mech)
out={'createdAt':datetime.now(timezone.utc).isoformat(),'status':'joint-proposals-pass-shared-boundaries-await-root-review','formalAccepted':False,'sources':registry,'artifacts':outputs,'baseJointAssembly':art(B/'joint-assembly.json'),'rightV6Assembly':art(r6p),'rightV6Candidate':art(Path(r6['candidate'])),'script':art(Path(__file__)),'mechanicalCheck':art(O/'mechanical-check.json'),'paths':m['paths'],'diagnostics':m['diagnostics'],'sharedQAUnchangedUnderV6':True,'jointNorthCornerPreserved':True,'supportCorePreserved':True,'supportHaloChanges':read(B/'mechanical-check.json')['supportBridge'],'originalCandidatesModified':False,'originalIndicesModified':False,'resample':False,'feather':False,'actualModel':None,'actualQuality':None,'pending':['r04c04 north border with r03c04','future r05c04 beyond present native bridge and east/south surroundings','full r05c03 not produced; supplied first row remains partial']}
write(O/'joint-assembly.json',out)
print(json.dumps({'manifest':art(O/'joint-assembly.json'),'mechanical':art(O/'mechanical-check.json'),'outputs':outputs,'verified':count}))

