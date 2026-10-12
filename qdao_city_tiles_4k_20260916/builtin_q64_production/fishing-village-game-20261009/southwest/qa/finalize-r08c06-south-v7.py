import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1];Q=Z/'qa';prefix='r08c06-south-final-v7'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def arr(p):return np.array(Image.open(p).convert('RGB'))
def out(n,a):
 p=Q/(prefix+'-'+n+'.png');assert not p.exists();Image.fromarray(a).save(p);return ref(p)
t=rd(Q/'r08c06-south-final-v6-trace.json')
n=arr(Q/'pair-r08c06-r09c06-v5-r08_c06-context-native.png')
w=arr(Path(t['r09_c06']['context']['path']))
l=arr(Q/'r08c06-south-v5-rebased-r09_c06-context-native.png');l[:,:230]=w[:,:230]
r=arr(Q/'block2x2-r09r10c06c07-v2-r09_c07-context-native.png')
old=np.array(rd(Q/'pair-r09c06-c07-northupdate-v1-trace.json')['hardSeamPathIn230Overlap'])
a=l[:501,-230:].astype(np.float64);b=r[:501,:230].astype(np.float64)
c=np.mean((a-b)**2,axis=2)
cost=np.empty((501,231));cost[:,:230]=c;cost[:,230]=c[:,-1]
dp=np.full(231,np.inf);dp[230]=cost[0,230];bt=np.zeros((501,231),np.int8)
for y in range(1,501):
 cand=np.stack([np.r_[np.inf,dp[:-1]],dp,np.r_[dp[1:],np.inf]])
 choices=np.argmin(cand,axis=0);bt[y]=choices-1;dp=cost[y]+cand[choices,np.arange(231)]
seam=old.copy();seam[500]=old[500]
for y in range(500,0,-1):seam[y-1]=seam[y]+bt[y,seam[y]]
assert seam[0]==230
mask=np.arange(230)[None,:]<seam[:,None]
over=np.where(mask[:,:,None],l[:,-230:],r[:,:230])
lc=l.copy();rc=r.copy();lc[:,-230:]=over;rc[:,:230]=over
n[4096:]=lc[:230]
c5=arr(Path(t['r09_c05']['context']['path']))
assert np.array_equal(c5[:,-230:],lc[:,:230])
assert np.array_equal(lc[:,-230:],rc[:,:230])
assert np.array_equal(n[-230:],lc[:230])
report={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'candidate_pending_visual_qa','method':'230-pixel exact-source hard seam, top boundary fixed to left source; dynamic programming rows 0..500 and existing approved path below; no interpolation','sourcePixelIdentity':True,'nativePixelsResampled':False,'sourceInputs':[ref(Q/'r08c06-south-v5-rebased-r09_c06-context-native.png'),t['r09_c06']['context'],ref(Q/'block2x2-r09r10c06c07-v2-r09_c07-context-native.png'),ref(Q/'pair-r08c06-r09c06-v5-r08_c06-context-native.png')],'hardSeamPath':seam.tolist(),'r09_c05':t['r09_c05'],'sourceTrace':ref(Q/'r08c06-south-final-v6-trace.json'),'qa':[]}
for tile,img in [('r08_c06',n),('r09_c06',lc),('r09_c07',rc)]:
 report[tile]={'context':out(tile+'-context-native',img),'candidate':out(tile+'-candidate-4096',img[115:4211,115:4211])}
joint=np.concatenate([n[:4096],lc])
report['qa'].append(out('south-shared-part05-100pct',joint[3866:4556,3311:4211]))
ejoint=np.concatenate([lc[:,:4096],rc],axis=1)
report['qa'].append(out('east-shared-top-halo-100pct',ejoint[:900,3866:4556]))
report['qa'].append(out('north-south-corner-100pct',joint[3645:4545,3636:4326]))
for tile,img,base in [('r09_c06',lc,arr(Q/'block2x2-r09r10c06c07-v2-r09_c06-context-native.png')),('r09_c07',rc,r)]:
 d=np.any(img!=base,axis=2);ys,xs=np.where(d);report[tile]['changes']={'count':int(d.sum()),'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'rows751DownExactUnchanged':bool(np.array_equal(img[751:],base[751:])),'coreExactUnchanged':bool(np.array_equal(img[115:4211,115:4211],base[115:4211,115:4211]))}
p=Q/(prefix+'-trace.json');assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'trace':ref(p),'seamFirst15':seam[:15].tolist(),'outputs':{k:report[k] for k in ['r08_c06','r09_c06','r09_c07']}}))

