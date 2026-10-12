from pathlib import Path
import sys
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
import assemble_native as A
def ref(f):return {'file':str(f),'sha256':p.sha(f)}
C=T/'candidate/r07_c05-candidate-native-rois-e1016a4a06b9410e/candidate.png';D=T/'qa/final-roi-native-20261012';D.mkdir(exist_ok=True);assert not (D/'index.json').exists();im=Image.open(C).convert('RGB');entries=[]
boxes={'first-curb-region':[0,2912,850,3822],'bridge-top':[397,2365,1651,2845],'bridge-bottom':[397,3299,1651,3779],'bridge-left':[317,2445,797,3699],'bridge-right':[1251,2445,1731,3699],'shared-east-own':[3909,2104,4096,2464]}
for name,box in boxes.items():
 v=im.crop(box);rot=name in ('bridge-left','bridge-right')
 if rot:v=v.transpose(Image.Transpose.ROTATE_90)
 q=A.save_png(v,D/(name+'.png'));q.update(name=name,cropLTRB=box,rotationCCW90=rot,nativePixelScale=1,actuallyViewed=False);entries.append(q)
N=Z/'joint-2x2-r05_c04-r06_c05/deeb69ed9f705a70/tiles/r06_c05-joint-4096.png';W=Z/'r07_c04/candidate/r07_c04-candidate-native-bridges-2268d482e68c2928/candidate.png';n=Image.open(N).convert('RGB');w=Image.open(W).convert('RGB');external=[]
prior_path=T/'qa/external-north-west-1672ae5e4698/review.json';prior=p.read(prior_path);old={e['name']:e for e in prior['entries']}
for side,other in [('north',n),('west',w)]:
 band=Image.new('RGB',(4096,640) if side=='north' else (640,4096))
 if side=='north':band.paste(other.crop((0,3776,4096,4096)),(0,0));band.paste(im.crop((0,0,4096,320)),(0,320))
 else:band.paste(other.crop((3776,0,4096,4096)),(0,0));band.paste(im.crop((0,0,320,4096)),(320,0))
 for kind,i in [('segment',j) for j in range(4)]+[('junction',j) for j in range(1,4)]:
  if kind=='segment':
   v=band.crop((i*1024,0,(i+1)*1024,640)) if side=='north' else band.crop((0,i*1024,640,(i+1)*1024)).transpose(Image.Transpose.ROTATE_90);name=f'{side}-segment{i+1:02}'
  else:v=band.crop((i*1024-160,160,i*1024+160,480)) if side=='north' else band.crop((160,i*1024-160,480,i*1024+160));name=f'{side}-junction-{i*1024}'
  q=A.save_png(v,D/'external'/(name+'.png'));q.update(name=name,side=side,nativePixelScale=1,actuallyViewed=False)
  e=old[name];same=np.array_equal(np.array(v),np.array(Image.open(e['file']).convert('RGB')))
  q['unchangedPixelsFromPrior']=same
  if same and e.get('verdict')=='passed':q.update(inheritedReview=ref(prior_path),inheritedCrop={'file':e['file'],'sha256':e['sha256']},verdict='passed_by_identical_previously_reviewed_pixels')
  else:q['verdict']='pending'
  external.append(q)
E=Z/'r07_c06/candidate/r07_c06-candidate-native-roi-v05.png';eim=Image.open(E).convert('RGB');v=Image.new('RGB',(356,260));v.paste(im.crop((3940,2154,4096,2414)),(0,0));v.paste(eim.crop((0,2154,200,2414)),(156,0));q=A.save_png(v,D/'shared-east-joint.png');q.update(name='shared-east-joint',nativePixelScale=1,actuallyViewed=False,neighbor=ref(E));entries.append(q)
p.write_json(D/'index.json',{'candidate':ref(C),'north':ref(N),'west':ref(W),'entries':entries,'externalNorthWest':external,'allExternalNeighborsComplete':False,'formalAccepted':False},replace=False);print({'newRegions':len(entries),'externalInherited':sum(e['verdict']!='pending' for e in external),'externalPending':[e['name'] for e in external if e['verdict']=='pending']})
