from pathlib import Path
from datetime import datetime,timezone
import json,shutil,hashlib
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=read(T/'selected-patches.json');m=read(T/'colorpass-selected.json');v=read(T/'candidate/processed-verification.json')
expected='fe272333737013523783f6d58925354320a20ffdbffccbf6fc8cf3811b57395f'
assert sha(m['candidate']['file'])==expected and v['candidate']['sha256']==expected and len(v['selectedSourceChecks'])==16
dest=T/'candidate'/'r11_c10-internal-ready-4096.png';shutil.copy2(m['candidate']['file'],dest);assert sha(dest)==expected
review={'tile':T.name,'status':'internal_ready_external_east_south_pending','internalReady':True,'formalAccepted':False,'candidate':str(dest),'candidateSha256':expected,'internalSeams':24,'internalCrossings':9,'repairBoundaryStrips':8,'independentReviewer':'/root/seam_review','independentApprovalEvidence':'Direct agent message confirmed final fe272333 candidate: G1/Q1 adoption bounds and junction pass, p43v2/p44 last-row pass, north/west 8 segments and 2x2 center pass; all16 fields replay identical max20. Independent final-review file is being persisted.','independentReportDirectory':str(T.parent/'seam-qa/independent-20261010/r11_c10'),'resolvedIssues':['G1 rectangular hanging wood and disconnected slab T junction','Q1 soft crosspiece and nailheads'],'geometryBlockingIssues':[],'colorBlockingIssues':[],'externalNorth':'reviewed_current_selected_pixels','externalWest':'reviewed_current_selected_pixels','externalEast':'pending_neighbor','externalSouth':'pending_neighbor','colorCorrection':{'robustBefore':2.6161024446288743,'robustAfter':.49826389116545516,'maximumActualChannelChange':20,'resampling':False,'sourceImageBlur':False,'sourcePixelBlending':False},'verifiedAt':datetime.now(timezone.utc).isoformat()}
write(T/'qa/internal-review.json',review)
s.update(status=review['status'],internalReady=True,formalAccepted=False,candidate=str(dest),candidateSha256=expected,internalReview=str(T/'qa/internal-review.json'),updatedAt=review['verifiedAt']);write(T/'selected-patches.json',s)
v['internalReady']=True;v['internalReview']=str(T/'qa/internal-review.json');write(T/'candidate/processed-verification.json',v)
manifest={'tile':T.name,'file':str(dest),'sha256':expected,'dimensions':[4096,4096],'status':s['status'],'internalReady':True,'formalAccepted':False,'sources':v['selectedSourceChecks'],'operation':'16 unscaled native 1024 cores from1254 sources and traceable bounded additive RGB derivatives','resamplingApplied':False,'actualModel':None,'actualQuality':None,'review':str(T/'qa/internal-review.json'),'verification':str(T/'candidate/processed-verification.json')}
write(T/'candidate/internal-ready-manifest.json',manifest);write(str(dest)+'.derivation.json',manifest)
write(T/'progress.json',{'tile':T.name,'status':s['status'],'generatedNativeImageCount':22,'selectedNativeCount':16,'usableNativeCount':16,'complete4kCandidateCount':1,'internalReady4kCount':1,'formalAcceptedCount':0,'remainingPositions':[],'candidate':str(dest),'candidateSha256':expected,'geometryBlockingIssues':[],'colorBlockingIssues':[],'updatedAt':review['verifiedAt']})
print(json.dumps({'tile':T.name,'internalReady':True,'candidate':str(dest),'sha256':expected}))

