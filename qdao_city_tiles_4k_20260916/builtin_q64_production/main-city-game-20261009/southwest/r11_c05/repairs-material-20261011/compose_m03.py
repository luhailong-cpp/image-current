from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
from datetime import datetime,timezone
D=Path(__file__).resolve().parent
BASE=D.parents[1]
sys.path.insert(0,str(BASE/'pipeline-tools'))
from quilt import blend_exact
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size)}
old=np.array(Image.open(D/'M03.input.png').convert('RGB'))
new=np.array(Image.open(D/'M03.native.png').convert('RGB'))
assert old.shape==new.shape==(1254,1254,3)
roi=(503,495,573,536)
x0,y0,x1,y1=roi
h,w=y1-y0,x1-x0
yy,xx=np.indices((h,w))
distance=np.minimum.reduce([yy,xx,h-1-yy,w-1-xx])
alpha=np.uint8(np.clip(distance/2,0,1)*255)
patch=blend_exact(old[y0:y1,x0:x1],new[y0:y1,x0:x1],alpha)
Image.fromarray(patch).save(D/'M03.preblended.patch.png')
Image.fromarray(alpha).save(D/'M03.alpha.png')
Image.fromarray(np.uint8(alpha>0)*255).save(D/'M03.paste-mask.png')
applied=old.copy();applied[y0:y1,x0:x1]=patch
Image.fromarray(applied).save(D/'M03.applied-crop.png')
Image.fromarray(applied[450:580,450:675]).save(D/'M03.applied-detail.png')
core_roi=[1600+x0,1650+y0,1600+x1,1650+y1]
source=BASE/'r11_c05/refinement-resume20261010/integrated-v2/r11_c05.repaired-v2.candidate.png'
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'id':'M03','sourceCandidate':info(source),'sourceInput':info(D/'M03.input.png'),'inputCoreBox':[1600,1650,2854,2904],'native':info(D/'M03.native.png'),'receipt':str(D/'M03.receipt.json'),'receiptSha256':sha(D/'M03.receipt.json'),'actualModel':None,'actualQuality':None,'nativeCropBox':list(roi),'coreBox':core_roi,'contextBox':[v+115 for v in core_roi],'patch':info(D/'M03.preblended.patch.png'),'pasteMask':info(D/'M03.paste-mask.png'),'alpha':info(D/'M03.alpha.png'),'featherRadiusPixels':2,'activePixels':int((alpha>0).sum()),'outsideRoiExact':bool(np.array_equal(applied[:y0],old[:y0]) and np.array_equal(applied[y1:],old[y1:]) and np.array_equal(applied[:,:x0],old[:,:x0]) and np.array_equal(applied[:,x1:],old[:,x1:])),'localVisualPassed':None,'internalPassed':False,'formalAccepted':False}
(D/'M03.overlay-proposal.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'coreBox':core_roi,'activePixels':record['activePixels'],'outsideRoiExact':record['outsideRoiExact']}))
