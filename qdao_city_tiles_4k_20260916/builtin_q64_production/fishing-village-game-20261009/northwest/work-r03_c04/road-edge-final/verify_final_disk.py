from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
W=Path(__file__).resolve().parent;D=W/'final-candidate';B=W.parents[1]
rd=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rgb=lambda p:np.array(Image.open(p).convert('RGB'))
m=rd(D/'assembly.json');checks=[];sourceChecks=[]
for s in m['sources']:
 assert sha(s['file'])==s['sha256'];gen=rd(s['generationRecord']);assert sha(s['generationRecord'])==s['generationRecordSha256'];assert gen['sha256']==s['sha256'];assert gen['globalNativeBox']==s['globalNativeBox']
 if s['sourceId']>=46:
  assert gen['actualModel'] is None and gen['actualQuality'] is None and not gen['nativeScaleResampled'];req=rd(gen['evidence']['request']);assert req['prompt'].strip()==Path(gen['prompt']).read_text(encoding='utf-8-sig').strip();assert req['globalNativeBox']==s['globalNativeBox']
  for ref in gen['references']:assert sha(ref['file'])==ref['sha256']
 sourceChecks.append(dict(sourceId=s['sourceId'],sha256=s['sha256'],generationSha256=s['generationRecordSha256'],verified=True))
for art in m['artifacts']:
 assert sha(art['file'])==art['sha256'];assert sha(art['sourceIdMap']['file'])==art['sourceIdMap']['sha256'];a=rgb(art['file']);i=np.array(Image.open(art['sourceIdMap']['file']));assert a.shape==(4096,4096,3) and i.shape==(4096,4096);assert 0 not in np.unique(i);total=0;parts=[]
 for s in m['sources']:
  yy,xx=np.nonzero(i==s['sourceId'])
  if not len(xx):continue
  r=rgb(s['file']);sx=xx+art['globalBox'][0]-s['globalNativeBox'][0];sy=yy+art['globalBox'][1]-s['globalNativeBox'][1];assert sx.min()>=0 and sy.min()>=0 and sx.max()<1254 and sy.max()<1254;diff=int(np.count_nonzero(np.any(a[yy,xx]!=r[sy,sx],axis=1)));assert diff==0;parts.append(dict(sourceId=s['sourceId'],pixels=len(xx),mismatches=diff));total+=len(xx)
 assert total==16777216;old=rgb(art['base']['file']);change=np.any(a!=old,axis=2);yy,xx=np.nonzero(change);assert np.array_equal(change,np.array(Image.open(art['changedMask']['file']))>0);checks.append(dict(tile=art['tile'],pixels=total,mismatches=0,sha256=art['sha256'],changedPixels=len(xx),changedGlobalBox=[int(xx.min())+art['globalBox'][0],int(yy.min())+art['globalBox'][1],int(xx.max()+1)+art['globalBox'][0],int(yy.max()+1)+art['globalBox'][1]],contributions=parts))
n=rgb(m['artifacts'][0]['file']);s=rgb(m['artifacts'][1]['file']);ni=np.array(Image.open(m['artifacts'][0]['sourceIdMap']['file']));si=np.array(Image.open(m['artifacts'][1]['sourceIdMap']['file']));exit=[]
for gy,row,ids in [(12287,n[-1],ni[-1]),(12288,s[0],si[0]),(12289,s[1],si[1])]:
 v=row.astype('int16');xx=np.flatnonzero((v[:,2]-v[:,0]>8)&(v[:,2]-v[:,1]>3)&(v[:,0]>140));xx=xx[xx+12288>16000];x=int(xx.min())+12288;assert (16250<=x<=16350) if gy==12288 else (16245<=x<=16355);exit.append(dict(globalY=gy,firstBlueFaceX=x,sourceIds=sorted(map(int,np.unique(ids[x-12288:])))))
# Fish body and main tassel visible pixels, reported separately from source replay.
old=rgb(m['artifacts'][0]['base']['file']);propChecks=[]
for name,box in [('fish_body',[15100,9900,16384,10960]),('tassel',[15640,10975,15775,11370])]:
 x,y,x1,y1=box;aa=n[y-8192:y1-8192,x-12288:x1-12288];bb=old[y-8192:y1-8192,x-12288:x1-12288];v=bb.astype('int16');sel=(v[:,:,0]>v[:,:,2]+65)&(v[:,:,0]>v[:,:,1]+25)&(v[:,:,0]>100);propChecks.append(dict(name=name,globalBox=box,objectPixels=int(sel.sum()),changedObjectPixels=int(np.count_nonzero(np.any(aa[sel]!=bb[sel],axis=1)))))
proof=dict(checkedAt=datetime.now(timezone.utc).isoformat(),method='independent fresh disk read: each PNG hash, each source ID, global native coordinate bounds, every output RGB pixel, generation record/reference hashes, changed masks',totalPixels=sum(q['pixels'] for q in checks),mismatches=0,artifacts=checks,sources=sourceChecks,roadExit=exit,propPixelDiagnostics=propChecks,noResampling=True,noFeathering=True,noProceduralFinalPainting=True)
(D/'independent-replay.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items() if k not in ['sources','artifacts']}));print(json.dumps([{'tile':q['tile'],'changedGlobalBox':q['changedGlobalBox'],'changedPixels':q['changedPixels']} for q in checks]))
