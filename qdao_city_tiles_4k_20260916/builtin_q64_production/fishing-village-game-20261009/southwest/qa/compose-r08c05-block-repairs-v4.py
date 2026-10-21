import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
def ref(p):
 p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def png(p,a):
 assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(rgb(p),a);return dict(ref(p),size=[a.shape[1],a.shape[0]])
pre='block2x2-r08r09c05c06-v4';tp=Q/'block2x2-r08r09c05c06-v3-trace.json';t=read(tp);t1=read(Q/'block2x2-r08r09c05c06-v1-trace.json');t2=read(Q/'block2x2-r08r09c05c06-v2-trace.json')
assert ref(t['context']['path'])['sha256']==t['context']['sha256'];assert ref(t1['context']['path'])['sha256']==t1['context']['sha256']
base=rgb(t['context']['path']);original=rgb(t1['context']['path']);out=base.copy()
ids2=np.load(t2['repairSourceIds']['path'],allow_pickle=False);ids3=np.load(t['repairSourceIds']['path'],allow_pickle=False)
mask=np.zeros(base.shape[:2],bool);mask[3590:4844,4460:4824]=True;mask &= (ids2==6)&(ids3==0)
out[mask]=original[mask]
assert np.array_equal(out[~mask],base[~mask]);assert np.array_equal(out[mask],original[mask])
mp=Q/(pre+'-p-background-restore-mask.npy');assert not mp.exists();np.save(mp,mask,allow_pickle=False)
result={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native_four_block_final_pending_visual_qa','baseTrace':ref(tp),'baseContext':t['context'],'restorationSource':t1['context'],'globalContextBox':t['globalContextBox'],'script':ref(__file__),'method':'Restore only original pavement outside p lamp silhouette at local x >= 890; exact native pixel copy, no blend or resampling','restorationMask':ref(mp),'restoredPixelCount':int(mask.sum()),'context':png(Q/(pre+'-context-native.png'),out),'tiles':[],'qa':[],'nativePixelsResampled':False,'sourcePixelIdentity':True,'formalAcceptedCount':0,'validation':{'allFinalPixelsExactlyMatchBaseOrRecordedNativeSource':True,'allSavedPixelsVerified':True}}
for a in t['tiles']:
 l,top,r,bottom=a['contextBox'];cl,ct,cr,cb=a['coreBox'];result['tiles'].append({'tile':a['tile'],'context':png(Q/(pre+'-'+a['tile']+'-context-native.png'),out[top:bottom,l:r]),'contextBox':a['contextBox'],'candidate':png(Q/(pre+'-'+a['tile']+'-candidate-4096.png'),out[ct:cb,cl:cr]),'coreBox':a['coreBox'],'contextUnchangedFromBase':bool(np.array_equal(out[top:bottom,l:r],base[top:bottom,l:r]))})
for a in t['qa']:
 l,top,r,bottom=a['contextBox'];ar=out[top:bottom,l:r];label=a['edge']+('-'+str(a['part']) if a.get('part') is not None else '');result['qa'].append({'edge':a['edge'],'part':a.get('part'),'contextBox':a['contextBox'],'unchangedFromBase':bool(np.array_equal(ar,base[top:bottom,l:r])),**png(Q/(pre+'-'+label+'-100pct.png'),ar)})
result['pSurround']=png(Q/(pre+'-p-surround-100pct.png'),out[3510:4924,3490:4904])
p=Q/(pre+'-trace.json')
with p.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,ensure_ascii=False)
print(json.dumps({'trace':ref(p),'tiles':result['tiles'],'changedQa':[a['path'] for a in result['qa'] if not a['unchangedFromBase']]}))
