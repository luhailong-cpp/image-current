from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
B=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(B));from checkpoint_resume import atomic_json
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
checked=[]
for v in [11,13,14]:
    A=B/f'r12_c05/repairs-resume-20261012/integrated-local-v{v}/assembly.json';a=read(A)
    P=Path(a['appliedProposals'][0]);d=read(P)
    for e in [d[k] for k in ['input','native','request','receipt','sourceContext','copyMask','alpha','appliedCrop']]+[a['contextOutput'],a['output']]:assert sha(e['file'])==e['sha256'],e['file']
    old=np.array(Image.open(d['sourceContext']['file']).convert('RGB'));new=np.array(Image.open(a['contextOutput']['file']).convert('RGB'));core=np.array(Image.open(a['output']['file']).convert('RGB'))
    mask=np.array(Image.open(d['copyMask']['file']).convert('L'))>0
    alpha=np.array(Image.open(d['alpha']['file']).convert('L'));assert not np.any((alpha>0)&~mask)
    x,y,x2,y2=d['cropContextBox'];assert (x2-x,y2-y)==(1254,1254)
    global_mask=np.zeros(old.shape[:2],bool);global_mask[y:y2,x:x2]=mask
    changed=np.any(old!=new,axis=2);outside=int(np.sum(changed&~global_mask));assert outside==0
    assert np.array_equal(core,new[115:4211,115:4211])
    native=Image.open(d['native']['file']).convert('RGB');assert native.size==(1254,1254)
    merged=Image.composite(native,Image.fromarray(old).crop(d['cropContextBox']),Image.fromarray(alpha));assert np.array_equal(np.array(merged),new[y:y2,x:x2])
    checked.append({'version':v,'assembly':str(A),'assemblySha256':sha(A),'proposal':str(P),'proposalSha256':sha(P),'outsideMaskChangedPixels':outside,'copyMatchesNativeComposite':True,'coreEqualsContextCrop':True,'changedPixels':int(changed.sum())})
record={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'checks':checked,'sourceResampling':False,'maximumFeatherPixels':2,'visualReview':'Root viewed v11 H3-3 cream/blue edge, v13 east cap ROI and H3-4, v14 quiet ROI and V1-1. Small edge gap improved, gold/teal/red cap interior improved with floor unchanged; local diffuse stone improved but adjoining torn-cloud tones and blue face differences remain open.','formalAccepted':False,'internalPassed':False,'adoptedAsProvisional':True}
out=A.parent/'root-review.json';assert not out.exists();atomic_json(out,record)
C=B/'current-candidates.json';cat=read(C);old_entry=cat['tiles']['r12_c05'];cat['tiles']['r12_c05']={'tile':'r12_c05','source':'root-reviewed-local-repair-v14-provisional','assembly':str(A),'candidate':a['output'],'context':a['contextOutput'],'formalAccepted':False,'internalPassed':False,'review':str(out),'previousAssembly':old_entry['assembly']};cat['updatedAtUtc']=record['recordedAtUtc'];atomic_json(C,cat)
# Exact current neighbor strips for the next tile. These are guidance only until copied from a native tool return.
O=B/'r12_c06/pipeline/anchors';O.mkdir(parents=True,exist_ok=True)
for name,source,box in [
('left-r12c05-v14',a['contextOutput']['file'],[4096,0,4326,4326]),
('top-r11c06-v5',str(B/'integrated-20261011/v5/r11_c06.candidate.context.png'),[0,4096,4326,4326])]:
    dest=O/(name+'.png');assert not dest.exists()
    Image.open(source).convert('RGB').crop(box).save(dest)
    atomic_json(str(dest)+'.derivation.json',{'source':source,'sourceSha256':sha(source),'sourceCropBox':box,'output':str(dest),'sha256':sha(dest),'operation':'exact native crop; no resampling','sourceResampling':False,'forTile':'r12_c06'})
print(json.dumps(record))

