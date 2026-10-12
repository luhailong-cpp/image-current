from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;D=T/'repairs/north-halo-audit-20261012';O=D/'linear24-partial';O.mkdir()
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':str(p),'sha256':sha(p)}
def put(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2)
def png(p,a):
 with p.open('xb') as f:Image.fromarray(a).save(f,format='PNG')
m=rd(D/'linear24/composition.json');proof=rd(D/'provenance.json')
for a in [m['baseCandidate'],m['baseContext'],m['alpha'],m['sourceHalo'],proof['selectedNeighbor']]:assert sha(a['path'])==a['sha256']
alpha=np.array(Image.open(m['alpha']['path']));alpha=np.rint(alpha.astype(np.float64)*np.clip((2874-np.arange(4096))/32,0,1)[None,:]).astype(np.uint8)
assert not alpha[:,:630].any() and not alpha[:,2874:].any() and not alpha[24:].any()
base=np.array(Image.open(m['baseCandidate']['path']).convert('RGB'));halo=np.array(Image.open(m['sourceHalo']['path']).convert('RGB'));north=np.array(Image.open(proof['selectedNeighbor']['path']).convert('RGB'));out=base.copy();a=alpha[:,:,None].astype(np.uint32)
out[:115]=((halo.astype(np.uint32)*a+base[:115].astype(np.uint32)*(255-a)+127)//255).astype(np.uint8)
assert np.array_equal(out[:630,:630],base[:630,:630]) and np.array_equal(out[24:],base[24:]) and np.array_equal(out[:24,2874:],base[:24,2874:])
cp=T/'candidate/r14_c14-4k-north-halo-linear24-partial-trial-20261012.png';png(cp,out);cx=np.array(Image.open(m['baseContext']['path']).convert('RGB'));cx[115:4211,115:4211]=out;ctp=T/'candidate/r14_c14-context-north-halo-linear24-partial-trial-20261012.png';png(ctp,cx);png(O/'alpha.png',alpha)
views=[]
for x in [630,1600]:
 im=np.concatenate((north[3456:4096,x:x+1254],out[:614,x:x+1254]));p=O/f'joined-x{x}-1254.png';png(p,im);views.append(art(p))
for x in [630,1024,1490,2048,2842,2874]:
 x0=x-180;x1=x+180;im=np.concatenate((north[3896:,x0:x1],out[:200,x0:x1]));p=O/f'join-endpoint-x{x}-100pct.png';png(p,im);views.append(art(p))
meta={**m,'createdAt':datetime.now(timezone.utc).isoformat(),'status':'partial_trial_pending_visual_qa','alpha':art(O/'alpha.png'),'alphaRule':{'kind':'one-sided-linear','fullAtY':0,'zeroAtY':24,'leftFadeX':[630,662],'rightFadeX':[2842,2874]},'compositor':art(Path(__file__)),'candidate':art(cp),'context':art(ctp),'views':views,'unhandledNorthX':[2874,4096],'unhandledReason':'Far-east ledge/shadow structure does not survive the tested halo-only transitions without a visible shape/shadow issue.','newGenerationCount':0,'formalAccepted':False}
put(O/'composition.json',meta);print(json.dumps({'candidate':meta['candidate'],'manifest':art(O/'composition.json'),'unchangedOutside':[630,0,2874,24]},indent=2))

