from pathlib import Path
import numpy as np,json
from PIL import Image
import repair
R=repair.R
def feather_path(a,b):
 # Horizontal overlap, bounded path in y=80..150, radius2.
 cost=np.mean((a.astype(float)-b.astype(float))**2,axis=2).T
 cost[:,:80]=np.inf;cost[:,151:]=np.inf
 h,w=cost.shape;prev=cost[0].copy();back=np.zeros((h,w),np.int8)
 for i in range(1,h):
  alt=np.stack((np.r_[np.inf,prev[:-1]],prev,np.r_[prev[1:],np.inf]));ch=alt.argmin(0);back[i]=ch-1;prev=cost[i]+np.take_along_axis(alt,ch[None],0)[0]
 p=np.empty(h,np.int32);p[-1]=prev.argmin()
 for i in range(h-1,0,-1):p[i-1]=p[i]+back[i,p[i]]
 dist=np.arange(w)[None,:]-p[:,None];m=((np.clip(dist+2,0,4)*255+2)//4).astype(np.uint8).T
 weights=m.astype(np.uint32)[...,None];out=((a.astype(np.uint32)*(255-weights)+b.astype(np.uint32)*weights+127)//255).astype(np.uint8)
 return out,p
names=['wood-upper-v01','wood-middle-v01','wood-lower-v01']
parts=[np.array(Image.open(R/n/'premixed.png')) for n in names];allwood=parts[0].copy();paths=[]
for part in parts[1:]:
 overlap,path=feather_path(allwood[-230:],part[:230]);allwood=np.concatenate((allwood[:-230],overlap,part[230:]),axis=0);paths.append(path.tolist())
bbox=[19853,36864,21107,40166];base,sources=repair.cropworld(bbox);old=np.array(base)
mask=np.uint8(np.any(allwood!=old,axis=2))*255
out=R/'wood-combined';out.mkdir(exist_ok=True);Image.fromarray(allwood).save(out/'premixed.png',optimize=True);Image.fromarray(mask).save(out/'copy-mask.png');base.save(out/'input.png')
rec={'status':'combined_proposal_pending_parent_merge','worldBox':bbox,'premixed':str(out/'premixed.png'),'premixedSha256':repair.sha(out/'premixed.png'),'copyMask':str(out/'copy-mask.png'),'copyMaskSha256':repair.sha(out/'copy-mask.png'),'input':str(out/'input.png'),'inputSha256':repair.sha(out/'input.png'),'nativeContributions':[str(R/n/'proposal.json')for n in names],'contributionSha256':[repair.sha(R/n/'proposal.json')for n in names],'sourceCrops':sources,'sourceResampling':False,'maximumFeatherRadiusPixels':2,'overlapPixels':230,'overlapPaths':paths,'copyRule':'Copy already premixed RGB once wherever copy-mask is nonzero. Validate original pixels under mask against input.png before applying. Do not apply individual wood proposals again.','formalAccepted':False}
repair.write(out/'proposal.json',rec)
for i in range(4):
 y0=i*900;y1=min(len(allwood),y0+900)
 if y0<y1:Image.fromarray(allwood[y0:y1,365:985]).save(out/('review-segment'+str(i+1)+'.png'))
# Simulated east-border replacement in wider area; output is QA only.
box=[22900,40760,24550,41380];image,src=repair.cropworld(box);pixels=np.array(image)
p=repair.read(R/'east-stone-v01/proposal.json');w=p['worldBox'];l,t,rr,bb=max(box[0],w[0]),max(box[1],w[1]),min(box[2],w[2]),min(box[3],w[3])
new=np.array(Image.open(p['premixed']))[t-w[1]:bb-w[1],l-w[0]:rr-w[0]];m=np.array(Image.open(p['copyMask']))[t-w[1]:bb-w[1],l-w[0]:rr-w[0]]>0
part=pixels[t-box[1]:bb-box[1],l-box[0]:rr-box[0]];part[m]=new[m]
Image.fromarray(pixels).save(R/'east-stone-v01/wider-qa.png')
print(json.dumps({'woodCombinedProposal':str(out/'proposal.json'),'eastWiderQa':str(R/'east-stone-v01/wider-qa.png')}))

