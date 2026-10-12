from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys,importlib.util
from datetime import datetime,timezone
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;S=R.parent/'crossedge-stair-restored-20261011';SW=R.parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
rec=read(S/'stair-combined/proposal.json')
assert sha(rec['premixed'])==rec['premixedSha256']
g=read(S/'stair-upper-v01/generation.json');assert sha(g['file'])==g['sha256']
# Exact crop, all coordinates half-open. Current proposal premixed is expected input after parent applies it.
box=[20173,40467,20833,40547];sc=[v-o for v,o in zip(box,[19853,39320,19853,39320])]
old=np.array(Image.open(rec['premixed']).convert('RGB').crop(sc))
native=np.array(Image.open(g['file']).convert('RGB').crop(sc))
spec=importlib.util.spec_from_file_location('q',SW/'local_repairs.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
alpha=np.zeros(old.shape[:2],np.uint8)
l,rr,t,bb=90,595,30,55
alpha[t:bb,l:rr]=255;paths={}
for side,x,rev in [('left',l,False),('right',rr-115,True)]:
 a=old[t:bb,x:x+115];b=native[t:bb,x:x+115]
 if rev:a=a[:,::-1];b=b[:,::-1]
 p=q.minimum_error_path(a,b,2);m=q.inclusion_mask(p,2)
 if rev:m=m[:,::-1]
 alpha[t:bb,x:x+115]=np.minimum(alpha[t:bb,x:x+115],m);paths[side]=p.tolist()
alpha[t]=np.minimum(alpha[t],85);alpha[t+1]=np.minimum(alpha[t+1],170)
alpha[bb-2]=np.minimum(alpha[bb-2],170);alpha[bb-1]=np.minimum(alpha[bb-1],85)
w=alpha.astype(np.uint32)[...,None];out=((old.astype(np.uint32)*(255-w)+native.astype(np.uint32)*w+127)//255).astype(np.uint8)
mask=alpha>0
assert np.array_equal(old[~mask],out[~mask])
for n,z in [('input',old),('native-source-crop',native),('premixed',out),('alpha',alpha),('copy-mask',np.uint8(mask)*255)]:Image.fromarray(z).save(R/(n+'.png'))
ys,xs=np.nonzero(mask);affected=[box[0]+int(xs.min()),box[1]+int(ys.min()),box[0]+int(xs.max())+1,box[1]+int(ys.max())+1]
# Report the same centered gradient peak, plus narrower independent x probes. This is a local diagnostic, not sole visual approval.
probes=[]
orig=np.array(Image.open(S/'stair-combined/input.png').crop(sc)).astype(float)
for worldx in range(20353,20553,25):
 x=worldx-box[0]
 def peak(z):
  d=np.abs(np.diff(z[30:55,x:x+25].astype(float),axis=0)).mean(axis=(1,2))
  return int(np.argmax(d))+box[1]+30
 probes.append({'worldX':[worldx,worldx+25],'originalEdgeY':peak(orig),'supplementEdgeY':peak(out)})
pr={'name':'first-short-bevel-upper-native-local-reuse','status':'proposal_pending_parent_visual_review','worldBox':box,'affectedWorldBox':affected,'input':str(R/'input.png'),'inputSha256':sha(R/'input.png'),'premixed':str(R/'premixed.png'),'premixedSha256':sha(R/'premixed.png'),'copyMask':str(R/'copy-mask.png'),'copyMaskSha256':sha(R/'copy-mask.png'),'alpha':str(R/'alpha.png'),'alphaSha256':sha(R/'alpha.png'),'dependsOnProposal':str(S/'stair-combined/proposal.json'),'dependsOnProposalSha256':sha(S/'stair-combined/proposal.json'),'expectedParentPremixedSha256':rec['premixedSha256'],'source':{'generation':str(S/'stair-upper-v01/generation.json'),'generationSha256':sha(S/'stair-upper-v01/generation.json'),'native':g['file'],'nativeSha256':g['sha256'],'nativeCrop':sc,'exactTranslationPixels':[0,0],'reason':'The upper native aligns locally better than lower native; no 3-4px uniform translation is justified.'},'nativePixelSampling':'1:1 integer crop only','resampling':False,'maxFeatherRadiusPixels':2,'outerQuiltingPaths':paths,'copyRule':'Apply after the delivered stair-combined proposal. Validate local input under copy-mask; copy premixed once wherever copy-mask is nonzero, without reblending.','changedPixels':int(np.any(old!=out,axis=2).sum()),'outsideMaskUnchanged':True,'bevelDiagnostic':probes,'networkCalls':0,'imageGenerationCalls':0,'actualModel':None,'actualQuality':None,'formalAccepted':False,'atUtc':datetime.now(timezone.utc).isoformat()}
write(R/'proposal.json',pr)
print(json.dumps({k:v for k,v in pr.items()if k not in ['outerQuiltingPaths','bevelDiagnostic']},ensure_ascii=False))
