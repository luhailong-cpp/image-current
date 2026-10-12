from pathlib import Path
import json,hashlib,runpy
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;T=D.parent;R=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGB'))
def saveim(p,a):Image.fromarray(a).save(p,optimize=True);return {'file':str(p),'sha256':sha(p),'width':a.shape[1],'height':a.shape[0],'resampled':False}
candidate_path=D/'output/v2/r11-p01.north-and-bottom-fixed-context.png';original_path=T/'borders/r11-p01.original.context.png'
candidate=arr(candidate_path);original=arr(original_path)
box=[1100,545,4326,581];x0,y0,x1,y1=box;old=candidate[y0:y1,x0:x1];new=original[y0:y1,x0:x1];h,w=old.shape[:2];halo=8;radius=2
api=runpy.run_path(str(R/'local_repairs.py'),run_name='readonly_original_groove_restore')
for name in ['minimum_error_path','inclusion_mask']:api[name].__globals__['HALO']=halo
strips={'left':(old[:,:halo],new[:,:halo]),'right':(old[:,-halo:][:,::-1],new[:,-halo:][:,::-1]),'top':(old[:halo].transpose(1,0,2),new[:halo].transpose(1,0,2)),'bottom':(old[-halo:][::-1].transpose(1,0,2),new[-halo:][::-1].transpose(1,0,2))}
masks={};seams={}
for side,(a,b) in strips.items():
 seam=api['minimum_error_path'](a,b,radius);masks[side]=api['inclusion_mask'](seam,radius);seams[side]=seam.tolist()
alpha=np.full((h,w),255,dtype=np.uint8)
alpha[:,:halo]=np.minimum(alpha[:,:halo],masks['left']);alpha[:,-halo:]=np.minimum(alpha[:,-halo:],masks['right'][:,::-1]);alpha[:halo]=np.minimum(alpha[:halo],masks['top'].T);alpha[-halo:]=np.minimum(alpha[-halo:],masks['bottom'].T[::-1])
assert not any(a.any() for a in [alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
weight=alpha.astype(np.uint32)[...,None];local=((old.astype(np.uint32)*(255-weight)+new.astype(np.uint32)*weight+127)//255).astype(np.uint8)
out=candidate.copy();out[y0:y1,x0:x1]=local
check=out.copy();check[y0:y1,x0:x1]=candidate[y0:y1,x0:x1];assert np.array_equal(check,candidate)
assert np.array_equal(out[:116],candidate[:116]) and np.array_equal(out[1024:],original[1024:])
O=D/'output/v4';Q=D/'qa/v4';O.mkdir(parents=True,exist_ok=True);Q.mkdir(parents=True,exist_ok=True)
outputs={'context':saveim(O/'r11-p01.repaired.context.png',out),'core':saveim(O/'r11-p01.repaired.core.png',out[115:1139,115:4211])}
for label,a in [('before',candidate),('after',out)]:
 saveim(Q/f'groove-{label}.png',a[490:640,1100:4211])
 saveim(Q/f'groove-near-old-join-{label}.png',a[400:720,2850:3400])
 saveim(Q/f'groove-left-end-{label}.png',a[480:650,960:1280])
saveim(Q/'first-row-full.png',out[115:1139,115:4211])
report={'status':'pending_visual_qa','formalAccepted':False,'operation':'mechanical quilting of previously aligned original native stair groove into material-refined candidate','script':str(Path(__file__)),'scriptSha256':sha(Path(__file__)),'input':{'file':str(candidate_path),'sha256':sha(candidate_path)},'originalPixelSource':{'file':str(original_path),'sha256':sha(original_path)},'replacementContextBox':box,'unchangedOutsideBox':True,'nativeOriginalCoreBox':[1108,553,4318,573],'closedSeam':{'sourceAlgorithm':str(R/'local_repairs.py'),'sourceAlgorithmSha256':sha(R/'local_repairs.py'),'haloOverride':halo,'featherRadius':radius,'seams':seams,'alphaSha256':hashlib.sha256(alpha.tobytes()).hexdigest()},'newArtworkGenerated':False,'colorAdjustment':False,'resizing':False,'warping':False,'bottom230OriginalExact':True,'north116Unchanged':True,'outputs':outputs}
(O/'groove-preservation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(outputs,indent=2))
