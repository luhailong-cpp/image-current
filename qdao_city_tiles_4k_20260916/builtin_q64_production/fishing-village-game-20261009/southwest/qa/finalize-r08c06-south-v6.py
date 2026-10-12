import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
q=Path(__file__).resolve().parent
ref=lambda p:{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
rgb=lambda p:np.array(Image.open(p).convert('RGB'))
pre='r08c06-south-final-v6'
n=q/'pair-r08c06-r09c06-v5-r08_c06-context-native.png';s=q/'pair-r09c05-c06-northupdate-v1-r09_c06-context-native.png';w=q/'pair-r09c05-c06-northupdate-v1-r09_c05-context-native.png';e=q/'pair-r09c06-c07-northupdate-v1-r09_c07-context-native.png'
na,sa,wa,ea=[rgb(p) for p in (n,s,w,e)]
assert np.array_equal(wa[:,-230:],sa[:,:230]);assert np.array_equal(sa[:,-230:],ea[:,:230])
out=np.concatenate([na[:4096],sa],axis=0);north=out[:4326].copy()
assert np.array_equal(north[:4096],na[:4096]);assert np.array_equal(north[4096:],sa[:230])
def png(name,ar):
 p=q/(pre+'-'+name+'.png');assert not p.exists();Image.fromarray(ar).save(p);assert np.array_equal(rgb(p),ar);return dict(ref(p),size=[ar.shape[1],ar.shape[0]])
ctx=png('joint-context-native',out);nc=png('r08_c06-context-native',north);core=png('r08_c06-candidate-4096',north[115:4211,115:4211])
qa=[]
for i,x in enumerate([0,800,1600,2400,3196],1):
 b=[115+x,3866,1015+x,4556];l,t,r,bo=b;qa.append(dict(png('south-shared-part%02d-100pct'%i,out[t:bo,l:r]),contextBox=b))
views=[]
asm=rd(q/'full-tile-r08_c06-assembly.json')
for tile,after,before in [('r08_c06',north,rgb(q/'repair-r08_c06-internal-v5-context-native.png')),('r09_c06',sa,rgb(q/'block2x2-r09r10c06c07-v2-r09_c06-context-native.png'))]:
 for old in asm['qa']:
  box=old['sourceBox'];l,t,r,b=box;newa=after[t+115:b+115,l+115:r+115];olda=before[t+115:b+115,l+115:r+115]
  if np.array_equal(newa,olda):continue
  suffix=Path(old['file']).name.replace('full-tile-r08_c06-','')
  views.append(dict(png(tile+'-'+suffix.removesuffix('.png'),newa),tile=tile,coreBox=box))
checks={}
for tile,p,arr,base in [('r09_c05',w,wa,q/'block2x2-r09r10c05c06-v1-r09_c05-context-native.png'),('r09_c06',s,sa,q/'block2x2-r09r10c06c07-v2-r09_c06-context-native.png'),('r09_c07',e,ea,q/'block2x2-r09r10c06c07-v2-r09_c07-context-native.png')]:
 old=rgb(base);m=np.any(old!=arr,axis=2);ys,xs=np.where(m);checks[tile]={'base':ref(base),'context':ref(p),'changedPixels':int(m.sum()),'changedContextBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if m.any() else None,'rows751DownExactUnchanged':np.array_equal(old[751:],arr[751:])}
t={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'final_propagated_candidate_pending_final_visual_qa','context':ctx,'r08_c06':{'context':nc,'candidate':core},'r09_c05':{'context':ref(w),'candidate':ref(q/'pair-r09c05-c06-northupdate-v1-r09_c05-candidate-4096.png')},'r09_c06':{'context':ref(s),'candidate':ref(q/'pair-r09c05-c06-northupdate-v1-r09_c06-candidate-4096.png')},'r09_c07':{'context':ref(e),'candidate':ref(q/'pair-r09c06-c07-northupdate-v1-r09_c07-candidate-4096.png')},'sourceSelection':{'jointRows0To4095':ref(n),'jointRows4096To8421':ref(s),'northernContextRows4096To4325':'exact southern context rows 0..229; propagate resolved east/west corner pixels'},'sourceIdentityVerified':True,'noResampling':True,'allThree230OverlapPairsExact':True,'inputChanges':checks,'qa':qa,'affectedInternalQa':views,'provenance':[ref(q/'repair-r08_c06-internal-v5-internal-qa.json'),ref(q/'pair-r08c06-r09c06-v5-trace.json'),ref(q/'r08c06-south-v5-rebased-r09_c06-trace.json'),ref(q/'pair-r09c06-c07-northupdate-v1-trace.json'),ref(q/'pair-r09c05-c06-northupdate-v1-trace.json')]}
tp=q/(pre+'-trace.json');assert not tp.exists();tp.write_text(json.dumps(t,indent=2),encoding='utf-8')
print(json.dumps({'trace':ref(tp),'affectedInternalQa':views,'inputChanges':checks,'northContext':nc,'northCandidate':core}))

