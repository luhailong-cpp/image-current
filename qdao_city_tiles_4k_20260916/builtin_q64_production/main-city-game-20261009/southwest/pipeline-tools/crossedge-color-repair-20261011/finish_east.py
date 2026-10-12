from pathlib import Path
from PIL import Image
import numpy as np,json
import repair
R=repair.R
left=np.array(Image.open(R/'east-stone-left-v01/premixed.png'));right=np.array(Image.open(R/'east-stone-v01/premixed.png'))
a,b=left[:,660:],right[:,:594];cost=np.mean((a.astype(float)-b.astype(float))**2,axis=2);cost[:,:190]=np.inf;cost[:,405:]=np.inf
h,w=cost.shape;prev=cost[0].copy();back=np.zeros((h,w),np.int8)
for i in range(1,h):
 alt=np.stack((np.r_[np.inf,prev[:-1]],prev,np.r_[prev[1:],np.inf]));ch=alt.argmin(0);back[i]=ch-1;prev=cost[i]+np.take_along_axis(alt,ch[None],0)[0]
p=np.empty(h,np.int32);p[-1]=prev.argmin()
for i in range(h-1,0,-1):p[i-1]=p[i]+back[i,p[i]]
dist=np.arange(w)[None,:]-p[:,None];alpha=((np.clip(dist+2,0,4)*255+2)//4).astype(np.uint8);weights=alpha.astype(np.uint32)[...,None]
mixed=((a.astype(np.uint32)*(255-weights)+b.astype(np.uint32)*weights+127)//255).astype(np.uint8)
pixels=np.concatenate((left[:,:660],mixed,right[:,594:]),axis=1)
box=[22520,40370,24434,41624];im,sources=repair.cropworld(box);old=np.array(im);mask=np.uint8(np.any(pixels!=old,axis=2))*255
out=R/'east-combined';out.mkdir(exist_ok=True);Image.fromarray(pixels).save(out/'premixed.png',optimize=True);Image.fromarray(mask).save(out/'copy-mask.png');im.save(out/'input.png')
rec={'status':'combined_proposal_pending_parent_merge','worldBox':box,'premixed':str(out/'premixed.png'),'premixedSha256':repair.sha(out/'premixed.png'),'copyMask':str(out/'copy-mask.png'),'copyMaskSha256':repair.sha(out/'copy-mask.png'),'input':str(out/'input.png'),'inputSha256':repair.sha(out/'input.png'),'nativeContributions':[str(R/n/'proposal.json')for n in ['east-stone-left-v01','east-stone-v01']],'contributionSha256':[repair.sha(R/n/'proposal.json')for n in ['east-stone-left-v01','east-stone-v01']],'sourceCrops':sources,'sourceResampling':False,'maximumFeatherRadiusPixels':2,'overlapPixels':594,'overlapPath':p.tolist(),'copyRule':'Copy already premixed RGB once wherever copy-mask is nonzero. Validate original pixels under mask against input.png before applying. Do not apply individual east proposals again.','formalAccepted':False}
repair.write(out/'proposal.json',rec)
Image.fromarray(pixels[390:1010]).save(out/'review-band.png')
print(json.dumps({'proposal':str(out/'proposal.json'),'premixedSha256':rec['premixedSha256'],'maskSha256':rec['copyMaskSha256']}))

