import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
M=read(R/'processed/colorpass/colorpass-report.json')
assert sha(M['originalSelection']['file'])==M['originalSelection']['sha256']
sourceSelection=read(M['originalSelection']['file']);checks=[]
candidate=np.asarray(Image.open(M['candidate']['file']));cover=np.zeros((4096,4096),np.uint8)
for k,rel in sorted(M['patches'].items()):
 out=R/rel;d=read(str(out)+'.derivation.json');inp=Path(d['derivedFrom'][0]['file'])
 assert sha(inp)==d['derivedFrom'][0]['sha256'];a=np.asarray(Image.open(inp),dtype=np.float32)
 fp=Path(d['correctionEvidence']['file']);assert sha(fp)==d['correctionEvidence']['sha256']
 assert sha(d['correctionEvidence']['script'])==d['correctionEvidence']['scriptSha256']
 f=np.load(fp);g=f['additiveGridRgb']
 q=np.clip((np.arange(1254,dtype=np.float32)-115+.5)/16,0,64);lo=np.floor(q).astype(int);hi=np.minimum(lo+1,64);w=q-lo
 top=g[lo[:,None],lo[None,:]]*(1-w[None,:,None])+g[lo[:,None],hi[None,:]]*w[None,:,None]
 bot=g[hi[:,None],lo[None,:]]*(1-w[None,:,None])+g[hi[:,None],hi[None,:]]*w[None,:,None]
 field=(top*(1-w[:,None,None])+bot*w[:,None,None]).astype(np.float32)
 field*=1-f['safetyProtectionY'][:,None,None]*(1-f['safetyWeightX'][None,:,None])
 provisional=a+np.clip(field,-40,40);delta=np.clip(provisional-a,-40,40)
 rebuilt=np.uint8(np.clip(np.rint(a+delta),0,255));actual=np.asarray(Image.open(out))
 assert np.array_equal(rebuilt,actual),k
 assert np.max(np.abs(actual.astype(float)-a))<=40
 coords=np.arange(1024,dtype=float)+.5;yy,xx=np.meshgrid(coords,coords,indexing='ij');dist=np.full((1024,1024),9999.)
 for side in [n[9:] for n in f.files if n.startswith('boundary_')]:
  dist=np.minimum(dist,{'left':xx,'right':1024-xx,'top':yy,'bottom':1024-yy}[side])
 far=dist>=384
 assert np.array_equal(actual[115:1139,115:1139][far],a[115:1139,115:1139][far]),k
 r=int(k[1])-1;c=int(k[2])-1;x=c*1024;y=r*1024
 assert np.array_equal(candidate[y:y+1024,x:x+1024],actual[115:1139,115:1139])
 cover[y:y+1024,x:x+1024]+=1
 checks.append({'patch':k,'source':str(inp),'sourceSha256':sha(inp),'output':str(out),'outputSha256':sha(out),'savedFieldReconstructsExactly':True,'colorDeltaMax':float(np.max(np.abs(actual.astype(float)-a))),'outside384SupportUnchanged':True,'coordinateShift':[0,0],'resampling':False})
jr=read(R/'processed/jointpass/jointpass-report.json');jc=[]
for d in jr['outputs']:
 inp=Path(d['derivedFrom'][0]['file']);j=Path(d['derivedFrom'][1]['file'])
 assert sha(inp)==d['derivedFrom'][0]['sha256'] and sha(j)==d['derivedFrom'][1]['sha256']
 a=np.array(Image.open(inp));joint=np.array(Image.open(j));z=np.load(d['replacementMask']['file']);mask=z['mask'];yy,xx=np.where(mask);a[yy,xx]=joint[z['jointY'][yy],z['jointX'][xx]]
 assert np.array_equal(a,np.array(Image.open(d['file'])))
 jc.append({'output':d['file'],'sha256':sha(d['file']),'savedBinaryMaskReconstructsExactly':True,'outsideMaskByteIdentical':True})
assert cover.min()==cover.max()==1
native=[]
for p in (R/'native').glob('*.generation.json'):
 d=read(p);assert d['actualModel'] is None and d['actualQuality'] is None and d['submittedParameters']=={'model':None,'quality':None}
 assert sha(d['file'])==d['sha256']
 for ref in d['references']:assert sha(ref['path'])==ref['sha256']
 native.append({'file':d['file'],'sha256':d['sha256'],'nativeDimensions':d['nativeDimensions'],'actualModel':None,'actualQuality':None})
report={'tile':'r11_c09','verifiedAt':datetime.now(timezone.utc).isoformat(),'status':'all_processed_pixels_reconstruct_and_provenance_verified','candidateSha256':sha(M['candidate']['file']),'candidateSize':[4096,4096],'sourcePatchCount':16,'coverageMin':int(cover.min()),'coverageMax':int(cover.max()),'selectedCorePixelsExactlyMatch':True,'colorFieldChecks':checks,'jointMaskChecks':jc,'nativeGenerationRecords':native,'nativeImageCount':len(native),'maxActualColorDelta':max(c['colorDeltaMax'] for c in checks),'colorBoundAnchor':'geometry-corrected native-resolution source, not pre-repair geometry pixels','coordinateDisplacement':[0,0],'sourceImageResampling':False,'sourceImageBlur':False,'imagePixelBlending':False,'formalAccepted':False,'modelQualityEvidence':'All builtin generations have actual/submitted model and quality null; configuration target is gpt-image-2.5-sunburst/max only.'}
save(R/'candidate/processed-verification.json',report)
print(json.dumps({k:v for k,v in report.items() if k not in ['colorFieldChecks','jointMaskChecks','nativeGenerationRecords']}))

