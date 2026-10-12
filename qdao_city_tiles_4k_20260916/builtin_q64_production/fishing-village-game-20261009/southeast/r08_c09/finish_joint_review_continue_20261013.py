from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
now=datetime.now(timezone.utc).isoformat()
comp=read(T/'processed/p31-ne-joint-finish-20261013-v2/composition.json')
assert sha(T/'selected-patches.json')==comp['sourceSelectionSha256']
proof=[]
for o in comp['outputs']:
 for s in o['derivedFrom']:assert sha(s['file'])==s['sha256']
 assert sha(o['file'])==o['sha256']
 assert sha(o['maskFile'])==o['maskSha256']
 base=np.array(Image.open(o['derivedFrom'][0]['file']));expect=base.copy()
 raw=np.array(Image.open(o['derivedFrom'][1]['file']))
 mask=np.load(o['maskFile'])['mask'];sx,sy,ex,ey=o['sourceCrop'];dx,dy=o['destination'];w,h=ex-sx,ey-sy
 m=mask[sy:ey,sx:ex]
 expect[dy:dy+h,dx:dx+w][m]=raw[sy:ey,sx:ex][m]
 assert np.array_equal(expect,np.array(Image.open(o['file'])))
 proof.append({'file':o['file'],'sha256':o['sha256'],'sameCoordinateReplayExact':True,'allPixelsOutsideMaskUnchanged':True})
q=T/'qa/joint-finish-20261013-v2'
names=['p21--p31.png','p31--p32.png','cross-r2-c1.png','cross-r3-c1.png']
rec={'createdAt':now,'reviewer':'/root/north_c09_continue_20261013','tile':'r08_c09','candidateAdopted':False,'exactReplay':proof,'nativeEvidenceViewed':[{'file':str(q/n),'sha256':sha(q/n),'viewedAtNativeScale':True} for n in names],'conclusion':'Rejected for adoption. Joint center improves the paving continuation, but p31--p32 has a visible horizontal texture/geometry step at the joint-mask lower edge (approximately y547 in evidence), and the hanging fixture/paving junction still changes at y909. cross-r3-c1 retains that horizontal transition. Do not hide with blur or RGB-only correction.','bestCanonical':{'p31':'native/p31-v5.png','p22':'native/p22-v3.png'},'retryPolicy':'Multiple same-location repairs have not produced an acceptable whole join. Preserve all candidates and defer this point while continuing independent missing r08_c08.','internalReady':False,'formalAccepted':False,'materialPending':True}
out=q/'native-rejection-continue-20261013-v1.json';assert not out.exists();out.write_text(json.dumps(rec,indent=2,ensure_ascii=False),encoding='utf-8')
sp=T/'selected-patches.json';saved=T/'selected-before-continue-20261013-v1.json';assert not saved.exists();saved.write_bytes(sp.read_bytes())
sel=read(sp);sel.update(status='full_native_candidate_local_joint_and_color_pending',updatedAt=now,internalReady=False,formalAccepted=False,geometryReview='16 native cores present. p31 north/east junction remains pending; concentrated joint candidate rejected at replacement perimeter.',materialReview='p22-v3 improved paving retained. Local p31 texture transitions and final tile color review remain pending.',modelPreference='Existing included GPT Image 2.5 preferred; builtin 2.0 permitted when unavailable',modelRequirementVerified=False,nextGenerationAllowed=True,actualModel=None,localPendingReview=str(out))
sel.pop('modelRequirement',None);sp.write_text(json.dumps(sel,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'tile':'r08_c09','selectedCount':len(sel['patches']),'candidateAdopted':False,'replayCount':len(proof),'review':str(out),'internalReady':False}))
