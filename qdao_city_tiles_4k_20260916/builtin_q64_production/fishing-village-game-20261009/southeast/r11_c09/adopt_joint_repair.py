import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from datetime import datetime,timezone
R=Path(__file__).resolve().parent; O=R/'processed/jointpass';O.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
basepath=R/'layout-only/joint-p32-p33-native-crop.png';jointpath=R/'native/joint-p32-p33-v1.png'
base=np.asarray(Image.open(basepath));joint=np.asarray(Image.open(jointpath)); dif=np.abs(base.astype(float)-joint.astype(float)).mean(2)
# Follow low-difference hard cuts through stable surrounding material. No feathering or mixing.
def path(cost):
 n,h=cost.shape;dp=cost[0].copy();back=np.zeros((n,h),np.int16)
 for i in range(1,n):
  padded=np.pad(dp,(1,1),constant_values=1e12)
  a=np.stack([padded[:h]+.35,padded[1:h+1],padded[2:]+.35])
  choices=a.argmin(0);back[i]=choices-1
  dp=cost[i]+a[choices,np.arange(h)]
 out=np.empty(n,np.int16);out[-1]=dp.argmin()
 for i in range(n-1,0,-1):out[i-1]=out[i]+back[i,out[i]]
 return out
top=path(dif[340:391,:].T)+340
bottom=path(dif[920:1001,:].T)+920
left=path(dif[:,48:97])+48
right=path(dif[:,920:1001])+920
yy,xx=np.indices((1254,1254))
mask=(yy>=top[None,:])&(yy<bottom[None,:])&(xx>=left[:,None])&(xx<right[:,None])
assert mask[550:700,420:730].all()
assert not mask[:48].any() and not mask[-48:].any() and not mask[:,:48].any() and not mask[:,-48:].any()
np.savez_compressed(O/'adoption-mask.npz',mask=mask,top=top,bottom=bottom,left=left,right=right)
combined=base.copy();combined[mask]=joint[mask]
Image.fromarray(combined).save(O/'joint-adoption-native-1254.png')
outline=mask & ~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
perim=dif[outline]
vis=combined.copy();vis[outline]=[255,0,255];Image.fromarray(vis).save(O/'adoption-boundary-QA.png')
selection=read(R/'selected-patches.json'); originalSelection=json.loads(json.dumps(selection))
# Existing sixteen direct native sources are recorded immutably before derivative selection.
save(O/'input-selection.json',originalSelection)
cropOrigin=(1421,1741); outputrecords=[]
for pid in ['p32','p33']:
 src=R/selection['patches'][pid];a=np.array(Image.open(src));old=a.copy()
 r=int(pid[1])-1;c=int(pid[2])-1;ox=c*1024-115;oy=r*1024-115
 gx=ox+np.arange(1254);gy=oy+np.arange(1254);jx=gx-cropOrigin[0];jy=gy-cropOrigin[1]
 validx=(jx>=0)&(jx<1254);validy=(jy>=0)&(jy<1254)
 localmask=np.zeros((1254,1254),bool)
 localmask[np.ix_(validy,validx)]=mask[np.ix_(jy[validy],jx[validx])]
 sy,sx=np.where(localmask);a[sy,sx]=joint[jy[sy],jx[sx]]
 dest=O/(pid+'-jointpass.png');Image.fromarray(a).save(dest)
 maskfile=O/(pid+'-replacement-mask.npz');np.savez_compressed(maskfile,mask=localmask,jointX=jx,jointY=jy)
 assert np.array_equal(a[~localmask],old[~localmask])
 record={'file':str(dest),'sha256':sha(dest),'dimensions':[1254,1254],'operation':'unscaled exact coordinate copy of native joint AI pixels through a binary low-difference material cut; no alpha mixing','derivedFrom':[{'file':str(src),'sha256':sha(src),'record':str(src)+'.generation.json','role':'original selected native pixels outside adoption mask'},{'file':str(jointpath),'sha256':sha(jointpath),'record':str(jointpath)+'.generation.json','role':'AI-repaired pixels inside adoption mask'}],'replacementMask':{'file':str(maskfile),'sha256':sha(maskfile),'array':'mask'},'jointCropOriginTile':list(cropOrigin),'patchNativeOriginTile':[ox,oy],'replacementPixelCount':int(localmask.sum()),'outsideMaskByteIdentical':True,'coordinateShift':[0,0],'resampling':False,'imageBlur':False,'imagePixelBlending':False,'formalAccepted':False}
 save(str(dest)+'.derivation.json',record);outputrecords.append(record);selection['patches'][pid]=str(dest.relative_to(R))
selection['status']='joint_geometry_candidate_pending_native_review';selection['formalAccepted']=False
save(O/'selected-patches.json',selection)
canvas=np.zeros((4096,4096,3),np.uint8)
for pid,rel in selection['patches'].items():
 a=np.array(Image.open(R/rel));r=int(pid[1])-1;c=int(pid[2])-1;canvas[r*1024:(r+1)*1024,c*1024:(c+1)*1024]=a[115:1139,115:1139]
candidate=O/'r11_c09-jointpass-candidate-4096.png';Image.fromarray(canvas).save(candidate)
Image.fromarray(canvas).crop((1920,2048,2176,3072)).save(O/'p32-p33-after-native.png')
Image.fromarray(canvas).crop((1421,1741,2675,2995)).save(O/'joint-region-after-native.png')
Image.fromarray(canvas).resize((1024,1024),Image.Resampling.LANCZOS).save(O/'preview-1024.png')
bbox=[int(xx[mask].min()),int(yy[mask].min()),int(xx[mask].max()+1),int(yy[mask].max()+1)]
report={'status':'joint_geometry_candidate_pending_native_review','sourceCandidateSha256':read(R/'candidate/manifest.json')['candidateSha256'],'jointSource':str(jointpath),'jointSha256':sha(jointpath),'adoptionBoxNative':bbox,'adoptionPixelCount':int(mask.sum()),'adoptionMask':str(O/'adoption-mask.npz'),'adoptionMaskSha256':sha(O/'adoption-mask.npz'),'jointNativeSize':[1254,1254],'selection':str(O/'selected-patches.json'),'candidate':str(candidate),'candidateSha256':sha(candidate),'outputs':outputrecords,'boundaryRgbMeanAbsoluteDifference':float(perim.mean()),'boundaryRgb90thPercentile':float(np.percentile(perim,90)),'coordinateShift':[0,0],'resampling':False,'pixelBlending':False,'formalAccepted':False,'leftHullEdgeYAtX0_64_128':{'original':[439,476,511],'jointV1':[439,476,511]},'script':str(Path(__file__)),'scriptSha256':sha(__file__)}
save(O/'jointpass-report.json',report)
print(json.dumps({k:v for k,v in report.items() if k!='outputs'}))

