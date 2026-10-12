from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
from datetime import datetime,timezone
D=Path(__file__).resolve().parent
BASE=D.parents[1]
sys.path.insert(0,str(BASE/'pipeline-tools'))
from quilt import minimum_seam,feather_mask,blend_exact
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size)}
original=np.array(Image.open(D/'M01.input.png').convert('RGB'))
native=np.array(Image.open(D/'M01.native.png').convert('RGB'))
assert original.shape==native.shape==(1254,1254,3)
roi=(350,330,1110,500)
x0,y0,x1,y1=roi
old=original[y0:y1,x0:x1]
new=native[y0:y1,x0:x1]
h,w=old.shape[:2]
alpha=np.full((h,w),255,dtype=np.uint8)
left=feather_mask(minimum_seam(old[:,:110],new[:,:110]),110,2)
right=255-feather_mask(minimum_seam(old[:,-110:],new[:,-110:]),110,2)
top=feather_mask(minimum_seam(old[:22].transpose(1,0,2),new[:22].transpose(1,0,2)),22,2).T
bottom=255-feather_mask(minimum_seam(old[-20:].transpose(1,0,2),new[-20:].transpose(1,0,2)),20,2).T
alpha[:,:110]=np.minimum(alpha[:,:110],left)
alpha[:,-110:]=np.minimum(alpha[:,-110:],right)
alpha[:22]=np.minimum(alpha[:22],top)
alpha[-20:]=np.minimum(alpha[-20:],bottom)
patch=blend_exact(old,new,alpha)
Image.fromarray(patch).save(D/'M01.preblended.patch.png')
Image.fromarray(alpha).save(D/'M01.alpha.png')
Image.fromarray(np.uint8(alpha>0)*255).save(D/'M01.paste-mask.png')
applied=original.copy();applied[y0:y1,x0:x1]=patch
Image.fromarray(applied).save(D/'M01.applied-crop.png')
Image.fromarray(applied[330:495,450:960]).save(D/'M01.applied-detail.png')
core_roi=[2400+x0,650+y0,2400+x1,650+y1]
source=BASE/'r11_c05/refinement-resume20261010/integrated-v2/r11_c05.repaired-v2.candidate.png'
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'id':'M01','sourceCandidate':info(source),'sourceInput':info(D/'M01.input.png'),'inputCoreBox':[2400,650,3654,1904],'native':info(D/'M01.native.png'),'receipt':str(D/'M01.receipt.json'),'receiptSha256':sha(D/'M01.receipt.json'),'actualModel':None,'actualQuality':None,'nativeCropBox':list(roi),'coreBox':core_roi,'contextBox':[v+115 for v in core_roi],'patch':info(D/'M01.preblended.patch.png'),'pasteMask':info(D/'M01.paste-mask.png'),'alpha':info(D/'M01.alpha.png'),'featherRadiusPixels':2,'activePixels':int((alpha>0).sum()),'outsideRoiExact':bool(np.array_equal(applied[:y0],original[:y0]) and np.array_equal(applied[y1:],original[y1:]) and np.array_equal(applied[:,:x0],original[:,:x0]) and np.array_equal(applied[:,x1:],original[:,x1:])),'localVisualPassed':None,'internalPassed':False,'formalAccepted':False}
(D/'M01.overlay-proposal.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'coreBox':core_roi,'activePixels':record['activePixels'],'outsideRoiExact':record['outsideRoiExact']}))
