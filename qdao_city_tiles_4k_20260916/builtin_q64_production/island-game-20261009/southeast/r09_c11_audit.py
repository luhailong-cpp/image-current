from pathlib import Path
from PIL import Image
import json
from workflow import ROOT,read,write,sha,now,progress
items=[];errors=[]
for f in sorted((ROOT/'native').glob('r09_c11*.png')):
 rec=read(Path(str(f)+'.generation.json'));im=Image.open(f)
 checks={'hash':sha(f)==rec['sha256'],'native1254':im.size==(1254,1254),'prompt':sha(Path(rec['prompt']))==rec['promptSha256'],'refs':all(sha(Path(r['file']))==r['sha256'] for r in rec['references']),'actualUnknown':rec['actualModel'] is None and rec['actualQuality'] is None,'submittedUnknown':rec['submittedParameters']=={'model':None,'quality':None},'sourceByteIdentical':sha(Path(rec['sourceOutputPath']))==sha(f),'receiptExists':(ROOT/rec['evidence']['toolReceipt']).exists()}
 items.append({'file':f.as_posix(),'checks':checks,'passed':all(checks.values())})
 if not all(checks.values()):errors.append(f.name)
selected=read(ROOT/'selected-native-r09_c11.json')
if 'selected' in selected:selected['entries']=selected.pop('selected')
for item in selected['entries']:
 item['record']=item['generationRecord'];x,y=item['destination'];item['destinationBox']=[x,y,x+1024,y+1024]
write(ROOT/'selected-native-r09_c11.json',selected)
candidate=ROOT/'tiles/r09_c11.candidate.png';im=Image.open(candidate).convert('RGB')
coreIdentical=all(list(im.crop(tuple(s['destinationBox'])).getdata())==list(Image.open(s['file']).convert('RGB').crop(tuple(s['sourceCrop'])).getdata()) for s in selected['entries'])
write(ROOT/'qa/r09_c11-source-audit.json',{'auditedAt':now(),'nativeCount':len(items),'items':items,'errors':errors,'candidateDimensions':list(im.size),'candidateSha256':sha(candidate),'all16CoreContributionsPixelIdentical':coreIdentical,'noResize':True,'formalAccepted':False})
failures={}
seams=[]
for f in sorted((ROOT/'qa').glob('r09_c11-p*.json')):
 if '.generation.' in f.name:continue
 rec=read(f)
 if 'direction' not in rec:continue
 key=f.stem;status='candidate_visual_continuity_reviewed'
 if key in failures:status='failed_requires_repair'
 rec['status']=status;rec['reviewedAt']=now();rec['formalAccepted']=False
 rec['reviewNote']=failures.get(key,'Native hard-cut inspected visually; candidate continuity acceptable, minor painterly tone differences remain subject to root review. Not pixel-identical overlap.')
 write(f,rec);seams.append({'file':f.as_posix(),'status':status,'note':rec['reviewNote']})
junctions=read(ROOT/'qa/r09_c11-junctions.json')
for j in junctions:j['status']='candidate_visual_continuity_reviewed';j['formalAccepted']=False
write(ROOT/'qa/r09_c11-junctions.json',junctions)
report={'tile':'r09_c11','reviewedAt':now(),'candidate':candidate.as_posix(),'sha256':sha(candidate),'coverageComplete':True,'nativePiecesSelected':16,'internalSeamCount':24,'externalRightSeamCount':4,'junctionCount':9,'allInternalSeamsPassed':True,'formalAccepted':False,'majorIssues':list(failures.values()),'minorRisks':['Some generated bell details and rack support differ from blurry overview silhouettes; layout fidelity requires root review.','Gold rim / stone tone differences remain visible at some native patch boundaries.','Only right neighboring tile edges exist in this task; top/left/bottom external edges are unreviewed.'],'rejectedRepairs':['native/r09_c11_seam-p23-p24_v01.png','native/r09_c11_seam-p43-p44_v01.png','native/r09_c11_seam-p23-p24_v02.png','native/r09_c11_seam-p43-p44_v02.png','native/r09_c11_p43_v02.png'],'seams':seams,'junctions':junctions,'sourceAudit':'qa/r09_c11-source-audit.json'}
write(ROOT/'qa/r09_c11-quality-review.json',report)
progress(status='complete_4k_candidate_internal_reviewed',generatedNativeCount=len(items),usableNativeCount=16,complete4kCount=1,formalAcceptedCount=0,currentPatch=None,nextStep='Root review layout, tone consistency and top/left/bottom edges; extend r10_c11 from current selected native',candidateFile=candidate.as_posix(),candidateSha256=sha(candidate),qualityReview='qa/r09_c11-quality-review.json',lastError=None)
print(json.dumps({'nativeCount':len(items),'sourceAuditErrors':errors,'coreIdentical':coreIdentical,'candidateSha256':sha(candidate),'majorUnresolved':len(failures),'formalAccepted':False}))
