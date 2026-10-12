import json, hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
O=R/'processed/jointpass-20261012-v1';O.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def path(cost):
 n,h=cost.shape;dp=cost[0].copy();back=np.zeros((n,h),np.int16)
 for i in range(1,n):
  padded=np.pad(dp,(1,1),constant_values=1e12)
  options=np.stack([padded[:h]+.35,padded[1:h+1],padded[2:]+.35])
  choices=options.argmin(0);back[i]=choices-1
  dp=cost[i]+options[choices,np.arange(h)]
 result=np.empty(n,np.int16);result[-1]=dp.argmin()
 for i in range(n-1,0,-1):result[i-1]=result[i]+back[i,result[i]]
 return result
selection=read(R/'selected-patches.json')
save(O/'input-selection.json',selection)
baseCanvas=np.asarray(Image.open(R/'qa/full-resume-20261012-v1/candidate-4096.png')).copy()
arrays={pid:np.array(Image.open(R/rel)) for pid,rel in selection['patches'].items()}
originals={pid:a.copy() for pid,a in arrays.items()}
unionMasks={pid:np.zeros((1254,1254),bool) for pid in arrays}
jointRecords=[]; perPatchJoints={pid:[] for pid in arrays}
specs=[
 ('canopy-cross-r2-c2-v1',(1421,1421),(330,460),(950,1080),(48,145),(1100,1206),(510,700,600,960)),
 ('ridge-cross-r3-c3-v2',(2445,2445),(345,445),(790,890),(48,130),(1020,1140),(600,665,130,700))
]
for stem,origin,tr,br,lr,rr,required in specs:
 source=R/'repairs'/f'{stem}.png';target=R/'repairs'/('ridge-cross-r3-c3-v1-input.png' if 'ridge' in stem else f'{stem}-input.png')
 base=np.asarray(Image.open(target));joint=np.asarray(Image.open(source))
 assert base.shape==joint.shape==(1254,1254,3)
 dif=np.abs(base.astype(float)-joint.astype(float)).mean(2)
 top=path(dif[tr[0]:tr[1],:].T)+tr[0];bottom=path(dif[br[0]:br[1],:].T)+br[0]
 left=path(dif[:,lr[0]:lr[1]])+lr[0];right=path(dif[:,rr[0]:rr[1]])+rr[0]
 yy,xx=np.indices((1254,1254))
 mask=(yy>=top[None,:])&(yy<bottom[None,:])&(xx>=left[:,None])&(xx<right[:,None])
 y0,y1,x0,x1=required;assert mask[y0:y1,x0:x1].all()
 assert not mask[:48].any() and not mask[-48:].any() and not mask[:,:48].any() and not mask[:,-48:].any()
 mf=O/f'{stem}-adoption-mask.npz';np.savez_compressed(mf,mask=mask,top=top,bottom=bottom,left=left,right=right)
 combined=base.copy();combined[mask]=joint[mask]
 Image.fromarray(combined).save(O/f'{stem}-adopted-native-1254.png')
 outline=mask&~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
 vis=combined.copy();vis[outline]=[255,0,255]
 Image.fromarray(vis).save(O/f'{stem}-cut-outline-QA.png')
 record={'joint':stem,'source':str(source),'sourceSha256':sha(source),'generationRecord':str(source)+'.generation.json','generationRecordSha256':sha(str(source)+'.generation.json'),'target':str(target),'targetSha256':sha(target),'tileCropOrigin':list(origin),'adoptionMask':str(mf),'adoptionMaskSha256':sha(mf),'pixelCount':int(mask.sum()),'boundaryRgbMeanAbsoluteDifference':float(dif[outline].mean()),'boundaryRgb90thPercentile':float(np.percentile(dif[outline],90)),'operation':'unscaled exact native AI pixels through binary low-difference cut; no blending, blur, warp or resampling'}
 jointRecords.append(record)
 for pid,a in arrays.items():
  row,col=int(pid[1])-1,int(pid[2])-1;ox,oy=col*1024-115,row*1024-115
  jx=ox+np.arange(1254)-origin[0];jy=oy+np.arange(1254)-origin[1]
  vx=(jx>=0)&(jx<1254);vy=(jy>=0)&(jy<1254)
  local=np.zeros((1254,1254),bool);local[np.ix_(vy,vx)]=mask[np.ix_(jy[vy],jx[vx])]
  if not local.any():continue
  sy,sx=np.where(local);a[sy,sx]=joint[jy[sy],jx[sx]]
  unionMasks[pid]|=local;perPatchJoints[pid].append(record)
outputs=[]
for pid,a in arrays.items():
 if not unionMasks[pid].any():continue
 originalPath=R/selection['patches'][pid];destination=O/f'{pid}-jointpass-v1.png'
 Image.fromarray(a).save(destination)
 mf=O/f'{pid}-replacement-mask.npz';np.savez_compressed(mf,mask=unionMasks[pid])
 assert np.array_equal(a[~unionMasks[pid]],originals[pid][~unionMasks[pid]])
 record={'file':str(destination),'sha256':sha(destination),'dimensions':[1254,1254],'operation':'unscaled exact coordinate copy of native AI joint pixels through binary material cuts','originalSource':{'file':str(originalPath),'sha256':sha(originalPath),'generationRecord':str(originalPath)+'.generation.json'},'jointSources':perPatchJoints[pid],'replacementMask':{'file':str(mf),'sha256':sha(mf),'array':'mask'},'replacementPixelCount':int(unionMasks[pid].sum()),'outsideMaskByteIdentical':True,'coordinateShift':[0,0],'resampling':False,'imageBlur':False,'imagePixelBlending':False,'actualModel':None,'actualQuality':None,'formalAccepted':False}
 save(str(destination)+'.derivation.json',record);outputs.append(record)
 selection['patches'][pid]=str(destination.relative_to(R)).replace('\\','/')
selection.update(status='native_joint_candidate_pending_boundary_QA',internalReady=False,formalAccepted=False)
save(O/'selected-patches.json',selection)
canvas=np.zeros((4096,4096,3),np.uint8)
for pid,a in arrays.items():
 r,c=int(pid[1])-1,int(pid[2])-1;canvas[r*1024:(r+1)*1024,c*1024:(c+1)*1024]=a[115:1139,115:1139]
candidate=O/'candidate-4096.png';Image.fromarray(canvas).save(candidate)
Image.fromarray(canvas).resize((1024,1024),Image.Resampling.LANCZOS).save(O/'preview-QA-1024.png')
for stem,origin,*_ in specs:
 box=(*origin,origin[0]+1254,origin[1]+1254);Image.fromarray(canvas).crop(box).save(O/f'{stem}-assembled-after-native.png')
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'pending_boundary_visual_QA','tile':'r09_c09','inputCandidateSha256':sha(R/'qa/full-resume-20261012-v1/candidate-4096.png'),'candidate':str(candidate),'candidateSha256':sha(candidate),'selection':str(O/'selected-patches.json'),'joints':jointRecords,'outputs':outputs,'script':str(Path(__file__)),'scriptSha256':sha(__file__),'coordinateShift':[0,0],'resampling':False,'imageBlur':False,'imagePixelBlending':False,'formalAccepted':False}
save(O/'jointpass-report.json',report)
print(json.dumps({'candidate':str(candidate),'sha256':sha(candidate),'changedPatches':[p for p in arrays if unionMasks[p].any()],'joints':[{k:v for k,v in j.items() if k in ['joint','pixelCount','boundaryRgbMeanAbsoluteDifference','boundaryRgb90thPercentile']} for j in jointRecords]}))

