from workflow import ROOT,read,write,sha,now,patch
from pathlib import Path
from PIL import Image
import sys
tid,mode=sys.argv[1:3]
assert tid in ['r13_c13','r14_c13','r13_c14','r12_c14']
pf=ROOT/f'progress-{tid}.json'
if pf.exists():d=read(pf)
else:d={'currentTile':tid,'selectedVersions':{},'formalAcceptedCount':0,'internalPassed4kCount':0,'externalPassed4kCount':0}
d.update({'owner':'right_resume','generationModelRequirement':{'freeIncluded25Preferred':True,'builtin20FallbackAllowed':True,'newGenerationAllowed':True,'actualModel':None,'paidApiAuthorized':False,'authority':'D:/work/image/AGENTS.md'},'generationStopped':False,'newGenerationStatus':'active_builtin_native_continuation','productionFrozen':False})
if mode=='select':
 rc,ver,note=sys.argv[3:6];np=ROOT/'native'/f'{tid}_p{rc}_{ver}.png';recp=Path(str(np)+'.generation.json');rec=read(recp)
 assert [rec['width'],rec['height']]==[1254,1254]
 d['selectedVersions'][rc]=ver
 rec.update({'status':'selected_local_visual_seams_passed','visualReviewNote':note,'reviewedAtUtc':now()});write(recp,rec)
elif mode=='pending':
 rc,ver,note=sys.argv[3:6];d.setdefault('deferredIssues',{})[rc]={'version':ver,'note':note,'status':'not_passed','atUtc':now()};d['selectedVersions'].pop(rc,None)
elif mode!='sync':raise ValueError(mode)
d.update({'usableNativeCount':len(d['selectedVersions']),'generatedNativeCount':len(list((ROOT/'native').glob(tid+'_p*.png'))),'missingPatchCoordinates':[f'{r}{c}' for r in range(1,5) for c in range(1,5) if f'{r}{c}' not in d['selectedVersions']],'updatedAt':now(),'status':'continuing','inFlightRequestCount':0,'unsavedSuccessfulOutputCount':0,'nextStep':'Continue assigned native patches from accepted adjacent source pixels; concentrated actual seam QA on full tile.'})
write(pf,d)
print({'tile':tid,'selected':d['selectedVersions'],'missing':d['missingPatchCoordinates']})
