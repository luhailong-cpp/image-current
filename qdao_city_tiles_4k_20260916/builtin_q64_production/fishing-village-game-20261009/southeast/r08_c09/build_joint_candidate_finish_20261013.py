from pathlib import Path
import json,hashlib,copy
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageFilter
T=Path(__file__).resolve().parent;now=datetime.now(timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 p=Path(p);assert not p.exists();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sel=read(T/'selected-patches.json');selectionsha=sha(T/'selected-patches.json')
plan=read(T/'coordinate-plan.json')
raw=T/'raw/p31-ne-joint-v1-builtin.png';im=np.array(Image.open(raw));assert im.shape==(1254,1254,3)
guide=T/'layout-only/p31-ne-joint-v1.png';old=np.array(Image.open(guide)).astype(float)
dest=T/'native/p31-ne-joint-v1.png';assert not dest.exists();dest.write_bytes(raw.read_bytes())
write(str(dest)+'.generation.json',{'file':str(dest),'sha256':sha(dest),'nativeDimensions':[1254,1254],'route':'builtin','tool':'image_gen__imagegen','actualModel':None,'actualQuality':None,'createdAt':now,'request':str(T/'p31-ne-joint-v1.request.json'),'receipt':str(T/'p31-ne-joint-v1.receipt.json'),'globalBox':[33165,30093,34419,31347],'resampling':False})
out=T/'processed/p31-ne-joint-finish-20261013-v1';assert not out.exists();out.mkdir(parents=True)
mask=np.zeros((1254,1254),np.uint8);mask[470:1174,80:1174]=255
gold=((old[:,:,0]>old[:,:,1]*1.15)&(old[:,:,0]>old[:,:,2]*1.3)&(old[:,:,0]>90)).astype(np.uint8)*255
protect=np.array(Image.fromarray(gold).filter(ImageFilter.MaxFilter(17)))>0
mask[protect]=0
Image.fromarray(mask).save(out/'native-copy-mask.png')
np.savez_compressed(out/'native-copy-mask.npz',mask=mask>0)
box=[33165,30093,34419,31347]
newsel=copy.deepcopy(sel);newsel['status']='native_joint_candidate_pending_boundary_QA';newsel['internalReady']=False;newsel['formalAccepted']=False
items=[]
for pid,rel in sel['patches'].items():
 coord=next(p for p in plan['patches'] if p['id']==pid);pb=coord['globalBox']
 ov=[max(pb[0],box[0]),max(pb[1],box[1]),min(pb[2],box[2]),min(pb[3],box[3])]
 if ov[0]>=ov[2] or ov[1]>=ov[3]:continue
 a=np.array(Image.open(T/rel));base=a.copy();sx,sy=ov[0]-box[0],ov[1]-box[1];dx,dy=ov[0]-pb[0],ov[1]-pb[1];w,h=ov[2]-ov[0],ov[3]-ov[1]
 m=mask[sy:sy+h,sx:sx+w]>0
 a[dy:dy+h,dx:dx+w][m]=im[sy:sy+h,sx:sx+w][m]
 changed=int(np.any(a!=base,axis=2).sum())
 if not changed:continue
 f=out/f'{pid}-joint.png';Image.fromarray(a).save(f);newsel['patches'][pid]=str(f.relative_to(T))
 rec={'file':str(f),'sha256':sha(f),'createdAt':now,'dimensions':[1254,1254],'operation':'exact binary masked native-pixel copy at identical global coordinates; no interpolation, warp, blur, or blending','derivedFrom':[{'file':str(T/rel),'sha256':sha(T/rel)},{'file':str(dest),'sha256':sha(dest)}],'maskFile':str(out/'native-copy-mask.npz'),'maskSha256':sha(out/'native-copy-mask.npz'),'jointGlobalBox':box,'nativeGlobalBox':pb,'globalOverlap':ov,'sourceCrop':[sx,sy,sx+w,sy+h],'destination':[dx,dy],'changedPixels':changed,'resampling':False,'imagePixelBlending':False,'actualModel':None,'formalAccepted':False}
 write(str(f)+'.derivation.json',rec);items.append(rec)
assert sha(T/'selected-patches.json')==selectionsha
newsel['jointEvidence']=str(out/'composition.json')
write(out/'composition.json',{'createdAt':now,'tile':'r08_c09','sourceSelectionSha256':selectionsha,'candidateOnly':True,'canonicalAdopted':False,'maskBoxInJoint':[80,470,1174,1174],'foregroundPreserved':'Warm gold/red pixels plus8px protective dilation of mask only; no art smoothing','outputs':items})
write(T/'joint-selected-finish-20261013-v1.json',newsel)
print(json.dumps({'modifiedPatches':[Path(x['file']).stem for x in items],'maskPixels':int((mask>0).sum()),'canonicalUnchanged':True}))

