from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p): return {'path':str(p),'sha256':sha(p)}
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,obj):
 assert not Path(p).exists(),str(p)
 Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def save(p,a):
 assert not Path(p).exists(),str(p)
 Image.fromarray(a).save(p)
 return info(p)
def rgb(p): return np.array(Image.open(p).convert('RGB'))
jobs=sys.argv[1:] or ['W01','W02','W03']
P=read(D/jobs[0]/'preparation.json')
for key in ['sourceCandidate','sourceContext','sourceManifest','immutableWestCore']:
 assert sha(P[key]['path'])==P[key]['sha256'],key
base=rgb(P['sourceCandidate']['path']); old_context=rgb(P['sourceContext']['path'])
west=rgb(P['immutableWestCore']['path'])
assert np.array_equal(old_context[115:4211,115:4211],base)
outdir=D/('trial-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+'-'.join(jobs))
outdir.mkdir()
current=base.copy(); prior=P['sourceCandidate']; steps=[]
union=np.zeros((4096,4096),bool)
for index,job in enumerate(jobs,1):
 d=D/job;p=read(d/'preparation.json')
 for key in ['alpha','fullAlpha','savedMask','request','target','unmarkedReference']:
  assert sha(p[key]['path'])==p[key]['sha256'],key
 receipts=list(d.glob('receipt-*.json'));assert len(receipts)==1
 rec=read(receipts[0]);native=rgb(rec['savedNative']['path'])
 assert sha(rec['savedNative']['path'])==rec['savedNative']['sha256'] and native.shape==(1254,1254,3)
 nc=p['nativeCrop']; box=p['pasteBoxIn4096'];x0,y0,x1,y1=box
 cut=native[nc[1]:nc[3],nc[0]:nc[2]]
 a=np.array(Image.open(p['alpha']['path']).convert('L'))
 assert cut.shape[:2]==a.shape==(y1-y0,x1-x0)
 full=np.array(Image.open(p['fullAlpha']['path']).convert('L'))
 assert np.array_equal(full[nc[1]:nc[3],nc[0]:nc[2]],a)
 support=np.zeros((4096,4096),bool);support[y0:y1,x0:x1]=a>0
 assert not np.any(union&support)
 assert np.array_equal(current[support],base[support])
 before=current.copy(); old=before[y0:y1,x0:x1]
 aa=a.astype(np.uint32)[...,None]
 blended=((old.astype(np.uint32)*(255-aa)+cut.astype(np.uint32)*aa+127)//255).astype(np.uint8)
 current[y0:y1,x0:x1]=blended
 assert np.array_equal(current[~support],before[~support])
 # Independent scalar replay: Python integers and byte loop, no vectorized composition.
 replay=before.copy()
 for yy in range(a.shape[0]):
  for xx in range(a.shape[1]):
   av=int(a[yy,xx])
   if av:
    for channel in range(3):
     replay[y0+yy,x0+xx,channel]=(int(before[y0+yy,x0+xx,channel])*(255-av)+int(cut[yy,xx,channel])*av+127)//255
 assert np.array_equal(replay,current)
 union|=support
 sd=outdir/('step%02d-'%index+job);sd.mkdir()
 coreinfo=save(sd/'candidate-4096.png',current)
 context=old_context.copy();context[115:4211,115:4211]=current
 contextinfo=save(sd/'context-4326.png',context)
 assert np.array_equal(context[:115],old_context[:115]) and np.array_equal(context[-115:],old_context[-115:])
 assert np.array_equal(context[:, :115],old_context[:,:115]) and np.array_equal(context[:,-115:],old_context[:,-115:])
 # True-core diagnostic, at original 1:1 pixels.
 origin=p['referencePixelSources'][0]['sourceBox'][1]
 join=np.concatenate((west[origin:origin+1254,3456:4096],current[origin:origin+1254,:614]),axis=1)
 evidence=[]
 def qa(name,b):
  v=save(sd/(name+'.png'),join[b[1]:b[3],b[0]:b[2]])
  v['boxInNativeJoin']=b;v['scale']='1:1';evidence.append(v)
 qa('composed-core-join-1254',[0,0,1254,1254])
 qa('fixed-west-boundary-100pct',[512,max(0,nc[1]-64),896,min(1254,nc[3]+64)])
 qa('top-boundary-100pct',[512,nc[1]-80,min(1254,nc[2]+80),nc[1]+80])
 qa('right-boundary-100pct',[nc[2]-80,nc[1]-64,nc[2]+80,nc[3]+64])
 qa('bottom-boundary-100pct',[512,nc[3]-80,min(1254,nc[2]+80),nc[3]+80])
 for key in ['protectedLeafTipBoxInTarget','protectedRedPaperBoxInTarget']:
  if key in p:
   b=p[key];assert np.array_equal(join[b[1]:b[3],b[0]:b[2]],rgb(p['unmarkedReference']['path'])[b[1]:b[3],b[0]:b[2]])
   qa('protected-object-notch-100pct',[b[0]-64,b[1]-64,b[2]+64,b[3]+64])
 if job=='W01':
  qa('changed-h1024-q0-100pct',[640,1024-origin-256,1254,1024-origin+256])
 changed=np.any(current!=before,axis=2);ys,xs=np.where(changed)
 doc={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'job':job,'status':'trial_pending_visual_qa','published':False,'formalAccepted':False,'previousCandidate':prior,'originalBase':P['sourceCandidate'],'immutableWestCore':P['immutableWestCore'],'sourceReceipt':info(receipts[0]),'preparation':info(d/'preparation.json'),'request':info(d/'request.json'),'actualNative':rec['savedNative'],'nativeCrop':nc,'pasteBoxIn4096':box,'savedAlpha':p['alpha'],'blendArithmetic':p['blendArithmetic'],'sourceGenerationModel':None,'sourceGenerationQuality':None,'RGBColorCorrection':False,'resampling':False,'core':coreinfo,'context':contextinfo,'checks':{'independentScalarReplayExact':True,'outsideSavedAlphaExact':True,'contextOuterHaloUnchanged':True,'priorStepsPreserved':True,'native1254':True,'currentSupportIdenticalToPreparedBase':True,'frozenNW630Unchanged':bool(np.array_equal(current[:630,:630],base[:630,:630])),'westCoreHashUnchanged':sha(P['immutableWestCore']['path'])==P['immutableWestCore']['sha256']},'actualChangedBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changedPixelCount':int(changed.sum()),'evidence':evidence}
 dump(sd/'composition.json',doc);steps.append(info(sd/'composition.json'));prior=coreinfo
summary={'schemaVersion':1,'base':P['sourceCandidate'],'jobs':jobs,'steps':steps,'finalTrial':prior,'published':False,'formalAccepted':False,'networkUsedInComposition':False,'allNativeSourcesRetained':True,'outsideUnionAlphaExact':bool(np.array_equal(current[~union],base[~union]))}
dump(outdir/'trial-index.json',summary)
print(json.dumps({'directory':str(outdir),'index':info(outdir/'trial-index.json'),'finalTrial':prior,'steps':steps}))

