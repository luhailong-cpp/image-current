from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
P=B/'r12_c05/repairs-resume-20261012/upper-cream-step-local-v02/proposal-v03.json'
d=json.loads(P.read_text(encoding='utf-8-sig'));A=B/'r12_c05/repairs-resume-20261012/integrated-local-v10/assembly.json';a=json.loads(A.read_text(encoding='utf-8-sig'))
for e in [d[k] for k in ['input','native','request','receipt','sourceContext','copyMask','alpha','appliedCrop']]+[a['contextOutput'],a['output']]:
    assert sha(e['file'])==e['sha256'],e['file']
old=np.array(Image.open(d['sourceContext']['file']).convert('RGB'));new=np.array(Image.open(a['contextOutput']['file']).convert('RGB'));core=np.array(Image.open(a['output']['file']).convert('RGB'))
mask=np.array(Image.open(d['copyMask']['file']).convert('L'))>0
alpha=np.array(Image.open(d['alpha']['file']).convert('L')); assert not np.any((alpha>0)&~mask)
box=d['cropContextBox'];x,y,x2,y2=box
global_mask=np.zeros(old.shape[:2],bool);global_mask[y:y2,x:x2]=mask
changed=np.any(old!=new,axis=2);outside=int(np.sum(changed&~global_mask));assert outside==0
assert np.array_equal(core,new[115:4211,115:4211])
native=Image.open(d['native']['file']).convert('RGB');src=Image.fromarray(old).crop(box);merged=Image.composite(native,src,Image.fromarray(alpha)); assert np.array_equal(np.array(merged),new[y:y2,x:x2])
record={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'assembly':str(A),'assemblySha256':sha(A),'proposal':str(P),'proposalSha256':sha(P),'hashChecksPassed':True,'outsideMaskChangedPixels':outside,'coreEqualsContextCrop':True,'copyMatchesNativeComposite':True,'sourceResampling':False,'maximumFeatherPixels':2,'visualReview':'Root viewed applied ROI and H2-4 native crop. Upper thin gray/cream line materially improved; small left-cap kink remains. Lower blue/cream gap still open.','formalAccepted':False,'internalPassed':False,'adoptedAsProvisional':True}
out=B/'r12_c05/repairs-resume-20261012/integrated-local-v10/root-review.json';assert not out.exists();atomic_json(out,record)
C=B/'current-candidates.json';cat=json.loads(C.read_text(encoding='utf-8-sig'));old_entry=cat['tiles']['r12_c05'];cat['tiles']['r12_c05']={'tile':'r12_c05','source':'root-reviewed-local-repair-v10-provisional','assembly':str(A),'candidate':a['output'],'context':a['contextOutput'],'formalAccepted':False,'internalPassed':False,'review':str(out),'previousAssembly':old_entry['assembly']};cat['updatedAtUtc']=record['recordedAtUtc'];atomic_json(C,cat);print(json.dumps(record,ensure_ascii=False))
