"""Finite color matching only after geometric QA; no warping or resampling."""
from pathlib import Path
from PIL import Image
import numpy as np
import json,hashlib
from datetime import datetime,timezone
z=Path(__file__).resolve().parent;t=z/'r10_c09'
a=t/'native/p11-v1.png';b=t/'native/p12-v3.png'
aa=np.asarray(Image.open(a).convert('RGB'),dtype=np.float32)
bb=np.asarray(Image.open(b).convert('RGB'),dtype=np.float32)
# Robust native-overlap color difference at actual midpoint seam.
delta=np.median(bb[:,95:135]-aa[:,1119:1159],axis=1)
kernel=np.exp(-0.5*(np.arange(-32,33)/8)**2);kernel/=kernel.sum()
field=np.clip(np.stack([np.convolve(np.pad(delta[:,c],(32,32),mode='edge'),kernel,mode='valid') for c in range(3)],axis=1),-40,40)
x=np.arange(1254,dtype=np.float32)
q=np.clip((x-115)/(500-115),0,1)
weight=1-(q*q*(3-2*q))
correction=field[:,None,:]*weight[None,:,None]
out=np.uint8(np.clip(np.rint(bb-correction),0,255))
dest=t/'processed/p12-v3-color-match.png';dest.parent.mkdir(exist_ok=True)
Image.fromarray(out).save(dest)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record={'file':str(dest),'sha256':sha(dest),'createdAt':datetime.now(timezone.utc).isoformat(),'classification':'derived native-detail candidate, not a new model generation','dimensions':[1254,1254],'operation':'bounded additive per-channel local color correction from robust overlap statistics','derivedFrom':[{'file':str(b),'sha256':sha(b),'generationRecord':str(b)+'.generation.json'},{'file':str(a),'sha256':sha(a),'role':'color anchor; no source pixels copied'}],'geometryReview':'Main stone edges aligned within0-1px; no coordinate shift needed','pixelResampling':False,'geometryWarp':False,'imageBlending':False,'coordinateShift':[0,0],'maximumChannelCorrection':float(np.max(np.abs(correction))),'medianDifferenceSampleX':[95,135],'heightSmoothingSigma':8,'fullCorrectionUntilX':115,'zeroCorrectionFromX':500,'fieldRowsRgb':field.tolist(),'xWeights':weight.tolist(),'acceptance':'pending100percentReview'}
dest.with_suffix('.png.derivation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
pair=Image.new('RGB',(2278,1254));pair.paste(Image.fromarray(np.uint8(aa)).crop((0,0,1139,1254)),(0,0));pair.paste(Image.fromarray(out).crop((115,0,1254,1254)),(1139,0))
qa=t/'qa/p11-v1-p12-color-match-join-100pct.png';pair.crop((883,0,1395,1254)).save(qa)
print(json.dumps({'file':str(dest),'qa':str(qa),'maxCorrection':record['maximumChannelCorrection'],'seamMeanStepBefore':float(np.mean(np.abs(aa[1100:1200,1138]-bb[1100:1200,115]))),'seamMeanStepAfter':float(np.mean(np.abs(aa[1100:1200,1138]-out[1100:1200,115])))},indent=2))
