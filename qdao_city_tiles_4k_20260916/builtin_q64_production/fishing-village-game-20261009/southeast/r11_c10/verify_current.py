from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
m=read(T/'colorpass-selected.json');before=read(T/'native-selected-before-color.json')
canvas=np.asarray(Image.open(m['candidate']['file']));coverage=np.zeros((4096,4096),np.uint8);checks=[]
def expand(g):
 q=np.clip((np.arange(1254,dtype=np.float32)-115+.5)/16,0,64);lo=np.floor(q).astype(int);hi=np.minimum(lo+1,64);w=q-lo
 a=g[lo[:,None],lo[None,:]]*(1-w[None,:,None])+g[lo[:,None],hi[None,:]]*w[None,:,None]
 b=g[hi[:,None],lo[None,:]]*(1-w[None,:,None])+g[hi[:,None],hi[None,:]]*w[None,:,None]
 return (a*(1-w[:,None,None])+b*w[:,None,None]).astype(np.float32)
for pid,rel in sorted(m['patches'].items()):
 src=T/before['patches'][pid];dest=T/rel;rec=read(str(dest)+'.derivation.json');fieldpath=Path(rec['correctionEvidence']['file']);fd=np.load(fieldpath)
 field=expand(fd['additiveGridRgb'])*(1-fd['safetyProtectionY'][:,None,None]*(1-fd['safetyWeightX'][None,:,None]))
 orig=np.asarray(Image.open(src),dtype=np.float32);out=np.asarray(Image.open(dest))
 rebuilt=np.uint8(np.clip(np.rint(orig+np.clip(field,-40,40)),0,255))
 assert orig.shape==out.shape==(1254,1254,3) and np.array_equal(rebuilt,out)
 assert sha(src)==rec['derivedFrom'][0]['sha256'] and sha(dest)==rec['sha256'] and sha(fieldpath)==rec['correctionEvidence']['sha256']
 y=(int(pid[1])-1)*1024;x=(int(pid[2])-1)*1024
 assert np.array_equal(canvas[y:y+1024,x:x+1024],out[115:1139,115:1139]);coverage[y:y+1024,x:x+1024]+=1
 checks.append({'patch':pid,'source':str(src),'sourceSha256':sha(src),'processed':str(dest),'sha256':sha(dest),'fieldExactlyReproduced':True,'coreExactlyReproduced':True,'maximumChannelChange':float(np.abs(out.astype(float)-orig).max()),'crop':[115,115,1139,1139],'destination':[x,y,x+1024,y+1024],'derivation':str(dest)+'.derivation.json'})
assert coverage.min()==coverage.max()==1 and sha(m['candidate']['file'])==m['candidate']['sha256']
raw=[];missing=[];refchecks=[]
for gp in T.rglob('*.png.generation.json'):
 g=read(gp);p=Path(g['file']);assert sha(p)==g['sha256'] and Image.open(p).size==(1254,1254)
 assert g['actualModel'] is None and g['actualQuality'] is None
 prompt=Path(g['prompt']);assert prompt.exists()
 if 'promptSha256' in g:assert sha(prompt)==g['promptSha256']
 for ref in g['references']:
  rp=Path(ref['path'])
  if not rp.exists():missing.append({'record':str(gp),'path':str(rp),'recordedSha256':ref['sha256'],'status':'historical input missing; preserved source evidence not rewritten'})
  else:
   actual=sha(rp)
   if actual==ref['sha256']:refchecks.append({'path':str(rp),'sha256':actual,'status':'current_exact_match'})
   else:
    snapshot=T/'input-snapshots'/(ref['sha256']+'.png')
    if snapshot.exists() and sha(snapshot)==ref['sha256']:refchecks.append({'path':str(rp),'recordedSha256':ref['sha256'],'snapshot':str(snapshot),'status':'exact_submitted_snapshot'})
    else:refchecks.append({'path':str(rp),'recordedSha256':ref['sha256'],'currentSha256':actual,'status':'historical_reference_changed_original_record_preserved'})
 raw.append({'file':str(p),'sha256':sha(p),'record':str(gp),'nativeDimensions':list(Image.open(p).size),'actualModel':None,'actualQuality':None})
record={'tile':T.name,'candidate':m['candidate'],'sourceCount':16,'nativeGeneratedImageCount':len(raw),'coverageMin':1,'coverageMax':1,'coordinateShift':[0,0],'sourceResampling':False,'sourceImageBlur':False,'sourcePixelBlending':False,'allColorFieldsReconstructed':True,'selectedSourceChecks':checks,'nativeRecords':raw,'historicalMissingReferenceFiles':missing,'referenceChecks':refchecks,'createdAt':datetime.now(timezone.utc).isoformat(),'formalAccepted':False,'internalReady':'pending independent review'}
write(T/'candidate/processed-verification.json',record)
print(json.dumps({'sources':16,'nativeGeneratedImages':len(raw),'coverage':[int(coverage.min()),int(coverage.max())],'historicalMissingRefCount':len(missing),'candidateSha256':m['candidate']['sha256']}))

