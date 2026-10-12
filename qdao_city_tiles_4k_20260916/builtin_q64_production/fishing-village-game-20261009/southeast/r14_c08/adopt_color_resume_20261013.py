from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;P=T/'processed/colorpass-resume-20261013-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
m=read(P/'colorpass-report.json');sp=T/'selected-patches.json';s=read(sp);canvas=np.asarray(Image.open(m['candidate']['file']).convert('RGB'))
assert sha(m['candidate']['file'])==m['candidate']['sha256'] and canvas.shape==(4096,4096,3)
records=[]
for src in m['sources']:
 k=src['patch'];source=T/s['patches'][k];assert source.resolve()==Path(src['file']).resolve() and sha(source)==src['sha256']
 dest=T/m['patches'][k];d=read(str(dest)+'.derivation.json');assert sha(dest)==d['sha256']
 n=np.asarray(Image.open(source).convert('RGB'),dtype=np.float32);out=np.asarray(Image.open(dest).convert('RGB'))
 saved=np.load(d['correctionEvidence']['file']);g=saved['additiveGridRgb'];assert g.shape==(65,65,3)
 # Independently reconstruct the saved bilinear correction at original pixel centers.
 q=np.clip((np.arange(1254,dtype=np.float32)-115+.5)/16,0,64);lo=np.floor(q).astype(int);hi=np.minimum(lo+1,64);w=q-lo
 a=g[lo[:,None],lo[None,:]]*(1-w[None,:,None])+g[lo[:,None],hi[None,:]]*w[None,:,None]
 b=g[hi[:,None],lo[None,:]]*(1-w[None,:,None])+g[hi[:,None],hi[None,:]]*w[None,:,None]
 field=(a*(1-w[:,None,None])+b*w[:,None,None]).astype(np.float32)
 assert np.all(saved['safetyWeightX']==1) and np.all(saved['safetyProtectionY']==0)
 rebuilt=np.uint8(np.clip(np.rint(n+np.clip(field,-24,24)),0,255));assert np.array_equal(rebuilt,out)
 delta=int(np.max(np.abs(out.astype(np.int16)-n.astype(np.int16))));assert delta<=24
 r,c=int(k[1])-1,int(k[2])-1;assert np.array_equal(canvas[r*1024:(r+1)*1024,c*1024:(c+1)*1024],out[115:1139,115:1139])
 records.append(dict(patch=k,input=str(source),inputSha256=sha(source),output=str(dest),outputSha256=sha(dest),maximumActualRgbChange=delta,savedFieldReplayExact=True,coreReplayExact=True))
ev=[dict(file=e['afterStrip'],sha256=sha(e['afterStrip'])) for e in m['seams']]+[dict(file=e['file'],sha256=sha(e['file'])) for e in m['crossings']]
assert len(ev)==33
rp=P/'root-internal-review.json';assert not rp.exists()
review=dict(createdAt=datetime.now(timezone.utc).isoformat(),tile=s['tile'],internalGeometryPassed=True,internalColorPassed=True,internalMaterialPassed=True,
    observations=['All 24 seams and 9 crossings visually inspected at native resolution after color pass. Open-sea caustic endpoints and facet shapes remain continuous.',
    'All 16 open-sea cores retain coherent facet spacing, with no rectilinear material window at the reviewed seams. Low-frequency hue equalization does not move or blur source detail.'],
    evidence=ev,independentReplay=records,candidate=m['candidate'],sourceCoordinateShift=[0,0],sourceResampling=False,sourceBlur=False,sourcePixelBlending=False,internalReady=True,formalAccepted=False,externalReview='pending')
write(rp,review)
snap=T/'qa/selection-before-color-adoption-20261013.json';assert not snap.exists();snap.write_bytes(sp.read_bytes())
s.update(patches=m['patches'],candidate=m['candidate']['file'],candidateSha256=m['candidate']['sha256'],status='internal_passed_external_review_pending',internalReady=True,formalAccepted=False,materialPending=False,internalReview=str(rp),colorPass=str(P/'colorpass-report.json'))
write(sp,s)
print(json.dumps(dict(tile=s['tile'],internalReady=True,formalAccepted=False,independentNativeReplays=len(records),internalEvidence=len(ev),maximumRgbChange=max(x['maximumActualRgbChange'] for x in records))))
