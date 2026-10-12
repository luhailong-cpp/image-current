from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;wt=Path(sys.argv[1]);at=Path(sys.argv[2])
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'sha256':sha(p)}
def dump(p,d):
 assert not p.exists();p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
wc=read(wt/'step01-W02-last-v2/composition.json')
dump(wt/'step01-W02-last-v2/visual-qa.json',{'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'composition':info(wt/'step01-W02-last-v2/composition.json'),'native':wc['actualNative'],'evidenceReviewed':wc['evidence'],'status':'failed_second_targeted_attempt_stop_this_point','formalAccepted':False,'published':False,'findings':[{'childBox':[0,2290,80,2395],'description':'New upper grout starts at x~8,y2310 while immutable incoming reaches x0,y2360; still a blind gap, despite endpoint moving down versus v1.'},{'childBox':[20,2490,170,2580],'description':'Lower joint is shifted; retained edge and native blend produce a doubled/ghost bevel around leaf notch.'},{'childBox':[0,2120,40,2490],'description':'Strong fixed-edge slab texture/tone cut remains.'}],'leafProtectedPixels':'exact originals preserved mechanically; nearby border still failed','action':'Do not adopt either W02 output; keep published base pixels here. No third attempt in this round.'})
aidx=read(at/'trial-index.json');ac=read(at/'step01-W01-alpha-v2/composition.json')
# Compare selected composition's actual native join to the reviewed alpha-only trial.
assert sha(at/'step01-W01-alpha-v2/composed-core-join-1254.png')==sha(D/'W01-alpha-v2/composed-core-join-1254.png')
best=np.array(Image.open(aidx['finalTrial']['path']).convert('RGB'));base=np.array(Image.open(aidx['base']['path']).convert('RGB'))
Image.fromarray(best[768:1280,:614]).save(at/'W01-h1024-q0-after-100pct.png')
report={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'local_improvements_ready_for_root_review_external_west_failed','candidate':aidx['finalTrial'],'compositionIndex':info(at/'trial-index.json'),'W01':{'status':'local_geometry_and_alpha_boundary_pass','sourceNative':ac['actualNative'],'newAlpha':ac['savedAlpha'],'alphaSelection':info(D/'W01-alpha-v2/alpha-selection.json'),'description':'Reduced alpha excludes previous dark shoulder around child x295..335,y1125..1190, retaining original pixels there. Same actual native remains in removed-branch area. Full local join, top/right/bottom/fixed-west and before/after shoulder were reviewed at 1:1; no new grout hard break/ghosting observed.','evidenceReviewed':[info(x) for x in sorted((D/'W01-alpha-v2').glob('*.png')) if x.name not in ['alpha-native-1254.png','alpha-crop.png']]},'W02':{'status':'failed_stop_after_two_attempts','latestNative':wc['actualNative'],'latestQA':info(wt/'step01-W02-last-v2/visual-qa.json'),'adopted':False},'W03':{'status':'previous_local_pass_carried_forward','previousQA':info(D/'trial-20261013T090141-W01-W02-W03/step03-W03/visual-qa.json'),'allLocalPixelsUnchanged':bool(np.array_equal(best[3332:3762,:275],np.array(Image.open(D/'trial-20261013T094033-W01-W03/step02-W03/candidate-4096.png').convert('RGB'))[3332:3762,:275]))},'mechanicalChecks':ac['checks'],'remainingWest':'W02 geometry and W04 material unresolved, entire west failed','formalAccepted':False,'published':False,'RGBColorCorrection':False,'resampling':False,'newImageCallCountThisRound':1,'actualModel':None,'actualQuality':None,'localCompositionErrorResolved':'First alpha composition stopped on missing duplicate request.json; partial trial preserved. Existing original request byte-copied for compositor compatibility; complete new trial replay passed.'}
dump(D/'production-checkpoint-20261013-W02-last-W01-alpha-v2.json',report)
print(json.dumps({'candidate':aidx['finalTrial'],'checkpoint':info(D/'production-checkpoint-20261013-W02-last-W01-alpha-v2.json')}))

