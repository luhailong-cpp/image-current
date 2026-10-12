import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
m=read(R/'processed/colorpass/colorpass-report.json');raw=read(R/'native-selected-before-color.json');now=datetime.now(timezone.utc).isoformat()
def expand(g):
 q=np.clip((np.arange(1254,dtype=np.float32)-115+.5)/16,0,64)
 lo=np.floor(q).astype(int);hi=np.minimum(lo+1,64);w=q-lo
 a=g[lo[:,None],lo[None,:]]*(1-w[None,:,None])+g[lo[:,None],hi[None,:]]*w[None,:,None]
 b=g[hi[:,None],lo[None,:]]*(1-w[None,:,None])+g[hi[:,None],hi[None,:]]*w[None,:,None]
 return (a*(1-w[:,None,None])+b*w[:,None,None]).astype(np.float32)
canvas=np.array(Image.open(m['candidate']['file']));checks=[];coverage=np.zeros((4096,4096),dtype=np.uint8)
for pid,rel in sorted(m['patches'].items()):
 src=R/raw['patches'][pid];dest=R/rel;rec=read(str(dest)+'.derivation.json')
 fieldpath=Path(rec['correctionEvidence']['file']);fieldfile=np.load(fieldpath)
 field=expand(fieldfile['additiveGridRgb'])*(1-fieldfile['safetyProtectionY'][:,None,None]*(1-fieldfile['safetyWeightX'][None,:,None]))
 orig=np.asarray(Image.open(src),dtype=np.float32);rebuilt=np.uint8(np.clip(np.rint(orig+np.clip(field,-40,40)),0,255));out=np.array(Image.open(dest))
 assert np.array_equal(rebuilt,out) and sha(dest)==rec['sha256'] and sha(src)==rec['derivedFrom'][0]['sha256'] and sha(fieldpath)==rec['correctionEvidence']['sha256']
 y=(int(pid[1])-1)*1024;x=(int(pid[2])-1)*1024
 assert np.array_equal(canvas[y:y+1024,x:x+1024],out[115:1139,115:1139])
 coverage[y:y+1024,x:x+1024]+=1
 checks.append({'patch':pid,'source':str(src),'sourceSha256':sha(src),'processed':str(dest),'sha256':sha(dest),'fieldExactlyReproduced':True,'coreExactlyReproduced':True,'maximumChannelChange':float(np.abs(out.astype(float)-orig).max()),'crop':[115,115,1139,1139],'destination':[x,y,x+1024,y+1024],'derivation':str(dest)+'.derivation.json'})
assert coverage.min()==coverage.max()==1
dest=R/'candidate/r12_c09-internal-ready-4096.png';shutil.copy2(m['candidate']['file'],dest)
ver={'tile':R.name,'candidate':str(dest),'candidateSha256':sha(dest),'dimensions':[4096,4096],'nativeSize':[1254,1254],'sourceCount':16,'coverageMin':1,'coverageMax':1,'coordinateShift':[0,0],'sourceResampling':False,'sourceImageBlur':False,'sourcePixelBlending':False,'allCorrectionFieldsReconstructed':True,'checks':checks,'createdAt':now}
write(R/'candidate/processed-verification.json',ver)
review={'tile':R.name,'status':'internal_ready_external_pending','internalReady':True,'formalAccepted':False,'reviewer':'south_col09 production agent','candidate':str(dest),'candidateSha256':sha(dest),'nativeSeamsInspected':24,'nativeCrossingsInspected':9,'completePreviewInspected':True,'beforeAndAfterColorInspected':True,'geometryBlockingFindings':[],'colorBlockingFindings':[],'colorSummary':{'robustBefore':3.876736119389534,'robustAfter':.7747395820915699,'maximumChannelChange':16,'resize':False,'blur':False,'pixelBlending':False},'observations':['Rail horizontal beams and stone wall courses remain continuous across cuts.','Dock post and deck have no visible geometry step.','Rock contours, crevices, foliage and foam remain continuous; low-frequency boundary brightness offsets corrected.'],'externalSeams':'north raw source boundary independent review passed; final color selection needs refresh, other exterior edges pending neighbors','provenanceLimitation':'12 historical references use missing old style PNG. Original prompt/request/receipt/source hashes preserved and verified; new 4 generations use present contract JPG. No historic hashes rewritten.','records':{'nativeAudit':str(R/'candidate/provenance-audit.json'),'processedVerification':str(R/'candidate/processed-verification.json'),'colorpass':str(R/'processed/colorpass/colorpass-report.json')},'reviewedAt':now}
write(R/'qa/internal-review.json',review)
sel={'tile':R.name,'patches':m['patches'],'status':'internal_ready_external_pending','internalReady':True,'formalAccepted':False,'candidate':str(dest),'candidateSha256':sha(dest),'internalReview':str(R/'qa/internal-review.json'),'processedVerification':str(R/'candidate/processed-verification.json'),'updatedAt':now}
write(R/'selected-patches.json',sel)
write(R/'candidate/internal-ready-manifest.json',{'tile':R.name,'candidate':str(dest),'candidateSha256':sha(dest),'status':sel['status'],'internalReady':True,'formalAccepted':False,'dimensions':[4096,4096],'sources':checks,'verification':str(R/'candidate/processed-verification.json'),'review':str(R/'qa/internal-review.json'),'sourceOperation':'16 unscaled1024 cores from1254 native derivatives with saved bounded low-frequency RGB fields','actualModel':None,'actualQuality':None})
write(str(dest)+'.derivation.json',read(R/'candidate/internal-ready-manifest.json'))
write(R/'progress.json',{'tile':R.name,'status':sel['status'],'generatedNativeCount':17,'usableNativeCount':16,'selectedPatchCount':16,'complete4kCandidateCount':1,'internalReady4kCount':1,'formalAcceptedCount':0,'remainingPositions':[],'candidate':str(dest),'candidateSha256':sha(dest),'geometryBlockingIssues':[],'colorBlockingIssues':[],'updatedAt':now})
print(json.dumps({'tile':R.name,'internalReady':True,'candidate':str(dest),'sha256':sha(dest),'coverage':[int(coverage.min()),int(coverage.max())],'allFieldsExactlyReconstructed':True}))

